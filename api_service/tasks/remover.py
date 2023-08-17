import aiofiles.os

import arrow

from app.models.records import Stem, Record
from tasks.db import init_db


async def remove_files(files):
    for file in files:
        try:
            print(f"remove {file}")
            await aiofiles.os.remove(file)
        except FileNotFoundError:
            continue


async def remover():
    await init_db()
    async for record in await Record.filter(
        created_at__lte=str(arrow.utcnow().shift(hours=-24))
    ):
        stems_files = await Stem.filter(record=record).values_list(
            "file_path", flat=True
        )
        await remove_files(stems_files)
        await Stem.filter(record=record).delete()
        await record.delete()
