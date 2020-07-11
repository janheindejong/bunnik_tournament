"""Back-end API"""
from typing import Dict
from datetime import datetime

from pydantic import BaseModel
from fastapi import FastAPI

from .database import init_db, post_game as post_game_to_db, get_scores as get_scores_db

# FastAPI app
app = FastAPI()

# Initialize database
init_db()


class Game(BaseModel):
    name: str
    datetime: datetime
    duration: int
    ranking: Dict[str, int]


@app.post("/game")
def post_game(game: Game):
    return post_game_to_db(**dict(game))


@app.get("/scores")
def get_scores():
    return get_scores_db()
