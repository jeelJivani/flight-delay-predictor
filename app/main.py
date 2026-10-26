import json
from pathlib import Path
import pandas as pd
from typing import Literal
from pydantic import BaseModel, Field
import joblib
from fastapi import FastAPI

class FlightIn(BaseModel):
    flight_hour: int = Field(ge=0, le=23)
    weather: Literal["Clear", "Rain", "Snow", "Storm"]
    airline: Literal["EasyJet", "Lufthansa", "Ryanair"]

ROOT = Path(__file__).resolve().parent.parent
MODEL = joblib.load(ROOT / "models" / "model.joblib")
COLUMNS = json.loads((ROOT / "models" / "columns.json").read_text())

app = FastAPI(title="MUC Flight Delay Predictor")


@app.get("/health")
def health():
    return {"status": "ok", "features": len(COLUMNS)}

@app.post("/predict")
def predict(flight: FlightIn):
    # 1. Start with all 8 columns set to 0
    row = {col: 0 for col in COLUMNS}

    # 2. Fill in the hour
    row["flight_hour"] = flight.flight_hour

    # 3. Switch on the right weather and airline (set to 1)
    row[f"weather_{flight.weather}"] = 1
    row[f"airline_{flight.airline}"] = 1

    # 4. Make a one-row table in the right column order
    df = pd.DataFrame([row], columns=COLUMNS)

    # 5. Ask the model
    pred = MODEL.predict(df)[0]
    prob = MODEL.predict_proba(df)[0][1]

    # 6. Send the answer back
    return {
        "delayed": bool(pred),
        "probability": round(float(prob), 2),
    }