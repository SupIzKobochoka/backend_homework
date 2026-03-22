import pytest
import asyncpg
from uuid import uuid4

from db_scripts.storages import AccountRepository


async def _pg_available() -> bool:
    try:
        conn = await asyncpg.connect(database="hw", user="postgres", password="postgres", host="127.0.0.1", port=5435)
        await conn.close()
        return True
    except Exception:
        return False


@pytest.mark.integration
@pytest.mark.asyncio
async def test_account_repo_crud_and_block():
    if not await _pg_available():
        pytest.skip("Postgres is not available")

    repo = AccountRepository()
    login = f"u_{uuid4().hex[:8]}"
    password = "pass123"

    account_id = await repo.create(login, password)
    assert account_id is not None

    account = await repo.get_by_id(account_id)
    assert account is not None
    assert account["login"] == login
    assert account["is_blocked"] is False
    assert account["password"] != password

    by_creds = await repo.get_by_login_password(login, password)
    assert by_creds is not None
    assert by_creds["id"] == account_id

    await repo.block(account_id)
    blocked = await repo.get_by_id(account_id)
    assert blocked["is_blocked"] is True

    await repo.delete(account_id)
    deleted = await repo.get_by_id(account_id)
    assert deleted is None
