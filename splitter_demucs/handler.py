import json
import logging

from pydantic import BaseModel
from splitter import separate_record_subprocess


class Message(BaseModel):
    record_id: str
    codec: str
    count_stems: int


async def handle(amq_message: str) -> None:
    try:
        message_data = json.loads(amq_message)
    except json.JSONDecodeError:

        return None

    try:
        topic = message_data.pop("topic")
    except AttributeError:
        logging.error(f"Message content type must be dict, not {type(message_data)}")
        return None

    if topic == "split":
        await separate_record_subprocess(
            message_data["record_id"], message_data["codec"], message_data["count_stems"]
        )

