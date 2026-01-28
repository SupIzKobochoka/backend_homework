from __future__ import annotations

import asyncio

import joblib
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

import logging

logger = logging.getLogger(__name__)


def train_demo_model() -> Pipeline:
    texts = [
        "I love this product",
        "Great service",
        "Excellent quality",
        "Best purchase ever",
        "Highly recommend",
        "Amazing experience",
        "Terrible product",
        "Worst service",
        "Poor quality",
        "Waste of money",
        "Do not buy",
        "Horrible experience",
    ]
    labels = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]

    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=100)),
            ("clf", LogisticRegression()),
        ]
    )
    model.fit(texts, labels)
    return model


def load_or_train_model(model_path: str) -> Pipeline:
    try:
        model = joblib.load(model_path)
        logger.info("Model loaded successfully from file: %s", model_path)
        return model
    except FileNotFoundError:
        logger.info("Model not found at %s, training new model...", model_path)
        model = train_demo_model()
        joblib.dump(model, model_path)
        logger.info("Model trained and saved successfully to: %s", model_path)
        return model


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)


class PredictResponse(BaseModel):
    pred: int
    confidence: float


class BatchPredictRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=100)


class BatchPredictionItem(BaseModel):
    text: str
    pred: int
    confidence: float


class BatchPredictResponse(BaseModel):
    predictions: list[BatchPredictionItem]


class PredictResponseWithModelInfo(PredictResponse):
    model_version: str
    model_stage: str




def predict(model: Pipeline, text: str) -> tuple[int, float]:
    pred = int(model.predict([text])[0])
    proba = model.predict_proba([text])[0]
    confidence = float(max(proba))
    return pred, confidence


def predict_batch(model: Pipeline, texts: list[str]) -> tuple[list[int], list[list[float]]]:
    preds = [int(x) for x in model.predict(texts)]
    probas = model.predict_proba(texts)
    return preds, probas.tolist()


app = FastAPI(
    title="API",
    description="API using ML model",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    app.state.model = load_or_train_model("model.pkl")


def get_model() -> Pipeline:
    return app.state.model


def validate_and_predict(req: PredictRequest, model: Pipeline = Depends(get_model)) -> PredictResponse:
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not available")

    try:
        pred, confidence = predict(model, req.text)
        return PredictResponse(pred=pred, confidence=confidence)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Prediction error")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


router = APIRouter()


@router.get("/health")
def health(model: Pipeline = Depends(get_model)):
    return {"status": "healthy", "model_loaded": model is not None}


@router.post("/predict", response_model=PredictResponse)
async def predict_endpoint(req: PredictRequest, model: Pipeline = Depends(get_model)):
    await asyncio.sleep(0.1)
    try:
        return validate_and_predict(req, model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-predict", response_model=BatchPredictResponse)
async def batch_predict(req: BatchPredictRequest, model: Pipeline = Depends(get_model)):
    await asyncio.sleep(0.1)
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not available")

    try:
        preds, probas = predict_batch(model, req.texts)
        items: list[BatchPredictionItem] = []
        for text, pred, proba in zip(req.texts, preds, probas):
            items.append(
                BatchPredictionItem(
                    text=text,
                    pred=pred,
                    confidence=float(max(proba)),
                )
            )
        logger.info("Batch prediction completed for %s texts", len(req.texts))
        return BatchPredictResponse(predictions=items)
    except Exception as e:
        logger.exception("Batch prediction error")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {e}")


app.include_router(router)