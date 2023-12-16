import os
from typing import Optional, Annotated, List
from uuid import uuid4

from fastapi import (
    APIRouter,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
)

from app.api.adapters import (
    create_tts,
    get_tts,
    create_prompt,
    get_prompts,
    delete_prompt,
)
from app.api.logic import publish_text, publish_prompt
from app.api.schemas import Lang, Speach, PromptForList
from app.core.config import get_settings
from app.models.records import (
    TTSSchema,
    PromptSchema,
)

settings = get_settings()
router = APIRouter()


@router.post(
    "/",
    response_model=TTSSchema,
    description=(
        "Преобразовать текст в голос. Максимум 270 символов."
        "В ответ получите `id` по которому можно получить статус обработки"
        "Укажите `deviceToken` для того чтобы отправить пуш уведомление пользователю о завершении обработки"
    ),
)
async def add_tts(
    text: str, lang: Lang = Lang.EN.value, device_token: Optional[str] = None
):
    if len(text) > 270:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Введен слишком длинный текст, ограничение 270 символов",
        )

    tts = await create_tts(text, device_token)

    await publish_text(str(tts.id), text, lang)

    return tts


@router.get(
    "/{tts_id}/",
    response_model=Speach,
    description="Статус обработки преобразования текста в речь",
)
async def get_tts_info(tts_id: str):
    tts = await get_tts(tts_id)

    if not tts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Обработка не найдена"
        )

    return Speach(
        id=tts.id,
        url=f"{settings.MEDIA_URL}{tts.speech_path}",
        status=tts.status.value,
        created=tts.created_at,
    )
