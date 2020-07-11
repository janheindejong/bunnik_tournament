"""For testing purposes"""
import json
from .crud import create_new_game, get_scores
from .database import Base, SessionLocal, engine


def main():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    with open("games.json") as f:
        for game in json.load(f):
            create_new_game(db, **game)
    print(get_scores(db, ["Jan Hein", "Dirk", "Ruben"]))
    db.close()


main()
