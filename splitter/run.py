import asyncio

from splitter.consumer import run_consumer
from splitter.handler import handle


async def main() -> None:
    loop = asyncio.get_event_loop()
    await run_consumer(loop, handle)


if __name__ == "__main__":
    asyncio.run(main())
