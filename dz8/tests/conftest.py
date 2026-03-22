import pytest
import numpy as np
from typing import Callable, Generator
from fastapi.testclient import TestClient

from main import create_app
from routes.predict import get_model, get_producer
from db_scripts.redis import PredictRedisStorage, SyncPredictRedisStorage
from db_scripts.storages import AdRepository, ModerationRepository
from db_scripts.dependencies import get_current_account
from schemas.account import Account

BASE_AD = {
    "seller_id": 1,
    "is_verified_seller": True,
    "item_id": 1,
    "name": "test",
    "description": "test",
    "category": 11,
    "images_qty": 1,
}


@pytest.fixture(scope="function")
def client() -> TestClient:
    return TestClient(create_app())


@pytest.fixture(scope="function")
def client_without_lifespan() -> TestClient:
    return TestClient(create_app())


@pytest.fixture
def get_ad() -> Callable[..., dict[str, str | bool | int]]:
    args = BASE_AD.copy()

    def _get_ad(**kwargs) -> dict[str, str | bool | int]:
        return {**args, **kwargs}

    return _get_ad


class FakeModel:
    def __init__(self, value):
        self.value = value

    def predict_proba(self, *args, **kwargs):
        return np.array([[1 - float(self.value), float(self.value)]])

    def predict(self, *args, **kwargs):
        return np.array(self.value)


@pytest.fixture(scope="function")
def set_only_true_model(client: TestClient):
    client.app.dependency_overrides[get_model] = lambda: FakeModel(value=1)
    yield
    client.app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def set_only_false_model(client: TestClient):
    client.app.dependency_overrides[get_model] = lambda: FakeModel(value=0)
    yield
    client.app.dependency_overrides.clear()


class FakeAdRepository:
    def __init__(self, *args, fake_ad_return=BASE_AD, **kwargs):
        self.fake_ad_return = fake_ad_return.copy() if isinstance(fake_ad_return, dict) else fake_ad_return

    async def get_ad(self, *args, **kwargs):
        return self.fake_ad_return


class FakeModerationRepository:
    def __init__(self, *args, task_id=69, **kwargs):
        self.task_id = task_id
        self.deleted_item_id = None

    async def check_and_add_item(self, *args, **kwargs):
        return self.task_id

    async def delete_by_item_id(self, item_id: int):
        self.deleted_item_id = item_id


@pytest.fixture(scope="function")
def set_fake_ad_repo(client: TestClient):
    client.app.dependency_overrides[AdRepository] = lambda: FakeAdRepository()
    yield
    client.app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def set_fake_ad_repo_none(client: TestClient):
    client.app.dependency_overrides[AdRepository] = lambda: FakeAdRepository(fake_ad_return=None)
    yield
    client.app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def set_fake_moderation_repo(client: TestClient):
    client.app.dependency_overrides[ModerationRepository] = lambda: FakeModerationRepository(task_id=69)
    yield
    client.app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def set_fake_moderation_repo_none(client: TestClient):
    client.app.dependency_overrides[ModerationRepository] = lambda: FakeModerationRepository(task_id=None)
    yield
    client.app.dependency_overrides.clear()


class FakeKafkaProducer:
    async def send_moderation_request(self, item_id: int):
        self.send_moderation_request_item_id = item_id


@pytest.fixture(scope="function")
def set_fake_kafka_provider(client: TestClient) -> Generator[FakeKafkaProducer, None, None]:
    fake_kafka = FakeKafkaProducer()
    client.app.dependency_overrides[get_producer] = lambda: fake_kafka
    yield fake_kafka
    client.app.dependency_overrides.clear()


class FakeRedis:
    def __init__(self, *args, **kwargs):
        self.deleted_ad = None

    async def get(self, *args, **kwargs):
        return None

    async def set(self, *args, **kwargs):
        return None

    async def delete(self, ad: dict):
        self.deleted_ad = ad
        return None


@pytest.fixture(scope="function", autouse=True)
def set_fake_redis_storage(client: TestClient):
    fake_redis = FakeRedis()
    client.app.dependency_overrides[PredictRedisStorage] = lambda: fake_redis
    yield fake_redis
    client.app.dependency_overrides.pop(PredictRedisStorage, None)


class SyncFakeRedis:
    def get(self, *args, **kwargs):
        return None

    def set(self, *args, **kwargs):
        return None


@pytest.fixture(scope="function", autouse=True)
def set_sync_fake_redis_storage(client: TestClient):
    client.app.dependency_overrides[SyncPredictRedisStorage] = lambda: SyncFakeRedis()
    yield
    client.app.dependency_overrides.pop(SyncPredictRedisStorage, None)


class FakeAdRepositoryForClose:
    def __init__(self, *args, fake_ad_return=BASE_AD, **kwargs):
        self.fake_ad_return = fake_ad_return.copy() if isinstance(fake_ad_return, dict) else fake_ad_return
        self.deleted_item_id = None

    async def get_ad(self, *args, **kwargs):
        return self.fake_ad_return

    async def delete_ad(self, item_id: int) -> None:
        self.deleted_item_id = item_id


@pytest.fixture(scope="function")
def set_fake_ad_repo_for_close(client: TestClient):
    fake_repo = FakeAdRepositoryForClose()
    client.app.dependency_overrides[AdRepository] = lambda: fake_repo
    yield fake_repo
    client.app.dependency_overrides.pop(AdRepository, None)


@pytest.fixture(scope="function")
def set_fake_ad_repo_for_close_none(client: TestClient):
    fake_repo = FakeAdRepositoryForClose(fake_ad_return=None)
    client.app.dependency_overrides[AdRepository] = lambda: fake_repo
    yield fake_repo
    client.app.dependency_overrides.pop(AdRepository, None)


@pytest.fixture(scope="function", autouse=True)
def set_fake_auth_account(client: TestClient):
    client.app.dependency_overrides[get_current_account] = lambda: Account(
        id=1,
        login="test",
        password="x",
        is_blocked=False,
    )
    yield
    client.app.dependency_overrides.pop(get_current_account, None)


class DefaultProducer:
    async def send_moderation_request(self, item_id: int):
        return None


@pytest.fixture(scope="function", autouse=True)
def set_default_model_and_producer(client: TestClient):
    client.app.dependency_overrides[get_model] = lambda: FakeModel(value=0)
    client.app.dependency_overrides[get_producer] = lambda: DefaultProducer()
    yield
    client.app.dependency_overrides.pop(get_model, None)
    client.app.dependency_overrides.pop(get_producer, None)
