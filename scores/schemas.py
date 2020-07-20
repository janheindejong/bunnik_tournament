"""FastAPI schemas"""

from datetime import datetime
from typing import List

from pydantic import BaseModel


class ParticipantBase(BaseModel):
    player: str
    rank: int


class ParticipantCreate(ParticipantBase):
    pass


class Participant(ParticipantBase):
    id: int
    game_id: int
    points: float

    class Config:
        orm_mode = True


class GameBase(BaseModel):
    name: str
    datetime: datetime
    duration: int


class GameCreate(GameBase):
    participants: List[ParticipantCreate]


class Game(GameBase):
    id: int
    participants: List[Participant]
    points: int

    class Config:
        orm_mode = True


class Score(BaseModel):
    player: str
    participation: float
    performance: float
    score: float
