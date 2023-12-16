import json

import aio_pika
from aio_pika import DeliveryMode, Message, connect
from loguru import logger

from app.api.schemas import Codec, Lang

from app.core.config import get_settings

settings = get_settings()


async def publish(message: Message, key=None):
    logger.debug(f"Publishing message to motions: {message.body}")

    connection = await connect(
        f"amqp://{settings.RABBITMQ_USERNAME}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}/"
    )

    async with connection:
        channel = await connection.channel()

        try:
            exchange = await channel.get_exchange(key, ensure=True)
        except Exception:
            exchange = await channel.declare_exchange(key, aio_pika.ExchangeType.DIRECT)

        await exchange.publish(message, routing_key=key)


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
    await publish(message, key=settings.RABBITMQ_ROUTING_KEY)


async def publish_text(tts_id: str, text: str, lang: Lang, prompt_id=None):
    message_data = {
        "topic": "tts",
        "tts_id": tts_id,
        "text": text,
        "lang": lang.value,
        "prompt_id": prompt_id,
    }

    message_body = json.dumps(message_data).encode()
    message = Message(
        message_body,
        delivery_mode=DeliveryMode.PERSISTENT,
    )

    await publish(message, key=settings.RABBITMQ_ROUTING_KEY_TTS)


async def publish_prompt(prompt_id):
    message_data = {
        "topic": "clone",
        "prompt_id": prompt_id,
    }

    message_body = json.dumps(message_data).encode()
    message = Message(
        message_body,
        delivery_mode=DeliveryMode.PERSISTENT,
    )

    await publish(message, key=settings.RABBITMQ_ROUTING_KEY_TTS)
