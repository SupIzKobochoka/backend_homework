import pytest
from fastapi import HTTPException
from starlette.requests import Request

from db_scripts.dependencies import get_current_account


class FakeAuthService:
    def __init__(self, account_id):
        self.account_id = account_id

    def verify_token(self, token: str):
        return self.account_id


class FakeRepo:
    def __init__(self, account):
        self.account = account

    async def get_by_id(self, account_id: int):
        return self.account


def _request_with_cookie(token: str | None) -> Request:
    headers = []
    if token is not None:
        headers = [(b"cookie", f"access_token={token}".encode())]
    scope = {"type": "http", "headers": headers}
    return Request(scope)


@pytest.mark.asyncio
async def test_get_current_account_ok():
    account = await get_current_account(
        _request_with_cookie("ok"),
        auth_service=FakeAuthService(10),
        account_repo=FakeRepo({"id": 10, "login": "u", "password": "x", "is_blocked": False}),
    )
    assert account.id == 10


@pytest.mark.asyncio
async def test_get_current_account_no_cookie():
    with pytest.raises(HTTPException) as e:
        await get_current_account(
            _request_with_cookie(None),
            auth_service=FakeAuthService(10),
            account_repo=FakeRepo({"id": 10, "login": "u", "password": "x", "is_blocked": False}),
        )
    assert e.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_account_blocked():
    with pytest.raises(HTTPException) as e:
        await get_current_account(
            _request_with_cookie("ok"),
            auth_service=FakeAuthService(10),
            account_repo=FakeRepo({"id": 10, "login": "u", "password": "x", "is_blocked": True}),
        )
    assert e.value.status_code == 401
