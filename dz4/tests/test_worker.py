import pytest
from unittest.mock import AsyncMock, patch
from workers.moderation_worker import main
import json

@pytest.mark.asyncio
@pytest.mark.parametrize("status,raise_error", 
                         [('pending', False),
                          ('pending', True),
                          ])
async def test_worker(status, raise_error):
    fake_msg = AsyncMock()
    fake_msg.value = json.dumps({"item_id": 123}).encode()

    async def fake_iter():
        yield fake_msg

    fake_consumer = AsyncMock()
    fake_consumer.start = AsyncMock()
    fake_consumer.commit = AsyncMock()
    fake_consumer.stop = AsyncMock()
    fake_consumer.__aiter__ = lambda self=fake_consumer: fake_iter() # Бот подсказал

    fake_producer = AsyncMock()
    fake_producer.send_dlq_request = AsyncMock()
    fake_producer.stop = AsyncMock()

    fake_db = AsyncMock()
    fake_db.get_moderation_status.return_value = status
    fake_db.get_ad.return_value = {"text": "ad"}
    fake_db.check_and_update_moderation = AsyncMock()

    fake_model = AsyncMock()
    fake_pred = {'is_violation': False, 'probability': 0.9}

    def fake_get_pred(model, ad):
        if raise_error:
            raise Exception()
        return fake_pred

    with patch('workers.moderation_worker.get_db_provider', return_value=fake_db), \
         patch('workers.moderation_worker.AIOKafkaConsumer', return_value=fake_consumer), \
         patch('workers.moderation_worker.get_kafka_producer', return_value=fake_producer), \
         patch('workers.moderation_worker.load_or_train_model', return_value=fake_model), \
         patch('workers.moderation_worker.get_pred', side_effect=fake_get_pred):
        await main()

    if raise_error:
        fake_db.check_and_update_moderation.assert_called_with(item_id=123, 
                                                               status='failed', 
                                                               error_message='test error'
                                                               )
        fake_producer.send_dlq_request.assert_called_once()
    else:
        fake_db.check_and_update_moderation.assert_called_with(item_id=123,
                                                               status='completed',
                                                               is_violation=False,probability=0.9
                                                               )
        fake_consumer.commit.assert_called()
