from fastapi import Depends, HTTPException, Request
from db_scripts.auth import AuthService
from db_scripts.storages import AccountRepository
from schemas.account import Account


async def get_current_account(
    request: Request,
    auth_service: AuthService = Depends(),
    account_repo: AccountRepository = Depends(),
) -> Account:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, detail="Unauthorized")

    account_id = auth_service.verify_token(token)
    if account_id is None:
        raise HTTPException(401, detail="Unauthorized")

    account = await account_repo.get_by_id(account_id)
    if not account or account["is_blocked"]:
        raise HTTPException(401, detail="Unauthorized")

    return Account(**account)
