import json

import aio_pika
from aio_pika import DeliveryMode, Message, connect
from loguru import logger

from app.api.schemas import Codec

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
        f"amqp://{settings.RABBITMQ_USERNAME}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}/"
    )

    async with connection:
        channel = await connection.channel()

        try:
            exchange = await channel.get_exchange(settings.RABBITMQ_ROUTING_KEY, ensure=True)
        except Exception:
            exchange = await channel.declare_exchange(
                settings.RABBITMQ_ROUTING_KEY, aio_pika.ExchangeType.DIRECT
            )

        await exchange.publish(message, routing_key=settings.RABBITMQ_ROUTING_KEY)
