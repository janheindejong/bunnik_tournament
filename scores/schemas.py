"""FastAPI schemas"""

from typing import Dict
from datetime import datetime

from pydantic import BaseModel

class Game(BaseModel):
    name: str
    datetime: datetime
    duration: int
    ranking: Dict[str, int]
