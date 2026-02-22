from client.postgres import get_pg_connection
from .queries import (GET_AD_QUERY,
                      CHECK_MODERATION_QUERY,
                      ADD_MODERATION_QUERY,
                      CHECK_ADS_QUERY,
                      GET_MODERATION_AD_QUERY,
                      UPDATE_MODERATION_AD_QUERY,
                      GET_MODERATION_STATUS_QUERY
                      )
from utils import get_timestamp
from .services import async_log_db_calls
from typing import Literal, Any

async def query_handler(query: str, 
                        *args: list[Any], 
                        kind: Literal['row', 'all'] = 'row') -> list:
    async with get_pg_connection() as connection:
        if kind == 'row':
            result = await connection.fetchrow(query, *args)
        else:
            result = await connection.fetch(query, *args)
    return result

class DBProvider:
    @async_log_db_calls
    async def get_ad(self,
                     item_id: int
                 ) -> dict:
        ad = await query_handler(GET_AD_QUERY, item_id)
        return dict(ad) if ad is not None else None
    
    @async_log_db_calls
    async def check_and_add_moderation(self,
                                       item_id: int
                                       ) -> tuple[bool, int|None]:
        '''
        -> [item_id_exist, task_id]
        '''
        ads_exist = await query_handler(CHECK_ADS_QUERY, item_id) is not None

        if not ads_exist:
            return False, None
        
        task_id = await query_handler(CHECK_MODERATION_QUERY, item_id)
        if task_id is None:
            task_id = await query_handler(ADD_MODERATION_QUERY, 
                                          item_id, 'pending' # item_id status
                                          )
            
        return True, task_id['task_id']
    
    @async_log_db_calls
    async def get_ad_from_moderation(self,
                                     task_id: int
                                     ) -> dict:
        response = await query_handler(GET_MODERATION_AD_QUERY, task_id)
        return dict(response) if response is not None else None
    
    @async_log_db_calls
    async def check_and_update_moderation(self,
                                          item_id: int,
                                          status: str|None = None,
                                          is_violation: bool|None = None,
                                          probability: float|None = None,
                                          error_message: str|None = None,
                                          ) -> tuple[bool, int|None]:
        '''
        -> [item_id_exist, task_id]
        '''
        response = await query_handler(UPDATE_MODERATION_AD_QUERY, 
                                       item_id, 
                                       status, 
                                       is_violation, 
                                       probability, 
                                       error_message, 
                                       get_timestamp())

        if response is None:
            return False, None
        return True, response['task_id']
    
    @async_log_db_calls
    async def get_moderation_status(self,
                                    item_id: int
                                    ) -> str:
        response = await query_handler(GET_MODERATION_STATUS_QUERY, item_id)
        return response['status']
    
def get_db_provider() -> DBProvider:
    return DBProvider()