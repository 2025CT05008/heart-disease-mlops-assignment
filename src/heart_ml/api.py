"""FastAPI inference service."""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field
from starlette.responses import Response

from heart_ml.data import FEATURE_COLUMNS

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)
MODEL_PATH = Path(os.getenv("MODEL_PATH", "models/heart_disease_pipeline.joblib"))
PREDICTION_COUNT = Counter("heart_predictions_total", "Number of prediction requests", ["outcome"])
PREDICTION_LATENCY = Histogram("heart_prediction_latency_seconds", "Prediction latency in seconds")


class PatientFeatures(BaseModel):
    age: float = Field(ge=1, le=120)
    sex: int = Field(ge=0, le=1)
    cp: int = Field(ge=1, le=4)
    trestbps: float = Field(ge=50, le=300)
    chol: float = Field(ge=50, le=700)
    fbs: int = Field(ge=0, le=1)
    restecg: int = Field(ge=0, le=2)
    thalach: float = Field(ge=40, le=250)
    exang: int = Field(ge=0, le=1)
    oldpeak: float = Field(ge=0, le=10)
    slope: int = Field(ge=1, le=3)
    ca: float = Field(ge=0, le=4)
    thal: float = Field(ge=3, le=7)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model file not found: {MODEL_PATH}. Run training first.")
    app.state.model = joblib.load(MODEL_PATH)
    logger.info("Loaded model from %s", MODEL_PATH)
    yield


app = FastAPI(title="Heart Disease Risk API", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model_path": str(MODEL_PATH)}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/predict")
def predict(patient: PatientFeatures) -> dict[str, float | int]:
    try:
        row = pd.DataFrame(
            [[getattr(patient, col) for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS
        )
        with PREDICTION_LATENCY.time():
            probability = float(app.state.model.predict_proba(row)[0, 1])
        prediction = int(probability >= 0.5)
        PREDICTION_COUNT.labels(outcome=str(prediction)).inc()
        logger.info("prediction=%s confidence=%.4f", prediction, probability)
        return {"prediction": prediction, "confidence": round(probability, 4)}
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed") from exc
