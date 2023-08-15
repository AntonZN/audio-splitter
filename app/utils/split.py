import os

from spleeter.audio import Codec
from spleeter.separator import Separator

from app.api.adapters import create_stems
from app.core.config import get_settings
from app.models.records import Record, RecordStatus
from app.utils.cmd import run_command

settings = get_settings()


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
