import pytest
from fastapi.testclient import TestClient
from typing import Callable, Any
from fastapi import status
from client.kafka import KafkaProducer

def test_is_violation_true(client: TestClient,
                           get_ad: Callable[..., dict[str, str|bool|int]],
                           set_only_true_model: None,
                           ):
    ad = get_ad()
    response = client.post('/predict_one', json=ad)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['is_violation'] is True

def test_is_violation_false(client: TestClient,
                            get_ad: Callable[..., dict[str, str|bool|int]],
                            set_only_false_model: None,
                            ):
    ad = get_ad()
    response = client.post('/predict_one', json=ad)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['is_violation'] is False


@pytest.mark.parametrize('field,value', [['images_qty', 'TWO'],
                                         ['is_verified_seller', 'YES'],
                                         ['images_qty', 'TWO']]
                        )
def test_wrong_types(field: str,
                     value: Any,
                     get_ad: Callable[..., dict[str, str|bool|int]],
                     client: TestClient,
                    ):
    ad = get_ad(**{field: value})
    response = client.post(url='/predict_one',
                            json=ad)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_model_not_found(get_ad: Callable[..., dict[str, str|bool|int]],
                         client_without_lifespan: TestClient
                         ):
    ad = get_ad()
    response = client_without_lifespan.post(url='/predict_one', json=ad)
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.parametrize('item_id', [True, 'One', 31.1])
def test_wrong_types_simple_predict(item_id: Any,
                                    client: TestClient,
                                    set_fake_db_provider: None,                                   
                                    ):
    response = client.post(url='/simple_predict', params={'item_id': item_id})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.parametrize('item_id', [1, 2, 3])
def test_missing_id_simple_predict(item_id: int,
                                    client: TestClient,
                                    set_fake_db_None_provider: None
                                    ):
    response = client.post(url='/simple_predict', params={'item_id': item_id})
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.parametrize('item_id', [1, 2, 3])
def test_true_simple_predict(item_id: int,
                             client: TestClient,
                             set_fake_db_provider: None,
                             set_only_true_model: None
                             ):
    response = client.post(url='/simple_predict', 
                           params={'item_id': item_id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['is_violation'] is True

@pytest.mark.parametrize('item_id', [1, 2, 3])
def test_false_simple_predict(item_id: int,
                             client: TestClient,
                             set_fake_db_provider: None,
                             set_only_false_model: None
                             ):
    response = client.post(url='/simple_predict', 
                           params={'item_id': item_id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['is_violation'] is False

@pytest.mark.parametrize('item_id', [1, 2, 3])
def test_async_predict_call(item_id: int,
                            client: TestClient,
                            set_fake_kafka_provider: KafkaProducer,
                            set_fake_db_provider: None,
                            ):
    response = client.post(url='/async_predict', params={'item_id': item_id})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == 69
    assert set_fake_kafka_provider.send_moderation_request_item_id == item_id
