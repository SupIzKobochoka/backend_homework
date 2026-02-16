from fastapi import APIRouter, Depends, HTTPException
from db_scripts.db_access import DBProvider, get_db_provider
from typing import Any
from utils import logger

router = APIRouter()

@router.get('/moderation_result/{task_id}')
async def moderation_result(task_id: int,
                      db_provider: DBProvider = Depends(get_db_provider)
                      ) -> dict[str, Any]:
    response = await db_provider.get_ad_from_moderation(task_id)
    if response is None:
        logger.exception('task_id is not found')
        raise HTTPException(404, detail='task_id is not found')
    cols_to_return = ['status', 'is_violation', 'probability']
    return {col: response[col] for col in cols_to_return}