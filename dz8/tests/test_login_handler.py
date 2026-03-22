from fastapi.testclient import TestClient
from fastapi import status
from db_scripts.auth import AuthService


class FakeAuthOk:
    async def login(self, login: str, password: str):
        return "token123"


class FakeAuthFail:
    async def login(self, login: str, password: str):
        return None


def test_login_ok(client: TestClient):
    client.app.dependency_overrides[AuthService] = lambda: FakeAuthOk()
    response = client.post("/login", json={"login": "u", "password": "p"})
    client.app.dependency_overrides.pop(AuthService, None)

    assert response.status_code == status.HTTP_200_OK
    assert response.cookies.get("access_token") == "token123"


def test_login_bad_credentials(client: TestClient):
    client.app.dependency_overrides[AuthService] = lambda: FakeAuthFail()
    response = client.post("/login", json={"login": "u", "password": "p"})
    client.app.dependency_overrides.pop(AuthService, None)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
