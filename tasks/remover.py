import aiofiles.os

import arrow
from app.core.config import get_settings

from app.models.records import Stem
from tasks.db import init_db


settings = get_settings()
STREAM_FOLDER = "/stream"
STORAGE_FOLDER = "/storage"


async def remove_files(files):
    for file in files:
        try:
            print(f"remove {file}")
            await aiofiles.os.remove(file)
        except FileNotFoundError:
            continue


async def remover():
    await init_db()

    files = await Stem.filter(
        created_at__lte=str(arrow.utcnow().shift(hours=-2))
    ).values_list("file_path", flat=True)

    await remove_files(files)
