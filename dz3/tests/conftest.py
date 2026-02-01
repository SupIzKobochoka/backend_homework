import pytest
from main import create_app
from fastapi.testclient import TestClient
from typing import Callable
from sklearn.linear_model import LogisticRegression
from model import train_model

@pytest.fixture(scope="function")
def client() -> TestClient:
    with TestClient(create_app()) as client: # Чтобы lifespan работал
        yield client

@pytest.fixture
def client_without_lifespan() -> TestClient:
    return TestClient(create_app())

@pytest.fixture
def get_ad() -> Callable[..., dict[str, str|bool|int]]:
    args = {'seller_id': 1,
            'is_verified_seller': True,
            'item_id': 1,
            'name': 'test',
            'description': 'test',
            'category': 11,
            'images_qty': 1}
    
    def _get_ad(**kwargs) -> dict[str, str|bool|int]:
        return {**args, **kwargs}
    
    return _get_ad