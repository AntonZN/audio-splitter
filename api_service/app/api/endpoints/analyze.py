import os
from typing import Annotated, Literal, Optional
from uuid import uuid4
import httpx
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
)

from pydantic import BaseModel, Field
from typing import List

from app.api.analyze_fn import analyze_audio
from app.core.config import get_settings

from app.api.schemas import BeatNetResult

from app.api.analyze_fn import analyze_with_beatnet_offline

settings = get_settings()
router = APIRouter()


class AudioAnalysisResult(BaseModel):
    bpm: Optional[float] = Field(None, description="Оцененный темп трека в BPM")
    beats: List[float] = Field(None, description="Таймкоды битов в секундах")
    key: Optional[str] = Field(None, description="Тональность, например 'G'")
    scale: Optional[str] = Field(None, description="Лад: 'major' или 'minor'")
    onsetsSec: Optional[List[float]] = Field(
        None,
        description="Таймкоды онсетов (атак) в секундах",
    )

    beatN: Optional[BeatNetResult] = None


@router.post(
    "/",
    response_model=AudioAnalysisResult,
    description=(
        "Загрузка записи для анализа. Используйте `multipart/form-data`. "
    ),
)
async def analyze_record(
    file: Annotated[UploadFile, File()],
    onsetType: Literal["complex", "hfc", "flux"],
):
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

    record_path = os.path.join(settings.UPLOAD_FOLDER, f"{uuid4()}_{file.filename}")

    with open(record_path, "wb") as f:
        f.write(file.file.read())

    try:
        data = analyze_audio(record_path, onset_type=onsetType)
        bn = analyze_with_beatnet_offline(record_path)
        result =  AudioAnalysisResult(**data)
        result.beatN = bn
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Audio analysis failed")
    finally:
        try:
            os.remove(record_path)
        except OSError:
            pass


