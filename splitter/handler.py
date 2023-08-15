import json
import logging

from pydantic import BaseModel
from spleeter.audio import Codec

from app.utils.split import separate_record_subprocess


class Message(BaseModel):
    record_id: str
    codec: Codec
    count_stems: int


async def handle(amq_message: str) -> None:
    try:
        message_data = json.loads(amq_message)
    except json.JSONDecodeError:
        logging.error(f"Message is not json formatted {amq_message}")
        return None

    try:
        topic = message_data.pop("topic")
    except AttributeError:
        logging.error(f"Message content type must be dict, not {type(message_data)}")
        return None

    if topic == "split":
        try:
            message = Message(**message_data)
            await separate_record_subprocess(
                message.record_id, message.codec, message.count_stems
            )
        except TypeError:
            logging.error(f"Invalid message format: {message_data.keys()}")
