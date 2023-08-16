import aiofiles.os
from fastapi import HTTPException
from app.api.schemas import Codec
from starlette import status

from app.core.config import get_settings
from app.models.records import Record, Stem, StemType

settings = get_settings()


async def create_record(name: str, record_path: str, device_token: str = None):
    return await Record.create(
        name=name, file_path=record_path, device_token=device_token
    )


async def get_record(record_id: str):
    return await Record.get_or_none(id=record_id)


async def delete_record(record_id: str):
    stems_files = await Stem.filter(record_id=record_id).values_list(
        "file_path", flat=True
    )

    for file in stems_files:
        try:
            await aiofiles.os.remove(file)
        except FileNotFoundError:
            continue

    await Record.filter(id=record_id).delete()
    await Stem.filter(record_id=record_id).delete()


async def get_stems_for_record(record_id: str):
    record = await Record.get_or_none(id=record_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )

    return await record.stems
