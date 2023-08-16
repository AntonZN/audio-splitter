import asyncio
from typing import Callable

import aio_pika
from aio_pika.abc import AbstractRobustConnection
from aio_pika.pool import Pool

from core.config import get_settings

settings = get_settings()


async def run_consumer(loop, message_handler: Callable) -> None:
    connection_pool: Pool = Pool(get_connection, max_size=10, loop=loop)
    channel_pool: Pool = Pool(get_channel, connection_pool, max_size=10, loop=loop)
    queue_name = settings.RABBITMQ_ROUTING_KEY

    tasks = []

    for _ in range(settings.CONSUMERS):
        tasks.append(
            asyncio.create_task(consume(channel_pool, queue_name, message_handler))
        )

    for task in tasks:
        await task


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
    async with channel_pool.acquire() as channel:
        await channel.set_qos(1)
        try:
            exchange = await channel.get_exchange(settings.RABBITMQ_ROUTING_KEY, ensure=True)
        except Exception:
            exchange = await channel.declare_exchange(
                settings.RABBITMQ_ROUTING_KEY, aio_pika.ExchangeType.DIRECT
            )
        queue = await channel.declare_queue(
            queue_name,
            durable=True,
            auto_delete=False,
        )

        await queue.bind(exchange, settings.RABBITMQ_ROUTING_KEY)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await message_handler(message.body.decode())
                await message.ack()
