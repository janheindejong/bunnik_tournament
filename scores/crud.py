"""Database"""

import dateutil.parser
from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Game, Participation


def get_scores(db: Session):
    total = db.query(func.sum(Game.points)).scalar()
    stmt = (
        db.query(
            Participation.player,
            (
                func.round(100 * func.sum(Participation.points) / func.sum(Game.points))
            ).label("performance"),
            (func.round(100 * func.sum(Game.points) / float(total))).label(
                "participation"
            ),
        )
        .join(Game)
        .group_by(Participation.player)
        .subquery()
    )
    query = db.query(
        stmt.c.player,
        stmt.c.performance,
        stmt.c.participation,
        func.round(0.67 * stmt.c.performance + 0.33 * stmt.c.participation).label(
            "score"
        ),
    ).order_by("score")
    return query.all()


def get_games(db: Session):
    return db.query(Game).all()


def create_new_game(db: Session, name, datetime, duration, participants):
    points = _extract_game_points(duration)
    datetime = (
        dateutil.parser.parse(datetime) if isinstance(datetime, str) else datetime
    )
    game = Game(name=name, datetime=datetime, duration=duration, points=points)
    max_rank = 0
    for participant in participants:
        max_rank = max(max_rank, participant.rank)
    for participant in participants:
        game.participations.append(
            Participation(
                player=participant.player,
                rank=participant.rank,
                points=points * (max_rank - participant.rank) / (max_rank - 1),
            )
        )
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


def _extract_game_points(duration):
    if duration < 45:
        return 1
    if duration < 90:
        return 2
    if duration < 180:
        return 3
    return 4
