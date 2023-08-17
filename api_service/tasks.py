import argparse
import aiofiles.os

import arrow

from tortoise import run_async
from tortoise import Tortoise

from app.core.config import get_settings
from app.models.records import Stem, Record

settings = get_settings()


async def init_db():
    await Tortoise.init(
        db_url=settings.DATABASE_URI,
        modules={"models": settings.MODELS},
    )


async def remove_files(files):
    for file in files:
        try:
            print(f"remove {file}")
            await aiofiles.os.remove(file)
        except FileNotFoundError:
            continue


async def remover():
    await init_db()
    async for record in Record.filter(
        created_at__lte=str(arrow.utcnow().shift(hours=-24))
    ):
        stems_files = await Stem.filter(record=record).values_list(
            "file_path", flat=True
        )
        await remove_files(stems_files)
        await Stem.filter(record=record).delete()
        await record.delete()


TASKS = {
    "remover": remover,
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spitter tasks")
    parser.add_argument("task", type=str, help="Input task name")
    args = parser.parse_args()
    task = TASKS.get(args.task)

    if task:
        run_async(task())
    else:
        raise ValueError(
            f'Unknown task name: {args.task}. Available tasks are {", ".join(TASKS)}'
        )
