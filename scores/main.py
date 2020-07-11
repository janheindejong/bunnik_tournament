"""FastAPI app"""
from typing import List

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from . import schemas, crud

Base.metadata.create_all(engine)

# FastAPI app
app = FastAPI()

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()


@app.post("/game")
def post_game(game: schemas.Game, db: Session = Depends(get_db)):
    return crud.create_new_game(db, game.name, game.datetime, game.duration, game.ranking)


@app.get("/scores")
def get_scores(db: Session = Depends(get_db)):
    return [s._asdict() for s in crud.get_scores(db, ["Jan Hein", "Ruben"])]
