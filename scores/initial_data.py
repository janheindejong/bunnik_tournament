"""Creates initial database"""
import json

from scores import crud
from scores.database import Base, SessionLocal, engine
from scores.schemas import GameCreate

FILENAME_INTIAL_DATA = "initial_data.json"


def main():
    # Check if table exists and create one if necessary
    Base.metadata.create_all(engine)

    # Connect to DB
    db = SessionLocal()

    # Parse json
    with open(FILENAME_INTIAL_DATA, "r") as f:
        for game in json.load(f):
            game = GameCreate(**game)
            crud.create_new_game(db, game)


if __name__ == "__main__":
    main()
