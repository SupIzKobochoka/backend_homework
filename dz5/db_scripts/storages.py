from client.postgres import get_pg_connection
from .queries import (GET_AD_QUERY,
                      ADD_MODERATION_QUERY,
                      UPDATE_MODERATION_AD_QUERY,
                      GET_MODERATION_TASK_FROM_ITEM_ID_QUERY,
                      GET_MODERATION_TASK_FROM_TASK_ID_QUERY
                      )
from utils import get_timestamp
from typing import Literal, Any

async def query_handler(query: str, 
                        *args: Any, 
                        kind: Literal['row', 'all'] = 'row') -> list:
    async with get_pg_connection() as connection:
        if kind == 'row':
            result = await connection.fetchrow(query, *args)
        else:
            result = await connection.fetch(query, *args)
    return result

class AdStorage:
    async def get_ad(self,
                     item_id: int
                 ) -> dict | None:
        ad = await query_handler(GET_AD_QUERY, item_id)
        if ad:
            return dict(ad)
        return None
        
class ModerationStorage:
    async def add_item(self, 
                       item_id: int,
                       status: str
                       ) -> int | None:
        task_id = await query_handler(ADD_MODERATION_QUERY, item_id, status)
        if task_id:
            return task_id['task_id']
        return None
        
    async def get_task_from_item_id(self, 
                                    item_id: int
                                    ) -> dict | None:
        task = await query_handler(GET_MODERATION_TASK_FROM_ITEM_ID_QUERY, item_id)
        if task:
            return dict(task)
        return None
    
    async def get_task_from_task_id(self, 
                                    task_id: int
                                    ) -> dict | None:
        task = await query_handler(GET_MODERATION_TASK_FROM_TASK_ID_QUERY, task_id)
        if task:
            return dict(task)
        return None
        

    async def update_item_id(self,
                            item_id: int,
                            status: str|None = None,
                            is_violation: bool|None = None,
                            probability: float|None = None,
                            error_message: str|None = None,
                            ) -> None:
        
        await query_handler(UPDATE_MODERATION_AD_QUERY, 
                            item_id,
                            status,
                            is_violation, 
                            probability,
                            error_message,
                            get_timestamp())
        

class AdRepository:
    ad_storage: AdStorage = AdStorage()

    async def get_ad(self, 
                     item_id: int
                     ) -> dict | None:
        return await self.ad_storage.get_ad(item_id)
    

class ModerationRepository:

    moderation_storage = ModerationStorage()
    ad_storage: AdStorage = AdStorage()

    async def check_and_add_item(self, 
                                 item_id: int
                                 ) -> int|None:
        '''
        -> task_id
        '''
        ad = await self.ad_storage.get_ad(item_id)
        if not ad:
            return None
        
        task = await self.moderation_storage.get_task_from_item_id(item_id)
        if task:
            return task['task_id']
    
        task_id = await self.moderation_storage.add_item(item_id, 'pending')
        return task_id
    
    async def get_task(self,
                       task_id: int
                       ) -> dict | None:
        response = await self.moderation_storage.get_task_from_task_id(task_id)
        if response:
            return response
        return  None
    
    async def check_and_update_task(self,
                                    item_id: int,
                                    status: str|None = None,
                                    is_violation: bool|None = None,
                                    probability: float|None = None,
                                    error_message: str|None = None,
                                    ) -> int|None:
        '''
        -> task_id
        '''
        task = await self.moderation_storage.get_task_from_item_id(item_id)
        if not task:
            return None
        await self.moderation_storage.update_item_id(item_id=item_id, 
                                                     status=status, 
                                                     is_violation=is_violation, 
                                                     probability=probability, 
                                                     error_message=error_message)
 
        return task['task_id']

    async def get_moderation_status(self,
                                    item_id: int
                                    ) -> str | None:
        task = await self.moderation_storage.get_task_from_item_id(item_id)
        if task:
            return task['status']
        return None