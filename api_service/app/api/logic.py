import json

from aio_pika import DeliveryMode, Message, connect
from loguru import logger

from spleeter.audio import Codec

from app.core.config import get_settings

settings = get_settings()


async def publish_record(record_id: str, codec: Codec, count_stems: int):
    message_data = {
        "topic": "split",
        "record_id": record_id,
        "codec": codec.value,
        "count_stems": count_stems,
    }

    message_body = json.dumps(message_data).encode()
    message = Message(
        message_body,
        delivery_mode=DeliveryMode.PERSISTENT,
    )

    logger.debug(f"Publishing message to motions: {message_body}")

    connection = await connect(
        f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}/"
    )

    async with connection:
        channel = await connection.channel()
        exchange = await channel.get_exchange(
            settings.RABBITMQ_ROUTING_KEY, ensure=True
        )
        await exchange.publish(message, routing_key=settings.RABBITMQ_ROUTING_KEY)
