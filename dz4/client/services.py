from utils import logger
from functools import wraps
from fastapi import HTTPException

def async_log_kafka_calls(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f'kafka call: {func.__name__}, {args=}, {kwargs=}')
        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            logger.exception(f'error while data kafka query, {e}')
            raise HTTPException(500, detail=f'Internal Server Error while data base query')
        return result
    
    return wrapper