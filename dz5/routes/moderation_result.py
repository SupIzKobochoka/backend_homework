from fastapi import APIRouter, Depends, HTTPException
from typing import Any

from db_scripts.storages import ModerationRepository
from utils import logger

router = APIRouter()

@router.get("/moderation_result/{task_id}")
async def moderation_result(task_id: int,
                            moderation_repo: ModerationRepository = Depends(),
                            ) -> dict[str, Any]:
    response = await moderation_repo.get_task(task_id)

    if response is None:
        logger.exception("task_id is not found")
        raise HTTPException(status_code=404, detail="task_id is not found")

    cols_to_return = ["status", "is_violation", "probability"]
    return {col: response.get(col) for col in cols_to_return}