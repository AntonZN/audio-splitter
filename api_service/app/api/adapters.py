import aiofiles.os
from fastapi import HTTPException
from starlette import status

from app.core.config import get_settings
from app.models.records import Record, Stem, TTS, Prompt

settings = get_settings()


async def create_record(name: str, record_path: str, device_token: str = None):
    return await Record.create(
        name=name, file_path=record_path, device_token=device_token
    )


async def create_tts(text: str, device_token: str):
    return await TTS.create(text=text, device_token=device_token)


async def get_tts(tts_id: str):
    return await TTS.get_or_none(id=tts_id)


async def create_prompt(name: str, voice_path: str):
    return await Prompt.create(name=name, voice_path=voice_path)


async def delete_prompt(prompt_id: str):
    return await Prompt.filter(id=prompt_id).delete()


async def get_prompts():
    return await Prompt.filter(is_efficient=True)


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
