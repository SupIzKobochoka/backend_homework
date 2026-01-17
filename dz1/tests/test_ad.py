import pytest
from model_ad import Ad
from fastapi.testclient import TestClient
from typing import Callable, Any
from fastapi import status


@pytest.mark.parametrize('is_verified_seller', [True])
def test_verified(is_verified_seller: bool,
                  get_ad: Callable[..., dict[str, str|bool|int]],
                  client: TestClient,
                  ):
    ad = get_ad(is_verified_seller=is_verified_seller)
    response = client.post(url='/predict',
                            json=ad)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == True


@pytest.mark.parametrize('images_qty', [1, 2, 3, 4, 9999])
@pytest.mark.parametrize('is_verified_seller', [False])
def test_have_images(images_qty: int,
                     is_verified_seller: bool,
                     get_ad: Callable[..., dict[str, str|bool|int]],
                     client: TestClient,
                     ):
    ad = get_ad(images_qty=images_qty,
                is_verified_seller=is_verified_seller)
    response = client.post(url='/predict',
                           json=ad)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == True


@pytest.mark.parametrize('images_qty', [0])
@pytest.mark.parametrize('is_verified_seller', [False])
def test_havent_images(images_qty: int,
                       is_verified_seller: bool,
                       get_ad: Callable[..., dict[str, str|bool|int]],
                       client: TestClient,
                       ):
    ad = get_ad(images_qty=images_qty,
                is_verified_seller=is_verified_seller)
    response = client.post(url='/predict',
                           json=ad)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == False



@pytest.mark.parametrize('field,value', [['images_qty', 'TWO'],
                                         ['is_verified_seller', 'YES'],
                                         ['category', 32],
                                         ['images_qty', 'TWO']]
                        )
def test_wrong_types(field: str,
                     value: Any,
                     get_ad: Callable[..., dict[str, str|bool|int]],
                     client: TestClient,
                    ):
    ad = get_ad(**{field: value})
    response = client.post(url='/predict',
                            json=ad)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize('field,value', [['seller_id', -1],
                                         ['item_id', -2],
                                         ['images_qty', -4]]
                        )
def test_wrong_values(field: str,
                      value: Any,
                      get_ad: Callable[..., dict[str, str|bool|int]],
                      client: TestClient,
                      ):
    ad = get_ad(**{field: value})
    response = client.post(url='/predict',
                            json=ad)
    assert response.status_code == status.HTTP_400_BAD_REQUEST