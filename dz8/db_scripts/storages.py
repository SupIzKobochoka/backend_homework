from client.postgres import get_pg_connection
from .queries import (
    GET_AD_QUERY,
    ADD_MODERATION_QUERY,
    UPDATE_MODERATION_AD_QUERY,
    GET_MODERATION_TASK_FROM_ITEM_ID_QUERY,
    GET_MODERATION_TASK_FROM_TASK_ID_QUERY,
    DELETE_AD_QUERY,
    ADD_AD_QUERY,
    CREATE_ACCOUNT_QUERY,
    GET_ACCOUNT_BY_ID_QUERY,
    DELETE_ACCOUNT_QUERY,
    BLOCK_ACCOUNT_QUERY,
    GET_ACCOUNT_BY_LOGIN_PASSWORD_QUERY,
    DELETE_MODERATION_BY_ITEM_ID_QUERY,
)
from utils import get_timestamp
from typing import Literal, Any
import time
import hashlib
from metrics import DB_QUERY_DURATION_SECONDS


def hash_password(password: str) -> str:
    return hashlib.md5(password.encode("utf-8")).hexdigest()


async def query_handler(query: str, *args: Any, kind: Literal["row", "all"] = "row") -> list:
    query_type = "select"
    q = query[7:].lstrip().lower()
    if q.startswith("select"):
        query_type = "select"
    elif q.startswith("insert"):
        query_type = "insert"
    elif q.startswith("update"):
        query_type = "update"
    elif q.startswith("delete"):
        query_type = "delete"

    start = time.perf_counter()
    async with get_pg_connection() as connection:
        try:
            if kind == "row":
                result = await connection.fetchrow(query, *args)
            else:
                result = await connection.fetch(query, *args)
            return result
        finally:
            DB_QUERY_DURATION_SECONDS.labels(query_type=query_type).observe(time.perf_counter() - start)


class AdStorage:
    async def get_ad(self, item_id: int) -> dict | None:
        ad = await query_handler(GET_AD_QUERY, item_id)
        if ad:
            return dict(ad)
        return None

    async def add_ad(
        self,
        seller_id: int,
        item_id: int,
        name: str,
        description: str,
        category: int,
        images_qty: int,
    ) -> int:
        ad_id = await query_handler(ADD_AD_QUERY, seller_id, item_id, name, description, category, images_qty)
        return ad_id

    async def delete_ad(self, item_id: int) -> None:
        await query_handler(DELETE_AD_QUERY, item_id)


class ModerationStorage:
    async def add_item(self, item_id: int, status: str) -> int | None:
        task_id = await query_handler(ADD_MODERATION_QUERY, item_id, status)
        if task_id:
            return task_id["task_id"]
        return None

    async def get_task_from_item_id(self, item_id: int) -> dict | None:
        task = await query_handler(GET_MODERATION_TASK_FROM_ITEM_ID_QUERY, item_id)
        if task:
            return dict(task)
        return None

    async def get_task_from_task_id(self, task_id: int) -> dict | None:
        task = await query_handler(GET_MODERATION_TASK_FROM_TASK_ID_QUERY, task_id)
        if task:
            return dict(task)
        return None

    async def update_item_id(
        self,
        item_id: int,
        status: str | None = None,
        is_violation: bool | None = None,
        probability: float | None = None,
        error_message: str | None = None,
    ) -> None:
        await query_handler(
            UPDATE_MODERATION_AD_QUERY,
            item_id,
            status,
            is_violation,
            probability,
            error_message,
            get_timestamp(),
        )

    async def delete_by_item_id(self, item_id: int) -> None:
        await query_handler(DELETE_MODERATION_BY_ITEM_ID_QUERY, item_id)


class AccountStorage:
    async def create_account(self, login: str, password: str) -> dict | None:
        account = await query_handler(CREATE_ACCOUNT_QUERY, login, hash_password(password))
        return dict(account) if account else None

    async def get_account_by_id(self, account_id: int) -> dict | None:
        account = await query_handler(GET_ACCOUNT_BY_ID_QUERY, account_id)
        return dict(account) if account else None

    async def delete_account(self, account_id: int) -> None:
        await query_handler(DELETE_ACCOUNT_QUERY, account_id)

    async def block_account(self, account_id: int) -> None:
        await query_handler(BLOCK_ACCOUNT_QUERY, account_id)

    async def get_by_login_password(self, login: str, password: str) -> dict | None:
        account = await query_handler(GET_ACCOUNT_BY_LOGIN_PASSWORD_QUERY, login, hash_password(password))
        return dict(account) if account else None


class AdRepository:
    ad_storage: AdStorage = AdStorage()

    async def get_ad(self, item_id: int) -> dict | None:
        return await self.ad_storage.get_ad(item_id)

    async def add_ad(
        self,
        seller_id: int,
        item_id: int,
        name: str,
        description: str,
        category: int,
        images_qty: int,
    ) -> int:
        return await self.ad_storage.add_ad(seller_id, item_id, name, description, category, images_qty)

    async def delete_ad(self, item_id: int) -> None:
        await self.ad_storage.delete_ad(item_id)


class ModerationRepository:
    moderation_storage = ModerationStorage()
    ad_storage: AdStorage = AdStorage()

    async def check_and_add_item(self, item_id: int) -> int | None:
        ad = await self.ad_storage.get_ad(item_id)
        if not ad:
            return None

        task = await self.moderation_storage.get_task_from_item_id(item_id)
        if task:
            return task["task_id"]

        task_id = await self.moderation_storage.add_item(item_id, "pending")
        return task_id

    async def get_task(self, task_id: int) -> dict | None:
        response = await self.moderation_storage.get_task_from_task_id(task_id)
        if response:
            return response
        return None

    async def check_and_update_task(
        self,
        item_id: int,
        status: str | None = None,
        is_violation: bool | None = None,
        probability: float | None = None,
        error_message: str | None = None,
    ) -> int | None:
        task = await self.moderation_storage.get_task_from_item_id(item_id)
        if not task:
            return None
        await self.moderation_storage.update_item_id(
            item_id=item_id,
            status=status,
            is_violation=is_violation,
            probability=probability,
            error_message=error_message,
        )
        return task["task_id"]

    async def get_moderation_status(self, item_id: int) -> str | None:
        task = await self.moderation_storage.get_task_from_item_id(item_id)
        if task:
            return task["status"]
        return None

    async def delete_by_item_id(self, item_id: int) -> None:
        await self.moderation_storage.delete_by_item_id(item_id)


class AccountRepository:
    account_storage: AccountStorage = AccountStorage()

    async def create(self, login: str, password: str) -> int | None:
        account = await self.account_storage.create_account(login, password)
        return account["id"] if account else None

    async def get_by_id(self, account_id: int) -> dict | None:
        return await self.account_storage.get_account_by_id(account_id)

    async def delete(self, account_id: int) -> None:
        await self.account_storage.delete_account(account_id)

    async def block(self, account_id: int) -> None:
        await self.account_storage.block_account(account_id)

    async def get_by_login_password(self, login: str, password: str) -> dict | None:
        return await self.account_storage.get_by_login_password(login, password)
