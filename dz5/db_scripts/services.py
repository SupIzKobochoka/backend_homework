from utils import logger
from functools import wraps
from fastapi import HTTPException

def async_log_db_calls(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f'db call: {func.__name__}, {args=}, {kwargs=}')
        
        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            logger.exception(f'error while data base query, {e}')
            raise HTTPException(500, detail=f'Internal Server Error while data base query')
        return result
    
    return wrapper