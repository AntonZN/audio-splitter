from enum import Enum, IntEnum

from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
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
    device_token = fields.CharField(max_length=1024)
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


RecordSchema = pydantic_model_creator(Record, name="RecordSchema")
RecordStatusSchema = pydantic_model_creator(
    Record, name="RecrodStatusSchema", include=("id", "name", "status")
)
