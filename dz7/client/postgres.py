import os
import asyncpg
from typing import AsyncGenerator
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_pg_connection() -> AsyncGenerator[None, asyncpg.Connection]:
    connection: asyncpg.Connection = await asyncpg.connect(
        database=os.getenv("POSTGRES_DB", "hw"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5435")),
    )
    yield connection
    await connection.close()
