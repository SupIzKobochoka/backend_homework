import pytest
import asyncpg
from uuid import uuid4

from db_scripts.storages import AdRepository


async def _pg_available() -> bool:
    try:
        conn = await asyncpg.connect(database="lesson",
                                     user="postgres",
                                     password="postgres",
                                     host="127.0.0.1",
                                     port=5432)
        await conn.close()
        return True
    except Exception:
        return False

@pytest.mark.integration
@pytest.mark.asyncio
async def test_ad_add_get_delete_in_postgres():
    if not await _pg_available():
        raise ConnectionError('Postgres donst run')

    repo = AdRepository()

    # Какой-то левый айдишник
    item_id = int(uuid4().int % 1_000_000_000)

    await repo.add_ad(seller_id=1,
                      item_id=item_id,
                      name="test",
                      description="test",
                      category=11,
                      images_qty=1)

    ad = await repo.get_ad(item_id)
    assert ad is not None
    assert ad["item_id"] == item_id
    assert ad["seller_id"] == 1
    assert ad["name"] == "test"
    assert ad["description"] == "test"
    assert ad["category"] == 11
    assert ad["images_qty"] == 1

    await repo.delete_ad(item_id)

    ad2 = await repo.get_ad(item_id)
    assert ad2 is None

@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_missing_ad_returns_none():
    if not await _pg_available():
        raise ConnectionError('Postgres donst run')

    repo = AdRepository()

    missing_item_id = int(uuid4().int % 1_000_000_000)
    ad = await repo.get_ad(missing_item_id)
    assert ad is None