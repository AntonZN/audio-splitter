import asyncio
import logging
from typing import Callable

import aio_pika
from aio_pika.abc import AbstractRobustConnection
from aio_pika.pool import Pool
from aiormq import exceptions

from core.config import get_settings

settings = get_settings()


async def run_consumer(loop, message_handler: Callable) -> None:
    connection_pool: Pool = Pool(get_connection, max_size=10, loop=loop)
    channel_pool: Pool = Pool(get_channel, connection_pool, max_size=10, loop=loop)
    queue_name = "tts"

    while True:
        try:
            tasks = []

            for _ in range(settings.CONSUMERS):
                tasks.append(
                    asyncio.create_task(
                        consume(channel_pool, queue_name, message_handler)
                    )
                )

            await asyncio.gather(*tasks)

        except exceptions.AMQPConnectionError as e:
            logging.error(f"Connection error: {e}")
            await asyncio.sleep(5)
        except Exception as e:
            logging.error(f"Unhandled error: {e}")
            break


async def get_connection() -> AbstractRobustConnection:
    return await aio_pika.connect_robust(
        host=settings.RABBITMQ_HOST,
        login=settings.RABBITMQ_USERNAME,
        password=settings.RABBITMQ_PASSWORD,
        timeout=60,
    )


async def get_channel(connection_pool) -> aio_pika.Channel:
    await asyncio.sleep(10)
    async with connection_pool.acquire() as connection:
        return await connection.channel()


async def consume(
    channel_pool: Pool, queue_name: str, message_handler: Callable
) -> None:
    while True:
        try:
            async with channel_pool.acquire() as channel:
                await channel.set_qos(1)
                exchange = await channel.declare_exchange(
                    "tts", aio_pika.ExchangeType.DIRECT
                )
                queue = await channel.declare_queue(
                    queue_name,
                    durable=True,
                    auto_delete=False,
                )

                await queue.bind(exchange, "tts")

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        task = asyncio.create_task(
                            message_handler(message.body.decode())
                        )
                        await message.ack()
                        await task

        except exceptions.AMQPError as e:
            logging.error(f"Error during consume: {e}")
            await asyncio.sleep(5)
