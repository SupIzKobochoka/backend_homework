import asyncio
import json
from aiokafka import AIOKafkaConsumer

from utils import logger
from model import get_pred, load_or_train_model
from db_scripts.db_access import get_db_provider
from fastapi import HTTPException
from client.kafka import get_kafka_producer

async def main():
    db_provider = get_db_provider()
    consumer = AIOKafkaConsumer('moderation',
                                bootstrap_servers='localhost:9092',
                                group_id='moderation-group',
                                enable_auto_commit=False,  # commit only after successful handling
                                auto_offset_reset="earliest")
    
    dlq = get_kafka_producer()
    await consumer.start()
    logger.info(f'kafka consumer started (moderation)')
    model = load_or_train_model()
    try:
        async for msg in consumer:
            try:
                item_id = json.loads(msg.value.decode("utf-8"))['item_id']
                status = await db_provider.get_moderation_status(item_id)
                if status is None:
                    raise HTTPException(404, detail=f'item_id from kafka dosnt found in moderation db')
                if status == 'pending':
                    ad = await db_provider.get_ad(item_id)
                    response = get_pred(model, ad) # {'is_violation': target, 'probability': proba}
                    await db_provider.check_and_update_moderation(item_id=item_id,
                                                                  status='completed',
                                                                  is_violation=response['is_violation'],
                                                                  probability=response['probability'])
                    await consumer.commit()
                    
            except Exception as e:
                payload = {"error": str(e),
                           "topic": 'moderation-group',
                           "original": msg.value.decode("utf-8", errors="replace")}
                logger.error(f'error in moderation consumer: {e}')
                await db_provider.check_and_update_moderation(item_id=item_id,
                                                              status='failed',
                                                              error_message=str(e)
                                                              )

                await dlq.send_dlq_request(payload)
                await consumer.commit()
    finally:
        await dlq.stop()
        await consumer.stop()
        
if __name__ == "__main__":
    asyncio.run(main())
