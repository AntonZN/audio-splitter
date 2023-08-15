from datetime import datetime

from pydantic import BaseModel, UUID4


class Stem(BaseModel):
    id: UUID4
    name: str
    type: str
    url: str
    created: datetime
