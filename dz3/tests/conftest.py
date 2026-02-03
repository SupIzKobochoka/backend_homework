import pytest
from main import create_app, app
from fastapi.testclient import TestClient
from typing import Callable, Generator
from routes.predict import get_model, get_ad_provider
import numpy as np

BASE_AD = {'seller_id': 1,
           'is_verified_seller': True,
           'item_id': 1,
           'name': 'test',
           'description': 'test',
           'category': 11,
           'images_qty': 1}

@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as client: # Чтобы lifespan работал
        yield client

@pytest.fixture(scope="function")
def client_without_lifespan() -> TestClient:
    return TestClient(create_app())

class FakeModel:
    def __init__(self, value):
        self.value = value

    def predict_proba(self, *args, **kwargs):
        return np.array([[1-float(self.value), float(self.value)]])

    def predict(self, *args, **kwargs):
        return np.array(self.value)

@pytest.fixture(scope="function")
def set_only_true_model():
    app.dependency_overrides[get_model] = lambda: FakeModel(1)
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def set_only_false_model():
    app.dependency_overrides[get_model] = lambda: FakeModel(0)
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def get_ad() -> Callable[..., dict[str, str|bool|int]]:
    args = BASE_AD.copy()
    
    def _get_ad(**kwargs) -> dict[str, str|bool|int]:
        return {**args, **kwargs}
    
    return _get_ad

async def get_ad_(ad_id: int):
    return BASE_AD.copy()

@pytest.fixture(scope="function")
def set_fake_get_ad():
    app.dependency_overrides[get_ad_provider] = lambda: get_ad_
    yield
    app.dependency_overrides.clear()

async def get_ad_None(ad_id: int):
    return None

@pytest.fixture(scope="function")
def set_None_get_ad():
    app.dependency_overrides[get_ad_provider] = lambda: get_ad_None
    yield
    app.dependency_overrides.clear()
    