import os
from typing import Annotated, List, Optional
from uuid import uuid4

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
)

from app.api import responses
from app.api.adapters import (
    create_record,
    get_record,
    get_stems_for_record,
    delete_record,
)
from app.api.logic import publish_record
from app.api.schemas import Stem, Codec
from app.core.config import get_settings
from app.models.records import (
    RecordSchema,
    RecordStatusSchema,
    Stems,
)

settings = get_settings()
router = APIRouter()


@router.post(
    "/upload/",
    response_model=RecordSchema,
    description=(
        "Загрузка записи. Используйте `multipart/form-data`. "
        "В ответ получите `id` записи по которому можно получить статус и список дорожек"
    ),
)
async def upload_record(
    file: Annotated[UploadFile, File()],
    output_codec: Annotated[Codec, int, Form(alias="outputCodec")] = Codec.WAV.value,
    output_stems: Annotated[Stems, int, Form(alias="outputStems")] = Stems.TWO.value,
    device_token: Annotated[Optional[str], Form(alias="deviceToken")] = None,
):
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

    record_path = os.path.join(settings.UPLOAD_FOLDER, f"{uuid4()}_{file.filename}")

    with open(record_path, "wb") as f:
        f.write(file.file.read())

    record = await create_record(
        name=file.filename, record_path=record_path, device_token=device_token
    )

    await publish_record(str(record.id), output_codec, output_stems)

    return record


@router.get(
    "/{record_id}/",
    response_model=RecordStatusSchema,
    description="Получение информации о загруженной записи",
    responses={
        status.HTTP_404_NOT_FOUND: responses.HTTP_404_NOT_FOUND,
    },
)
async def record_status(record_id: str):
    record = await get_record(record_id)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )

    return record


@router.delete(
    "/{record_id}/",
    description="Используйте этот метод после того как загрузили все дорожки",
)
async def record_delete(record_id: str):
    await delete_record(record_id)


@router.get(
    "/{record_id}/stems/",
    response_model=List[Stem],
    description="Получить все дорожки после обработки записи",
    responses={
        status.HTTP_404_NOT_FOUND: responses.HTTP_404_NOT_FOUND,
    },
)
async def get_record_stems(record_id: str):
    stems = await get_stems_for_record(record_id)

    return [
        Stem(
            id=stem.id,
            name=stem.name,
            type=stem.type,
            url=f"{settings.MEDIA_URL}{stem.file_path}",
            created=stem.created_at,
        )
        for stem in stems
    ]
