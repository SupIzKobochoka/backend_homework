import pytest
from unittest.mock import AsyncMock, patch
from workers.moderation_worker import main
import json


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,raise_error",
    [
        ("pending", False),
        ("pending", True),
    ],
)
async def test_worker(status, raise_error):
    fake_msg = AsyncMock()
    fake_msg.value = json.dumps({"item_id": 123}).encode()

    async def fake_iter():
        yield fake_msg

    fake_consumer = AsyncMock()
    fake_consumer.start = AsyncMock()
    fake_consumer.commit = AsyncMock()
    fake_consumer.stop = AsyncMock()
    fake_consumer.__aiter__ = lambda self=fake_consumer: fake_iter()

    fake_producer = AsyncMock()
    fake_producer.start = AsyncMock()
    fake_producer.send_dlq_request = AsyncMock()
    fake_producer.stop = AsyncMock()

    fake_ad_repo = AsyncMock()
    fake_ad_repo.get_ad.return_value = {"text": "ad"}

    fake_moderation_repo = AsyncMock()
    fake_moderation_repo.get_moderation_status.return_value = status
    fake_moderation_repo.check_and_update_task = AsyncMock()

    fake_model = AsyncMock()
    fake_pred = {"is_violation": False, "probability": 0.9}

    def fake_get_pred(*args, **kwargs):
        if raise_error:
            raise Exception("test error")
        return fake_pred

    fake_redis = AsyncMock()
    fake_redis.get = AsyncMock(return_value=None)
    fake_redis.set = AsyncMock(return_value=None)

    with patch("workers.moderation_worker.AIOKafkaConsumer", return_value=fake_consumer), \
         patch("workers.moderation_worker.get_kafka_producer", return_value=fake_producer), \
         patch("workers.moderation_worker.AdRepository", return_value=fake_ad_repo), \
         patch("workers.moderation_worker.ModerationRepository", return_value=fake_moderation_repo), \
         patch("workers.moderation_worker.load_or_train_model", return_value=fake_model), \
         patch("workers.moderation_worker.PredictRedisStorage", return_value=fake_redis), \
         patch("workers.moderation_worker.get_pred", side_effect=fake_get_pred):
        await main()

    if raise_error:
        fake_moderation_repo.check_and_update_task.assert_called_with(
            item_id=123,
            status="failed",
            error_message="test error",
        )
        fake_producer.send_dlq_request.assert_called_once()
        fake_consumer.commit.assert_called()
    else:
        fake_moderation_repo.check_and_update_task.assert_called_with(
            item_id=123,
            status="completed",
            is_violation=False,
            probability=0.9,
        )
        fake_consumer.commit.assert_called()