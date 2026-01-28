from fastapi import APIRouter, Request, Depends, HTTPException
from schemas.ad import Ad
from schemas.predicted import PredictedAd
from model import get_pred
from typing import Callable
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

def get_model(request: Request) -> Callable:
    try:
        return request.app.state.model
    except AttributeError:
        logger.exception('model doesnt found')
        raise HTTPException(503, detail='Service Unavailable') 

@router.post('/predict_one')
def predict_one(ad: Ad, model = Depends(get_model)) -> PredictedAd:
    logger.info(f'data input: {ad.model_dump()}')
    try:
        predicted = get_pred(model=model, ad=ad.model_dump())
        logger.info(f'predicted: {predicted}')
        return PredictedAd(**predicted)
    except Exception as e: 
        logger.exception(f'error while prediction, {e}')
        raise HTTPException(500, detail=f'Internal Server Error while prediction')
