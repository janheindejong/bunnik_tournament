import json
from typing import NamedTuple
import sqlite3
import hashlib
import time


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
        if conn.execute("SELECT 1 FROM games WHERE id = ?", (game.id,)).fetchone():
            raise AlreadyExists(f"Game with id {game.id} already exists")
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


def read_stuff():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.execute("""SELECT * FROM games """)
    for game in c:
        print(game)


def get_scores():
    with sqlite3.connect(DATABASE_URL) as conn:
        TOTAL_POINTS = conn.execute("SELECT SUM(points) FROM games").fetchone()[0]
        c = conn.execute(
            """
            SELECT 
                player, 
                ROUND(100 * performance, 1), 
                ROUND(100 * participation, 1), 
                ROUND(100 * (? * performance + ? * participation), 1) AS score
            FROM 
            (
                SELECT 
                    player AS player,
                    SUM(score) / SUM(points) AS performance,
                    SUM(points) / CAST(? AS float) AS participation
                FROM 
                    games 
                INNER JOIN participations ON participations.game_id = games.id
                GROUP BY 
                    player
            )
            ORDER BY 
                score
            """,
            (WEIGHT_PERFORMANCE, 1 - WEIGHT_PERFORMANCE, TOTAL_POINTS),
        )
        for player in c:
            print(
                "{} won {}%, participated in {}% and has an overall score of {}%".format(
                    *player
                )
            )


def main():
    init_db()
    with open("scores.json") as f:
        for game in json.load(f):
            game["id"] = _generate_game_id(**game)
            try:
                post_game(**game)
            except AlreadyExists as err:
                print(err)
    read_stuff()
    t = time.time()
    get_scores()
    print(f"This took {time.time() - t} seconds")


def _parse_game_dict(id, name, datetime, duration, ranking):
    points = _game_points(duration)
    game = Game(id, name, datetime, duration, points)
    participations = []
    max_rank = max(ranking.values())
    for player, rank in ranking.items():
        score = points * (max_rank - rank) / (max_rank - 1)
        participations.append(Participation(game.id, player, rank, score))
    return game, participations


def _generate_game_id(**kwargs):
    b = str(kwargs).encode("ascii")
    return hashlib.sha1(b).hexdigest()


def _game_points(duration):
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
