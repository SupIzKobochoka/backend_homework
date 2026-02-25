from fastapi import APIRouter, Request, Depends, HTTPException
from typing import Callable

from schemas.ad import Ad
from schemas.predicted import PredictedAd
from model import get_pred
from db_scripts.storages import AdRepository, ModerationRepository
from client.kafka import KafkaProducer
from utils import logger
from db_scripts.redis import PredictRedisStorage, SyncPredictRedisStorage

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
                sync_predict_redis_storage=Depends(SyncPredictRedisStorage),
                ) -> PredictedAd:
    logger.info(f"data input: {ad.model_dump()}")
    try:
        redis_response = sync_predict_redis_storage.get(ad.model_dump())
        if redis_response:
            return PredictedAd(**redis_response)
        predicted = get_pred(model=model, ad=ad.model_dump())
        sync_predict_redis_storage.set(ad, predicted)
        logger.info(f"predicted: {predicted}")
        return PredictedAd(**predicted)
    except Exception as e:
        logger.exception(f"error while prediction, {e}")
        raise HTTPException(500, detail="Internal Server Error while prediction")


@router.post("/simple_predict")
async def simple_predict(item_id: int,
                         model=Depends(get_model),
                         ad_repo: AdRepository = Depends(),
                         predict_redis_storage: PredictRedisStorage = Depends(),
                         ) -> PredictedAd:
    ad = await ad_repo.get_ad(item_id)
    if ad is None:
        logger.exception(f"No such item_id: {item_id}")
        raise HTTPException(404, detail=f"No such item_id: {item_id}")
    logger.info(f"data input: {ad}")
    try:
        redis_response = await predict_redis_storage.get(ad)
        if redis_response:
            return PredictedAd(**redis_response)
        predicted = get_pred(model=model, ad=ad)
        await predict_redis_storage.set(ad, predicted)
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