import uuid
import json
from typing import NamedTuple
import sqlite3
import hashlib
import time

import pandas as pd


WEIGHT_PERFORMANCE = 0.75  # Relative importance of winning versus participating
DATABASE_URL = "bunnik_boys_gaming_tournament.db"


class AlreadyExists(Exception):
    """Raised if entry already exists in database"""


class Game(NamedTuple):
    game_id: str
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
            CREATE TABLE IF NOT EXISTS games 
            (game_id text, name text, datetime text, duration int, points int)
            """
        )
        conn.execute(
            """ 
            CREATE TABLE IF NOT EXISTS participations 
            (game_id text, player text, rank int, score real)
            """
        )


def post_game(**kwargs):
    game, participations = _parse_game_dict(**kwargs)
    with sqlite3.connect(DATABASE_URL) as conn:
        if conn.execute(
            "SELECT 1 FROM games WHERE game_id = ?", (game.game_id,)
        ).fetchone():
            raise AlreadyExists("Entry already exists")
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
    c = conn.execute("""SELECT * FROM games""")
    for game in c:
        print(game)


def get_scores():
    conn = sqlite3.connect(DATABASE_URL)
    TOTAL_POINTS = conn.execute("SELECT SUM(points) FROM games").fetchone()[0]
    c = conn.execute(
        """
        SELECT 
            player, 
            ROUND(100 * performance, 1), 
            ROUND(100 * participation, 1), 
            ROUND(100 * (:weight * performance + (1 - :weight) * participation), 1) AS score
        FROM 
        (
            SELECT 
                player AS player,
                SUM(score) / SUM(points) AS performance,
                SUM(points) / CAST(:total_points AS float) AS participation
            FROM 
                games 
            INNER JOIN participations ON participations.game_id = games.game_id
            GROUP BY 
                player
        )
        ORDER BY 
            score
        """,
        {"weight": WEIGHT_PERFORMANCE, "total_points": TOTAL_POINTS},
    )
    for player in c:
        print(player)


def main():
    init_db()
    with open("scores.json") as f:
        for game in json.load(f):
            game["game_id"] = _generate_game_id(**game)
            try:
                post_game(**game)
            except AlreadyExists:
                print(f"Game with ID {game['game_id']} already exists!")
    read_stuff()
    t = time.time()
    get_scores()
    print(f"This took {time.time() - t} seconds")


def _parse_game_dict(game_id, name, datetime, duration, ranking):
    points = _game_points(duration)
    game = Game(game_id, name, datetime, duration, points)
    participations = []
    max_rank = max(ranking.values())
    for player, rank in ranking.items():
        score = points * (max_rank - rank) / (max_rank - 1)
        participations.append(Participation(game_id, player, rank, score))
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


# def main():
#     games_df = pd.DataFrame()
#     participations_df = pd.DataFrame()
#     with open("scores.json") as f:
#         for game in json.load(f):
#             game, participations = _parse_game_dict(**game)
#             games_df = games_df.append(pd.DataFrame([game]))
#             participations_df = participations_df.append(pd.DataFrame(participations))
#     df = pd.merge(games_df, participations_df, on="game_id")
#     scores = 100 * (
#         RATIO * df.groupby("player").score.sum() / df.groupby("player").points.sum()
#         + (1 - RATIO) * df.groupby("player").points.sum() / games_df.points.sum()
#     )
#     print(scores.sort_values())
#     print(games_df.duration.sum())
