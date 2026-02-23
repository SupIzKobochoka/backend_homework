import pytest
from main import create_app, app
from fastapi.testclient import TestClient
from typing import Callable, Generator
from routes.predict import get_model, get_producer
import numpy as np

from db_scripts.storages import AdRepository, ModerationRepository

BASE_AD = {
    "seller_id": 1,
    "is_verified_seller": True,
    "item_id": 1,
    "name": "test",
    "description": "test",
    "category": 11,
    "images_qty": 1,
}


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:  # Чтобы lifespan работал
        yield client


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
def set_only_true_model():
    app.dependency_overrides[get_model] = lambda: FakeModel(value=1)
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def set_only_false_model():
    app.dependency_overrides[get_model] = lambda: FakeModel(value=0)
    yield
    app.dependency_overrides.clear()


class FakeAdRepository:
    def __init__(self, *args, fake_ad_return=BASE_AD, **kwargs):
        self.fake_ad_return = fake_ad_return.copy() if isinstance(fake_ad_return, dict) else fake_ad_return

    async def get_ad(self, *args, **kwargs):
        return self.fake_ad_return


class FakeModerationRepository:
    def __init__(self, *args, task_id=69, **kwargs):
        self.task_id = task_id

    async def check_and_add_item(self, *args, **kwargs):
        return self.task_id


@pytest.fixture(scope="function")
def set_fake_ad_repo():
    app.dependency_overrides[AdRepository] = lambda: FakeAdRepository()
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def set_fake_ad_repo_none():
    app.dependency_overrides[AdRepository] = lambda: FakeAdRepository(fake_ad_return=None)
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def set_fake_moderation_repo():
    app.dependency_overrides[ModerationRepository] = lambda: FakeModerationRepository(task_id=69)
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def set_fake_moderation_repo_none():
    app.dependency_overrides[ModerationRepository] = lambda: FakeModerationRepository(task_id=None)
    yield
    app.dependency_overrides.clear()


class FakeKafkaProducer:
    def __init__(self, *args, **kwargs):
        ...

    async def send_moderation_request(self, item_id: int):
        self.send_moderation_request_item_id = item_id


@pytest.fixture(scope="function")
def set_fake_kafka_provider() -> Generator[FakeKafkaProducer, None, None]:
    fake_kafka = FakeKafkaProducer()
    app.dependency_overrides[get_producer] = lambda: fake_kafka
    yield fake_kafka
    app.dependency_overrides.clear()