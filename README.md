# Flight Delay Predictor

A learning project that builds toward predicting flight delays at Munich Airport (MUC).

## What it does so far

All work lives in [`01_data_exploration.ipynb`](01_data_exploration.ipynb):

1. **Prototype model:** generates 100 synthetic flights (hour, weather, airline), one-hot encodes them and trains a scikit-learn `RandomForestClassifier`. The labels are random, so this only tests the pipeline.
2. **Live arrivals:** pulls real-time aircraft positions over Munich from the [OpenSky Network API](https://openskynetwork.github.io/opensky-api/) and keeps airborne, descending aircraft.
3. **Distance and ETA:** computes each aircraft's distance to MUC with the Haversine formula and estimates minutes to landing from its current speed.
4. **Storage:** saves arrivals to a local SQLite database (`flight_data.db`) and queries flights landing within 15 minutes.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

Then open `01_data_exploration.ipynb` and run the cells in order. The live-data cells need an internet connection; `flight_data.db` is created automatically.

## How to run

The notebook's two parts are also available as scripts. Run them from the project root with the virtual environment active:

```bash
# Fetch live arrivals into Munich and save them to SQLite
python src/fetch.py

# Train the prototype delay model and save it
python src/train.py
```

| Script | What it does | Output |
|---|---|---|
| `src/fetch.py` | Pulls live aircraft over Munich from OpenSky, keeps descending flights, adds distance to MUC and ETA | `flight_data.db`, table `active_arrivals` (replaced on each run) |
| `src/train.py` | Trains a `RandomForestClassifier` on synthetic flights and prints test accuracy | `models/model.joblib` |

`fetch.py` needs an internet connection. OpenSky limits anonymous requests, so if it fails with HTTP 429, wait a few minutes and try again.

To check the results:

```bash
sqlite3 flight_data.db "SELECT callsign, distance_to_muc_km, eta_minutes FROM active_arrivals ORDER BY eta_minutes;"
python -c "import joblib; print(joblib.load('models/model.joblib'))"
```

## Roadmap

- Use real historical flight data with scheduled vs. actual times
- Add real weather data for Munich
- Train and evaluate a delay model on that data
