import asyncio
import os
import httpx
import arrow

from core.config import get_settings
from models import StemType, Stem, Record, RecordStatus
from loguru import logger

settings = get_settings()


async def run_command(cmd: str) -> bool:
    process = await asyncio.subprocess.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE
    )

    await process.communicate()

    if process.returncode == 0:
        return True
    else:
        return False


async def create_stems(record: Record, stems_count: int, codec: str):
    stem_mapping = {
        2: [StemType.VOCAL, StemType.NO_VOCALS],
        6: [
            StemType.VOCAL,
            StemType.DRUMS,
            StemType.BASS,
            StemType.PIANO,
            StemType.GUITAR,
            StemType.OTHER,
        ],
    }

    stem_types = stem_mapping.get(stems_count)

    if not stem_types:
        record.status = RecordStatus.ERROR
        await record.save(update_fields=["status"])

    stems = []

    for i in range(stems_count):
        stem_type = stem_types[i]

        if stems_count > 2 and stem_type == StemType.NO_VOCALS:
            continue

        stem_name = f"{stem_type.value}.{codec}"
        file_path = f"{settings.STEMS_FOLDER}/{record.id}/htdemucs_6s/{stem_name}"

        stem = Stem(
            record_id=record.id,
            name=stem_name,
            type=StemType.ACCOMPANIMENT
            if stem_type == StemType.NO_VOCALS
            else stem_type,
            file_path=file_path,
        )

        stems.append(stem)

    await Stem.bulk_create(stems)


async def separate_record_subprocess(record_id: str, codec: str, count_stems: int):
    try:
        record = await Record.get(id=record_id)
    except Exception:
        return

    try:
        output_folder = os.path.join(settings.STEMS_FOLDER, str(record_id))
        if count_stems > 2:
            command = " ".join(
                [
                    "demucs",
                    "--mp3" if codec == "mp3" else "",
                    f"-o {output_folder}",
                    "--filename {stem}" + f".{codec}",
                    f"-n htdemucs_6s",
                    f"'{record.file_path}'",
                ]
            )
        else:
            command = " ".join(
                [
                    "demucs",
                    "--mp3" if codec == "mp3" else "",
                    "--two-stems=vocals",
                    f"-o {output_folder}",
                    "--filename {stem}" + f".{codec}",
                    f"-n htdemucs_6s",
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
        logger.debug("create_stems success")

        try:
            os.remove(record.file_path)
        except Exception:
            pass

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                waiting_time_in_seconds = int(
                    (arrow.utcnow().datetime - record.created_at).total_seconds()
                )
                await client.post(
                    f"https://rvc.vocalremove.online/api/v1/studio/statistics/old_split/avg/",
                    params={"seconds": waiting_time_in_seconds, "token": settings.RVC_TOKEN},
                )
        except Exception:
            pass
    except Exception:
        record.status = RecordStatus.ERROR
        await record.save(update_fields=["status"])
