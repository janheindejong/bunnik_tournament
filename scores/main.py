"""FastAPI app"""
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import SessionLocal

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/games")
def post_game(game: schemas.GameCreate, db: Session = Depends(get_db)):
    return crud.create_new_game(db, game)


@app.get("/games")
def get_games(db: Session = Depends(get_db)):
    return crud.get_games(db)


@app.get("/scores")
def get_scores(db: Session = Depends(get_db)):
    return [s._asdict() for s in crud.get_scores(db)]
