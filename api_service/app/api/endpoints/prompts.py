import os
from typing import Annotated, List
from uuid import uuid4

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
)

from app.api.adapters import (
    create_prompt,
    get_prompts,
    delete_prompt,
)
from app.api.logic import publish_prompt
from app.api.schemas import PromptForList
from app.core.config import get_settings
from app.models.records import (
    PromptSchema,
)

settings = get_settings()
router = APIRouter()


@router.get(
    "/",
    response_model=List[PromptForList],
    description="Список готовых моделей для TTS",
)
async def prompts_list():
    return [
        PromptForList(
            id=str(prompt.id),
            name=prompt.name,
            created=prompt.created_at,
        )
        for prompt in await get_prompts()
    ]


@router.post(
    "/",
    response_model=PromptSchema,
    description="Создать модель для клонирования голоса",
)
async def prompt_create(
    file: Annotated[UploadFile, File()],
    name: Annotated[str, Form()],
):
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

    voice_path = os.path.join(settings.UPLOAD_FOLDER, f"{uuid4()}_{file.filename}")

    with open(voice_path, "wb") as f:
        f.write(file.file.read())

    prompt = await create_prompt(name, voice_path)
    await publish_prompt(str(prompt.id))

    return prompt


@router.delete(
    "/{prompt_id}/",
    description="Удалить модель для клонирования голоса",
)
async def prompt_delete(prompt_id: str):
    prompt = await delete_prompt(prompt_id)

    return prompt
