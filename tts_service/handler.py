import json
import logging

from pydantic import BaseModel
from text_to_speach import generate


class Message(BaseModel):
    record_id: str
    codec: str
    count_stems: int


async def handle(amq_message: str) -> None:
    try:
        message_data = json.loads(amq_message)
    except json.JSONDecodeError:
        return None

    logging.error(f"Message {message_data}")

    try:
        topic = message_data.pop("topic")
    except AttributeError:
        logging.error(f"Message content type must be dict, not {type(message_data)}")
        return None

    if topic == "tts":
        await generate(
            message_data["tts_id"], message_data["text"], message_data["lang"]
        )
