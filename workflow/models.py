from datetime import datetime

from pydantic import BaseModel


class Brief(BaseModel):
    guid: str
    title: str
    published_time: datetime
    audio_url: str
