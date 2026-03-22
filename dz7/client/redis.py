import redis.asyncio
import redis
from typing import AsyncGenerator, Generator
from contextlib import asynccontextmanager
from contextlib import contextmanager

@asynccontextmanager
async def get_redis_connection() -> AsyncGenerator[redis.asyncio.Redis, None]:
    connection = redis.asyncio.Redis(host="localhost", port=6379)

    yield connection

    await connection.aclose()

@contextmanager
def sync_get_redis_connection() -> Generator[redis.Redis, None, None]:
    connection = redis.Redis(host="localhost", port=6379)

    try:
        yield connection
    finally:
        connection.close()