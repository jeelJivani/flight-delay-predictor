"""Fetch live arrivals into Munich (MUC) from OpenSky and save them to SQLite.

Usage: python src/fetch.py
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import requests

# flight_data.db lives in the project root, wherever the script is run from
DB_PATH = Path(__file__).resolve().parent.parent / "flight_data.db"

OPENSKY_URL = "https://opensky-network.org/api/states/all"

# Geographic bounding box for Munich airspace
MUNICH_AIRSPACE = {
    "lamin": 48.0,  # Latitude minimum
    "lamax": 48.5,  # Latitude maximum
    "lomin": 11.4,  # Longitude minimum
    "lomax": 12.0,  # Longitude maximum
}

# Munich Airport (MUC / EDDM) GPS coordinates
MUC_LAT = 48.3538
MUC_LON = 11.7861

COLUMNS = [
    "icao24", "callsign", "origin_country", "time_position",
    "last_contact", "longitude", "latitude", "baro_altitude",
    "on_ground", "velocity", "true_track", "vertical_rate",
    "sensors", "geo_altitude", "squawk", "spi", "position_source",
]


def fetch_flights():
    """Return a DataFrame of all aircraft currently in the Munich sector."""
    response = requests.get(OPENSKY_URL, params=MUNICH_AIRSPACE, timeout=30)
    response.raise_for_status()

    # OpenSky returns "states": null when the sector is empty
    flight_vectors = response.json().get("states") or []
    return pd.DataFrame(flight_vectors, columns=COLUMNS)


def filter_arrivals(flights):
    """Keep airborne, descending aircraft that have a callsign."""
    is_flying = flights["on_ground"] == False  # noqa: E712
    is_descending = flights["vertical_rate"] < 0
    return flights[is_flying & is_descending].dropna(subset=["callsign"]).copy()


def haversine_distance(lat1, lon1, lat2, lon2):
    """Great-circle distance in kilometers."""
    R = 6371.0  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c


def add_distance_and_eta(arrivals):
    """Add distance to MUC (km) and a straight-line ETA (minutes)."""
    arrivals["distance_to_muc_km"] = haversine_distance(
        arrivals["latitude"], arrivals["longitude"], MUC_LAT, MUC_LON
    )

    # Time = Distance / Speed, with velocity converted from m/s to km/s
    speed_km_s = arrivals["velocity"] / 1000
    time_to_landing_seconds = arrivals["distance_to_muc_km"] / speed_km_s
    arrivals["eta_minutes"] = (time_to_landing_seconds / 60).round(1)

    return arrivals.sort_values(by="distance_to_muc_km")


def save_arrivals(arrivals, db_path=DB_PATH):
    """Replace the active_arrivals table with the latest snapshot."""
    with sqlite3.connect(db_path) as conn:
        arrivals.to_sql("active_arrivals", conn, if_exists="replace", index=False)


def main():
    print("Pinging OpenSky API for live Munich traffic...")
    flights = fetch_flights()
    print(f"Tracking {len(flights)} aircraft currently in the sector.")

    arrivals = add_distance_and_eta(filter_arrivals(flights))
    print(f"Found {len(arrivals)} aircraft currently on descent.")

    save_arrivals(arrivals)
    print(f"Saved {len(arrivals)} arrivals to {DB_PATH.name} (table: active_arrivals)")

    if not arrivals.empty:
        print(arrivals[["callsign", "origin_country", "distance_to_muc_km", "eta_minutes"]]
              .sort_values("eta_minutes")
              .to_string(index=False))


if __name__ == "__main__":
    main()
