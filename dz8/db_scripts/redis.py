from client.redis import get_redis_connection, sync_get_redis_connection
from json import loads, dumps
from datetime import timedelta
import asyncio

# result = asyncio.run(my_async_func())

class PredictRedisStorage:
    _TTL: timedelta = timedelta(days=1)

    async def set(self, 
                  ad: dict, 
                  value: dict
                  ) -> None:
        async with get_redis_connection() as connection:
            ad = dumps(ad, sort_keys=True)
            pipeline = connection.pipeline()
            pipeline.set(
                name=ad,
                value=dumps(value),
            )
            pipeline.expire(ad, self._TTL)
            await pipeline.execute()
    
    async def get(self,
                  ad: dict
                  ) -> dict | None:
        ad = dumps(ad, sort_keys=True)
        async with get_redis_connection() as connection:
            value =await connection.get(ad)
            if value:
                return loads(value)
            return None
        
    async def delete(self, 
                     ad: dict
                     ) -> None:
        ad = dumps(ad, sort_keys=True)
        async with get_redis_connection() as connection:
            await connection.delete(ad)

class SyncPredictRedisStorage:
    _TTL: timedelta = timedelta(days=1)
    
    def set(self, 
            ad: dict, 
            value: dict
            ) -> None:
        with sync_get_redis_connection() as connection:
            ad = dumps(ad, sort_keys=True)
            pipeline = connection.pipeline()
            pipeline.set(name=ad,
                         value=dumps(value))
            pipeline.expire(ad, self._TTL)
            pipeline.execute()
    
    def get(self,
            ad: dict
            ) -> dict | None:
        ad = dumps(ad, sort_keys=True)
        with sync_get_redis_connection() as connection:
            value = connection.get(ad)
            if value:
                return loads(value)
            return None

    def delete(self, 
               ad: dict
              ) -> None:
        ad = dumps(ad, sort_keys=True)
        with sync_get_redis_connection() as connection:
            connection.delete(ad)