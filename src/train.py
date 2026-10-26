"""Train the prototype flight delay model and save it with joblib.

The training data is synthetic (random labels), so this only exercises the
pipeline; the accuracy is not meaningful yet.

Usage: python src/train.py
"""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODELS_DIR / "model.joblib"
COLUMNS_PATH = MODELS_DIR / "columns.json"


def generate_data(n=100, seed=42):
    """Generate fake flights with realistic variables."""
    np.random.seed(seed)
    return pd.DataFrame({
        "flight_hour": np.random.randint(6, 24, n),  # Flights between 6 AM and Midnight
        "weather": np.random.choice(["Clear", "Rain", "Storm", "Snow"], n, p=[0.6, 0.2, 0.1, 0.1]),
        "airline": np.random.choice(["Lufthansa", "Ryanair", "EasyJet"], n),
        "is_delayed": np.random.choice([0, 1], n, p=[0.7, 0.3]),  # 0 = On Time, 1 = Delayed
    })


def main():
    df = generate_data()

    # Encode text columns into 0/1 columns
    df_encoded = pd.get_dummies(df, columns=["weather", "airline"], dtype=int)

    # Split 80% train / 20% test
    y = df_encoded["is_delayed"]
    X = df_encoded.drop("is_delayed", axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test))
    print(f"Model Accuracy: {accuracy * 100:.2f}%")

    # Save the model, plus the column order it was trained on so the API
    # can turn raw input ("Rain", "Ryanair") into the same one-hot columns
    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    COLUMNS_PATH.write_text(json.dumps(list(X.columns), indent=2))
    print(f"Model saved to models/{MODEL_PATH.name}")
    print(f"Columns saved to models/{COLUMNS_PATH.name}")


if __name__ == "__main__":
    main()
