import json
import time
from aiokafka import AIOKafkaProducer
from utils import get_timestamp

class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self._bootstrap = bootstrap_servers
        self._producer = None  # AIOKafkaProducer

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(bootstrap_servers=self._bootstrap)
        await self._producer.start()

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()
    
    async def send_moderation_request(self, 
                                      item_id : int
                                      ) -> dict:
        '''
        -> {'task_id': ..., 'timestamp': ...}
        '''
        assert self._producer is not None
        data = {'item_id': item_id , 'timestamp': get_timestamp()}
        data_json = json.dumps(data).encode("utf-8")
        await self._producer.send_and_wait('moderation', data_json)
        return data

    async def send_retry_request(self, item_id: int, retry_count: int) -> None:
        assert self._producer is not None
        data = {"item_id": item_id, "retry_count": retry_count, "timestamp": get_timestamp()}
        data_json = json.dumps(data).encode("utf-8")
        await self._producer.send_and_wait("moderation", data_json)
    
    async def send_dlq_request(self, 
                               data: dict
                               ) -> None:
        assert self._producer is not None
        data_json = json.dumps(data).encode("utf-8")
        await self._producer.send_and_wait('moderation.dlq', data_json)
    
def get_kafka_producer():
    return KafkaProducer(bootstrap_servers='localhost:9092')
