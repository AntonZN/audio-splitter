from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
import os
from loguru import logger

from models import TTS, RecordStatus

os.environ["SUNO_OFFLOAD_CPU"] = "False"
os.environ["SUNO_USE_SMALL_MODELS"] = "True"

from core.config import get_settings

settings = get_settings()


async def generate(tts_id: str, text: str, lang: str, custom_prompt=None):
    logger.debug("start tts")
    tts = await TTS.get(id=tts_id)
    output_folder = os.path.join(settings.TTS_FOLDER, str(tts_id))
    result_filepath = f"{output_folder}/result.wav"
    os.makedirs(output_folder, exist_ok=True)

    if custom_prompt:
        prompt = custom_prompt
    else:
        prompt = f"{lang}_speaker_0"

    try:
        preload_models(
            text_use_gpu=False,
            text_use_small=True,
            codec_use_gpu=False,
            coarse_use_gpu=False,
            coarse_use_small=True,
            fine_use_gpu=False,
            fine_use_small=True,
            path="models",
        )
        audio_array = generate_audio(text, history_prompt=prompt)
        write_wav(result_filepath, SAMPLE_RATE, audio_array)
        status = True
    except Exception as e:
        status = False
        logger.error(f"Geneteate tts Error: {e}")

    if not status:
        tts.status = RecordStatus.ERROR
        tts.file_path = None
    else:
        tts.status = RecordStatus.DONE
        tts.speech_path = result_filepath

    await tts.save(update_fields=["status", "speech_path"])
