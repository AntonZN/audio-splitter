from datetime import datetime
from enum import Enum
from pydantic import BaseModel, UUID4


class Stem(BaseModel):
    id: UUID4
    name: str
    type: str
    url: str
    created: datetime


class QueueRecordMessage(BaseModel):
    record_id: str
    output_codec: str
    output_stems: int


class Codec(str, Enum):
    """Enumeration of supported audio codec."""

    WAV: str = "wav"
    MP3: str = "mp3"
    OGG: str = "ogg"
    M4A: str = "m4a"
    WMA: str = "wma"
    FLAC: str = "flac"
