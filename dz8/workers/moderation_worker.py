import asyncio
import json
import os
from aiokafka import AIOKafkaConsumer

from utils import logger
from model import get_pred, load_or_train_model
from db_scripts.storages import AdRepository, ModerationRepository
from client.kafka import get_kafka_producer
from db_scripts.redis import PredictRedisStorage


async def main():
    ad_repo = AdRepository()
    moderation_repo = ModerationRepository()

    consumer = AIOKafkaConsumer(
        "moderation",
        bootstrap_servers="localhost:9092",
        group_id="moderation-group",
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )

    dlq = get_kafka_producer()
    predict_redis_storage = PredictRedisStorage() 

    await consumer.start()
    await dlq.start()
    logger.info("kafka consumer started (moderation)")

    model = load_or_train_model()
    max_retries = int(os.getenv("KAFKA_MAX_RETRIES", "3"))

    try:
        async for msg in consumer:
            item_id = None
            try:
                payload = json.loads(msg.value.decode("utf-8"))
                item_id = payload["item_id"]
                retry_count = int(payload.get("retry_count", 0))

                status = await moderation_repo.get_moderation_status(item_id)
                if status is None:
                    raise RuntimeError(f"item_id={item_id} not found in moderation table")

                if status != "pending":
                    await consumer.commit()
                    continue

                ad = await ad_repo.get_ad(item_id)
                if ad is None:
                    raise RuntimeError(f"item_id={item_id} not found in ads table")

                redis_response = await predict_redis_storage.get(ad)
                if redis_response:
                    response = redis_response
                else:
                    response = get_pred(model=model, ad=ad)
                    await predict_redis_storage.set(ad, response)

                await moderation_repo.check_and_update_task(
                    item_id=item_id,
                    status="completed",
                    is_violation=response["is_violation"],
                    probability=response["probability"],
                )

                await consumer.commit()

            except Exception as e:
                logger.error(f"error in moderation consumer: {e}")

                if item_id is not None:
                    await moderation_repo.check_and_update_task(
                        item_id=item_id,
                        status="failed",
                        error_message=str(e),
                    )
                    if retry_count < max_retries:
                        await dlq.send_retry_request(item_id=item_id, retry_count=retry_count + 1)
                    else:
                        dlq_payload = {
                            "error": str(e),
                            "topic": "moderation",
                            "group_id": "moderation-group",
                            "original": msg.value.decode("utf-8", errors="replace"),
                        }
                        await dlq.send_dlq_request(dlq_payload)
                else:
                    dlq_payload = {
                        "error": str(e),
                        "topic": "moderation",
                        "group_id": "moderation-group",
                        "original": msg.value.decode("utf-8", errors="replace"),
                    }
                    await dlq.send_dlq_request(dlq_payload)

                await consumer.commit()

    finally:
        await dlq.stop()
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
