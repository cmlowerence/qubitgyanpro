# qubitgyanpro\services\ml_model.py

import os
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

MODEL_PATH = "ml_models/recommendation_model.pkl"
SCALER_PATH = "ml_models/recommendation_scaler.pkl"


def train_model(X, y):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        n_jobs=-1
    )

    model.fit(X_scaled, y)

    os.makedirs("ml_models", exist_ok=True)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    return model


def load_model():
    try:
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        return model, scaler
    except Exception:
        return None, None