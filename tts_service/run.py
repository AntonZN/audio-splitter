import asyncio
from tortoise import Tortoise
from consumer import run_consumer
from handler import handle
from core.config import get_settings
from loguru import logger

settings = get_settings()


async def main() -> None:
    loop = asyncio.get_event_loop()
    await Tortoise.init(db_url=settings.DATABASE_URI, modules={"models": ["models"]})
    logger.debug("DB init")

    await run_consumer(loop, handle)


if __name__ == "__main__":
    asyncio.run(main())
