import aiofiles.os
from fastapi import HTTPException
from spleeter.audio import Codec
from starlette import status

from app.core.config import get_settings
from app.models.records import Record, Stem, StemType

settings = get_settings()


async def create_record(name: str, record_path: str):
    return await Record.create(name=name, file_path=record_path)


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


async def create_stems(record: Record, stems_count: int, codec: Codec):
    stem_types = [
        StemType.VOCAL,
        StemType.ACCOMPANIMENT,
        StemType.DRUMS,
        StemType.BASS,
        StemType.OTHER,
        StemType.PIANO,
    ]

    stems = []

    for i in range(stems_count):
        stem_type = stem_types[i]
        stem_name = f"{stem_type.value}.{codec.value}"
        file_path = f"{settings.STEMS_FOLDER}/{record.id}/{stem_name}"

        stem = Stem(
            record_id=record.id,
            name=stem_name,
            type=stem_type,
            file_path=file_path,
        )

        stems.append(stem)

    await Stem.bulk_create(stems)
