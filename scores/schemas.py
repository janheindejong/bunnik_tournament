"""FastAPI schemas"""

from datetime import datetime
from typing import List

from pydantic import BaseModel


class Participant(BaseModel):
    player: str
    rank: int


class GameBase(BaseModel):
    name: str
    datetime: datetime
    duration: int
    participants: List[Participant]


class GameCreate(GameBase):
    pass
