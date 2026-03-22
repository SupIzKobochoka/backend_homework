import pytest
from db_scripts.auth import AuthService


class FakeRepo:
    def __init__(self, account=None):
        self.account = account

    async def get_by_login_password(self, login: str, password: str):
        return self.account


def test_verify_token_ok():
    service = AuthService()
    token = service.create_token(7)
    assert service.verify_token(token) == 7


def test_verify_token_bad_token():
    service = AuthService()
    assert service.verify_token("bad-token") is None


@pytest.mark.asyncio
async def test_login_ok():
    service = AuthService()
    service.account_repo = FakeRepo({"id": 5, "is_blocked": False})
    token = await service.login("u", "p")
    assert token is not None
    assert service.verify_token(token) == 5


@pytest.mark.asyncio
async def test_login_blocked():
    service = AuthService()
    service.account_repo = FakeRepo({"id": 5, "is_blocked": True})
    token = await service.login("u", "p")
    assert token is None
