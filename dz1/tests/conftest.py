import pytest
from model_ad import Ad
from main import app
from fastapi.testclient import TestClient
from typing import Callable, Mapping, Any

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture
def get_ad() -> Callable[..., dict[str, str|bool|int]]:
    args = {'seller_id': 1,
            'is_verified_seller': True,
            'item_id': 1,
            'name': 'test',
            'description': 'test',
            'category': 'car',
            'images_qty': 1}
    
    def _get_ad(**kwargs) -> dict[str, str|bool|int]:
        return {**args, **kwargs}
    
    return _get_ad