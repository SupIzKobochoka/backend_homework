import pytest
from main import create_app, app
from fastapi.testclient import TestClient
from typing import Callable, Generator
from routes.predict import get_model
from db_scripts.db_access import get_db_provider, DBProvider
from routes.predict import get_producer
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

@pytest.fixture
def get_ad() -> Callable[..., dict[str, str|bool|int]]:
    args = BASE_AD.copy()
    
    def _get_ad(**kwargs) -> dict[str, str|bool|int]:
        return {**args, **kwargs}
    
    return _get_ad

class FakeModel:
    def __init__(self, value):
        self.value = value

    def predict_proba(self, *args, **kwargs):
        return np.array([[1-float(self.value), float(self.value)]])

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

class FakeDBProvider:
    def __init__(self, *args, fake_ad_return=BASE_AD, **kwargs):
        if isinstance(fake_ad_return, dict):
            self.fake_ad_return = fake_ad_return.copy()
        else:
            self.fake_ad_return = fake_ad_return
        self.fake_ad_return = fake_ad_return

    async def get_ad(self, *args, **kwargs):
        return self.fake_ad_return
    
    async def check_and_add_moderation(self, *args, **kwargs):
        return True, 69

@pytest.fixture(scope="function")
def set_fake_db_provider():
    app.dependency_overrides[get_db_provider] = lambda: FakeDBProvider()
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def set_fake_db_None_provider():
    app.dependency_overrides[get_db_provider] = lambda: FakeDBProvider(fake_ad_return=None)
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

# @router.post('/async_predict')
# async def async_predict(item_id: int,
#                         kafka_producer: KafkaProducer = Depends(get_producer),
#                         db_provider: DBProvider = Depends(get_db_provider),
#                         ) -> int:
#     item_id_exist, task_id = await db_provider.check_and_add_moderation(item_id)
#     if item_id_exist is False:
#         logger.exception(f'No such item_id: {item_id}')
#         raise HTTPException(404, detail=f'No such item_id: {item_id}')
#     await kafka_producer.send_moderation_request(item_id)

#     return task_id