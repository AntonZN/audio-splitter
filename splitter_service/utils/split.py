import os

from spleeter.audio import Codec
from spleeter.separator import Separator

from core.config import get_settings
from models import StemType, Stem, Record, RecordStatus
from utils.cmd import run_command

settings = get_settings()


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


async def separate_record(record_id: str, codec: Codec, count_stems: int):
    output_folder = os.path.join(settings.STEMS_FOLDER, str(record_id))
    os.makedirs(output_folder, exist_ok=True)
    record = await Record.get(id=record_id)
    separator = Separator(f"spleeter:{count_stems}stems")
    separator.separate_to_file(
        record.file_path,
        output_folder,
        filename_format="{instrument}.{codec}",
        codec=codec,
    )

    record.status = RecordStatus.DONE
    await record.save(update_fields=["status"])
    await create_stems(record, count_stems, codec)
    os.remove(record.file_path)


async def separate_record_subprocess(record_id: str, codec: Codec, count_stems: int):
    output_folder = os.path.join(settings.STEMS_FOLDER, str(record_id))
    record = await Record.get(id=record_id)
    command = " ".join(
        [
            "spleeter",
            "separate",
            f"-o {output_folder}",
            f"-p spleeter:{count_stems}stems",
            "-f {instrument}" + f".{codec}",
            f"'{record.file_path}'",
        ]
    )
    status = await run_command(command)

    if not status:
        record.status = RecordStatus.ERROR
    else:
        record.status = RecordStatus.DONE

    await record.save(update_fields=["status"])
    await create_stems(record, count_stems, codec)

    os.remove(record.file_path)
