from fastapi import APIRouter, Request, Depends, HTTPException
from typing import Callable

from schemas.ad import Ad
from schemas.predicted import PredictedAd
from model import get_pred
from db_scripts.storages import AdRepository, ModerationRepository
from client.kafka import KafkaProducer
from utils import logger

router = APIRouter()

def get_model(request: Request) -> Callable:
    try:
        return request.app.state.model
    except AttributeError:
        logger.exception("model doesnt found")
        raise HTTPException(503, detail="Service Unavailable")


def get_producer(request: Request) -> KafkaProducer:
    try:
        return request.app.state.producer
    except AttributeError:
        logger.exception("producer doesnt found")
        raise HTTPException(503, detail="Service Unavailable")


@router.post("/predict_one")
def predict_one(ad: Ad,
                model=Depends(get_model),
                ) -> PredictedAd:
    logger.info(f"data input: {ad.model_dump()}")
    try:
        predicted = get_pred(model=model, ad=ad.model_dump())
        logger.info(f"predicted: {predicted}")
        return PredictedAd(**predicted)
    except Exception as e:
        logger.exception(f"error while prediction, {e}")
        raise HTTPException(500, detail="Internal Server Error while prediction")


@router.post("/simple_predict")
async def simple_predict(item_id: int,
                         model=Depends(get_model),
                         ad_repo: AdRepository = Depends(),
                         ) -> PredictedAd:
    ad = await ad_repo.get_ad(item_id)
    if ad is None:
        logger.exception(f"No such item_id: {item_id}")
        raise HTTPException(404, detail=f"No such item_id: {item_id}")

    logger.info(f"data input: {ad}")
    try:
        predicted = get_pred(model=model, ad=ad)
        logger.info(f"predicted: {predicted}")
        return PredictedAd(**predicted)
    except Exception as e:
        logger.exception(f"error while prediction, {e}")
        raise HTTPException(500, detail="Internal Server Error while prediction")


@router.post("/async_predict")
async def async_predict(item_id: int,
                        kafka_producer: KafkaProducer = Depends(get_producer),
                        moderation_repo: ModerationRepository = Depends(),
                        ) -> int:
    task_id = await moderation_repo.check_and_add_item(item_id)
    if task_id is None:
        logger.exception(f"No such item_id: {item_id}")
        raise HTTPException(404, detail=f"No such item_id: {item_id}")

    await kafka_producer.send_moderation_request(item_id)
    return task_id