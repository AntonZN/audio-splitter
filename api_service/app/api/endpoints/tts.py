from typing import Optional

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.api.adapters import (
    create_tts,
    get_tts,
)
from app.api.logic import publish_text
from app.api.schemas import Lang, Speach, Speaker
from app.core.config import get_settings
from app.models.records import (
    TTSSchema,
)

settings = get_settings()
router = APIRouter()


@router.post(
    "/",
    response_model=TTSSchema,
    description=(
        "Преобразовать текст в голос. Максимум 270 символов. \n"
        "В ответ получите `id` по которому можно получить статус обработки\n"
        "Укажите `speaker` чтобы выбрать голос который будет использоваться\n"
        "Укажите `prompt_id` чтобы преобразовать текст в созданный голос, если задан этот параметр, то `lang` и `prompt_id` Не нужно указывать\n"
        "Укажите `deviceToken` для того чтобы отправить пуш уведомление пользователю о завершении обработки\n"
    ),
)
async def add_tts(
    text: str,
    lang: Lang = Lang.EN.value,
    speaker: Optional[Speaker] = None,
    prompt_id: Optional[str] = None,
    device_token: Optional[str] = None,
):
    if len(text) > 270:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Введен слишком длинный текст, ограничение 270 символов",
        )

    tts = await create_tts(text, device_token)

    await publish_text(str(tts.id), text, lang, speaker=speaker, prompt_id=prompt_id)

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
        url=f"{settings.MEDIA_URL}{tts.speech_path}" if tts.speech_path else None,
        status=tts.status.value,
        created=tts.created_at,
    )
