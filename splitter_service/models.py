from enum import Enum, IntEnum

from tortoise import fields
from tortoise.models import Model


class Stems(IntEnum):
    """Enumeration of output stems."""

    TWO: int = 2
    FOUR: int = 4
    FIVE: int = 5


class StemType(str, Enum):
    ACCOMPANIMENT = "accompaniment"
    VOCAL = "vocals"
    BASS = "bass"
    DRUMS = "drums"
    PIANO = "piano"
    OTHER = "other"


class RecordStatus(str, Enum):
    DONE = "done"
    ERROR = "error"
    PENDING = "pending"
    DELETED = "deleted"


class Record(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    status = fields.CharEnumField(enum_type=RecordStatus, default=RecordStatus.PENDING)
    file_path = fields.CharField(max_length=1024)
    device_token = fields.CharField(max_length=1024, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    stems: fields.ReverseRelation["Stem"]

    class PydanticMeta:
        exclude = ["file_path", "device_token"]


class Stem(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    type = fields.CharEnumField(enum_type=StemType, max_length=50)
    file_path = fields.CharField(max_length=1024)
    created_at = fields.DatetimeField(auto_now_add=True)
    record: fields.ForeignKeyNullableRelation[Record] = fields.ForeignKeyField(
        "models.Record", related_name="stems", null=True
    )


class TTS(Model):
    id = fields.UUIDField(pk=True)
    text = fields.TextField()
    status = fields.CharEnumField(enum_type=RecordStatus, default=RecordStatus.PENDING)
    device_token = fields.CharField(max_length=1024, null=True)
    speech_path = fields.CharField(max_length=1024, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)


class Prompt(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=256)
    voice_path = fields.CharField(max_length=1024)
    is_efficient = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
