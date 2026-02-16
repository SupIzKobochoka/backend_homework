import asyncpg
from typing import AsyncGenerator
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_pg_connection() -> AsyncGenerator[None, asyncpg.Connection]:
    connection: asyncpg.Connection = await asyncpg.connect(
        database="lesson",
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port=5432,
    )

    yield connection

    await connection.close()