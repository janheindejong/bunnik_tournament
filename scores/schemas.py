"""FastAPI schemas"""

from typing import List
from datetime import datetime

from pydantic import BaseModel


class Participant(BaseModel):
    player: str
    rank: int


class Game(BaseModel):
    name: str
    datetime: datetime
    duration: int
    participants: List[Participant]
