import json
from typing import NamedTuple, Dict
import sqlite3
import hashlib
import time
from datetime import datetime

from fastapi import FastAPI


WEIGHT_PERFORMANCE = 0.75  # Relative importance of winning versus participating
DATABASE_URL = "bunnik_boys_gaming_tournament.db"


class AlreadyExists(Exception):
    """Raised if entry already exists in database"""


class Game(NamedTuple):
    id: str
    name: str
    datetime: str
    duration: int
    points: int


class Participation(NamedTuple):
    game_id: str
    player: str
    rank: int
    score: float


def init_db():
    with sqlite3.connect(DATABASE_URL) as conn:
        conn.execute(
            """ 
            CREATE TABLE IF NOT EXISTS games (
                id text, 
                name text, 
                datetime text, 
                duration int, 
                points int,
                PRIMARY KEY (id)
                UNIQUE (id)
            )
            """
        )
        conn.execute(
            """ 
            CREATE TABLE IF NOT EXISTS participations (
                game_id text, 
                player text, 
                rank int, 
                score real,
                FOREIGN KEY (game_id) REFERENCES games (id)
            )
            """
        )


def post_game(**kwargs):
    game, participations = _parse_game_dict(**kwargs)
    with sqlite3.connect(DATABASE_URL) as conn:
        conn.execute(
            """
            INSERT INTO 
                games 
            VALUES 
                (?, ?, ?, ?, ?)
            """,
            game,
        )
        conn.executemany(
            """
            INSERT INTO 
                participations
            VALUES 
                (?, ?, ?, ?)
            """,
            participations,
        )
    return game.id


def read_stuff():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.execute("SELECT * FROM games")
    for game in c:
        print(game)
    c = conn.execute("SELECT * FROM participations")
    for partipation in c:
        print(partipation)


def get_scores():
    with sqlite3.connect(DATABASE_URL) as conn:
        TOTAL_POINTS = conn.execute("SELECT SUM(points) FROM games").fetchone()[0]
        c = conn.execute(
            """
            SELECT 
                player AS player,
                ROUND(SUM(score) / SUM(points), 3) AS performance,
                ROUND(SUM(points) / CAST(? AS float), 3) AS participation
            FROM 
                games 
            INNER JOIN participations ON participations.game_id = games.id
            GROUP BY 
                player
            """,
            (TOTAL_POINTS,),
        )
        scores = {}
        for player, performance, participation in c:
            scores[player] = {
                "performance": round(100 * performance, 1),
                "participation": round(100 * participation, 1),
                "score": round(_compute_score(performance, participation), 1),
            }
        return scores


def main():
    init_db()
    with open("scores.json") as f:
        for game in json.load(f):
            try:
                post_game(**game)
            except sqlite3.IntegrityError as err:
                print(err)
    read_stuff()
    t = time.time()
    get_scores()
    print(f"This took {time.time() - t} seconds")


def _parse_game_dict(name, datetime, duration, ranking):
    id = _generate_game_id(name, datetime)
    points = _extract_game_points(duration)
    game = Game(id, name, datetime, duration, points)
    participations = []
    max_rank = max(ranking.values())
    for player, rank in ranking.items():
        score = points * (max_rank - rank) / (max_rank - 1)
        participations.append(Participation(game.id, player, rank, score))
    return game, participations


def _generate_game_id(*args):
    b = str(args).encode("ascii")
    return hashlib.sha1(b).hexdigest()


def _compute_score(performance, participation):
    return 100 * (
        WEIGHT_PERFORMANCE * performance + (1 - WEIGHT_PERFORMANCE) * participation
    )


def _extract_game_points(duration):
    if duration < 45:
        return 1
    elif duration < 90:
        return 2
    elif duration < 180:
        return 3
    else:
        return 4


if __name__ == "__main__":
    main()
