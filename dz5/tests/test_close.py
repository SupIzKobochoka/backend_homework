import pytest
from fastapi.testclient import TestClient
from fastapi import status
from typing import Any
from conftest import BASE_AD


@pytest.mark.parametrize("item_id", [1, 2, 3])
def test_close_ok(item_id: int,
                  client: TestClient,
                  set_fake_ad_repo_for_close,
                  set_fake_redis_storage):
    response = client.post("/close", params={"item_id": item_id})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "closed", "item_id": item_id}
    assert set_fake_redis_storage.deleted_ad is not None
    assert set_fake_redis_storage.deleted_ad["item_id"] == BASE_AD["item_id"]
    assert set_fake_ad_repo_for_close.deleted_item_id == item_id


@pytest.mark.parametrize("item_id", [1, 2, 3])
def test_close_not_found(item_id: int,
                         client: TestClient,
                         set_fake_ad_repo_for_close_none,
                         set_fake_redis_storage):
    response = client.post("/close", params={"item_id": item_id})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert set_fake_redis_storage.deleted_ad is None


@pytest.mark.parametrize("item_id", [True, "One", 31.1])
def test_wrong_types_close(item_id: Any,
                           client: TestClient):
    response = client.post("/close", params={"item_id": item_id})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT