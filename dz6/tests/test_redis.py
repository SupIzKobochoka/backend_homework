import pytest
from json import dumps
import pytest
from uuid import uuid4
import redis
import redis.asyncio as aredis
from db_scripts.redis import PredictRedisStorage, SyncPredictRedisStorage

@pytest.mark.asyncio
async def test_async_set_calls_pipeline(monkeypatch):
    calls = {}

    class FakePipeline:
        def set(self, name, value):
            calls["set"] = {"name": name, "value": value}

        def expire(self, name, ttl):
            calls["expire"] = {"name": name, "ttl": ttl}

        async def execute(self):
            calls["execute"] = True

    class FakeConnection:
        def pipeline(self):
            return FakePipeline()

    class FakeCtx:
        async def __aenter__(self):
            return FakeConnection()

        async def __aexit__(self, exc_type, exc, tb):
            return False
        
    monkeypatch.setattr("db_scripts.redis.get_redis_connection", lambda: FakeCtx())

    storage = PredictRedisStorage()

    ad = {"b": 2, "a": 1}  # специально "не по порядку"
    value = {"ok": True}

    await storage.set(ad=ad, value=value)

    key = dumps(ad, sort_keys=True)

    assert calls["set"]["name"] == key
    assert calls["set"]["value"] == dumps(value)
    assert calls["expire"]["name"] == key
    assert calls["expire"]["ttl"] == storage._TTL
    assert calls["execute"] is True


@pytest.mark.asyncio
async def test_async_get_returns_value(monkeypatch):
    ad = {"b": 2, "a": 1}
    key = dumps(ad, sort_keys=True)

    class FakeConnection:
        async def get(self, name):
            assert name == key
            return dumps({"x": 123})

    class FakeCtx:
        async def __aenter__(self):
            return FakeConnection()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr("db_scripts.redis.get_redis_connection", lambda: FakeCtx())

    storage = PredictRedisStorage()
    result = await storage.get(ad)

    assert result == {"x": 123}


@pytest.mark.asyncio
async def test_async_get_returns_none(monkeypatch):
    class FakeConnection:
        async def get(self, name):
            return None

    class FakeCtx:
        async def __aenter__(self):
            return FakeConnection()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr("db_scripts.redis.get_redis_connection", lambda: FakeCtx())

    storage = PredictRedisStorage()
    result = await storage.get({"a": 1})

    assert result is None


@pytest.mark.asyncio
async def test_async_delete_calls_delete(monkeypatch):
    calls = {}

    ad = {"b": 2, "a": 1}
    key = dumps(ad, sort_keys=True)

    class FakeConnection:
        async def delete(self, name):
            calls["delete"] = name

    class FakeCtx:
        async def __aenter__(self):
            return FakeConnection()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr("db_scripts.redis.get_redis_connection", lambda: FakeCtx())

    storage = PredictRedisStorage()
    await storage.delete(ad)

    assert calls["delete"] == key

def test_sync_set_calls_pipeline(monkeypatch):
    calls = {}

    class FakePipeline:
        def set(self, name, value):
            calls["set"] = {"name": name, "value": value}

        def expire(self, name, ttl):
            calls["expire"] = {"name": name, "ttl": ttl}

        def execute(self):
            calls["execute"] = True

    class FakeConnection:
        def pipeline(self):
            return FakePipeline()

    class FakeCtx:
        def __enter__(self):
            return FakeConnection()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr("db_scripts.redis.sync_get_redis_connection", lambda: FakeCtx())

    storage = SyncPredictRedisStorage()

    ad = {"b": 2, "a": 1}
    value = {"ok": True}

    storage.set(ad=ad, value=value)

    key = dumps(ad, sort_keys=True)

    assert calls["set"]["name"] == key
    assert calls["set"]["value"] == dumps(value)
    assert calls["expire"]["name"] == key
    assert calls["expire"]["ttl"] == storage._TTL
    assert calls["execute"] is True


def test_sync_get_returns_value(monkeypatch):
    ad = {"b": 2, "a": 1}
    key = dumps(ad, sort_keys=True)

    class FakeConnection:
        def get(self, name):
            assert name == key
            return dumps({"x": 123})

    class FakeCtx:
        def __enter__(self):
            return FakeConnection()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr("db_scripts.redis.sync_get_redis_connection", lambda: FakeCtx())

    storage = SyncPredictRedisStorage()
    result = storage.get(ad)

    assert result == {"x": 123}


def test_sync_get_returns_none(monkeypatch):
    class FakeConnection:
        def get(self, name):
            return None

    class FakeCtx:
        def __enter__(self):
            return FakeConnection()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr("db_scripts.redis.sync_get_redis_connection", lambda: FakeCtx())

    storage = SyncPredictRedisStorage()
    assert storage.get({"a": 1}) is None


def test_sync_delete_calls_delete(monkeypatch):
    calls = {}

    ad = {"b": 2, "a": 1}
    key = dumps(ad, sort_keys=True)

    class FakeConnection:
        def delete(self, name):
            calls["delete"] = name

    class FakeCtx:
        def __enter__(self):
            return FakeConnection()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr("db_scripts.redis.sync_get_redis_connection", lambda: FakeCtx())

    storage = SyncPredictRedisStorage()
    storage.delete(ad)

    assert calls["delete"] == key

def _redis_available_sync() -> bool:
    try:
        r = redis.Redis(host="localhost", port=6379)
        r.ping()
        r.close()
        return True
    except Exception:
        return False


async def _redis_available_async() -> bool:
    try:
        r = aredis.Redis(host="localhost", port=6379)
        await r.ping()
        await r.aclose()
        
        return True
    except Exception:
        return False


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_storage_set_get_delete_in_redis():
    if not await _redis_available_async():
        pytest.skip("Redis is not available on localhost:6379")

    storage = PredictRedisStorage()

    ad = {"item_id": 1, "uniq": str(uuid4())}
    value = {"score": 0.77}

    await storage.set(ad, value)

    got = await storage.get(ad)
    assert got == value

    await storage.delete(ad)
    got2 = await storage.get(ad)
    assert got2 is None


@pytest.mark.integration
def test_sync_storage_set_get_delete_in_redis():
    if not _redis_available_sync():
        pytest.skip("Redis is not available on localhost:6379")

    storage = SyncPredictRedisStorage()

    ad = {"item_id": 1, "uniq": str(uuid4())}
    value = {"score": 0.77}

    storage.set(ad, value)

    got = storage.get(ad)
    assert got == value

    storage.delete(ad)
    got2 = storage.get(ad)
    assert got2 is None