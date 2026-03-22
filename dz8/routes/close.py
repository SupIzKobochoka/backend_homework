from fastapi import APIRouter, Request, Depends, HTTPException
from typing import Callable
from db_scripts.storages import AdRepository, ModerationRepository
from db_scripts.redis import PredictRedisStorage
from utils import logger

router = APIRouter()

@router.post("/close")
async def close_ad(
    item_id: int,
    ad_repo: AdRepository = Depends(),
    moderation_repo: ModerationRepository = Depends(),
    predict_redis_storage: PredictRedisStorage = Depends(),
):
    ad = await ad_repo.get_ad(item_id)
    if ad is None:
        logger.exception(f"No such item_id: {item_id}")
        raise HTTPException(404, detail=f"No such item_id: {item_id}")

    try:
        await predict_redis_storage.delete(ad)
        await moderation_repo.delete_by_item_id(item_id)
        await ad_repo.delete_ad(item_id)

        logger.info(f"Ad closed and prediction cache deleted: {item_id}")
        return {"status": "closed", "item_id": item_id}
    except Exception as e:
        logger.exception(f"error while closing ad {item_id}, {e}")
        raise HTTPException(500, detail="Internal Server Error while closing ad")
