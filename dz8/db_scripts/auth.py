from datetime import datetime, timedelta, timezone
import jwt
from db_scripts.storages import AccountRepository

JWT_SECRET = "super-secret"
JWT_ALGO = "HS256"
JWT_TTL_MINUTES = 60


class AuthService:
    account_repo: AccountRepository = AccountRepository()

    async def login(self, login: str, password: str) -> str | None:
        account = await self.account_repo.get_by_login_password(login, password)
        if not account or account["is_blocked"]:
            return None
        return self.create_token(account["id"])

    def create_token(self, account_id: int) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=JWT_TTL_MINUTES)
        payload = {"sub": account_id, "exp": expires_at}
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

    def verify_token(self, token: str) -> int | None:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
            return int(payload.get("sub"))
        except (jwt.InvalidTokenError, ValueError, TypeError):
            return None
