import pytest
from fastapi.testclient import TestClient
from typing import Callable, Any
from fastapi import status

# Тест успешного предсказания (is_violation = True)
# Тест успешного предсказания (is_violation = False)
# Тест валидации входных данных (неверные типы)
# Тест обработки ошибки при недоступной модели

def test_is_violation_true(client: TestClient,
                           get_ad: Callable[..., dict[str, str|bool|int]],
                           ):
    ad = get_ad(is_verified_seller=False, images_qty=0)
    response = client.post('/predict_one', json=ad)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['is_violation'] is True

def test_is_violation_false(client: TestClient,
                            get_ad: Callable[..., dict[str, str|bool|int]],
                            ):
    ad = get_ad(is_verified_seller=True, images_qty=1)
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