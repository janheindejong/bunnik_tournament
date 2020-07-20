"""Database"""

from json import dumps

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from .models import Game, Participant
from .schemas import GameCreate

WEIGHT_PERFORMANCE = 0.5
WEIGHT_PARTICIPATION = 1 - WEIGHT_PERFORMANCE


def to_json(model):
    """ Returns a JSON representation of an SQLAlchemy-backed object.
    """
    json = {}
    json['fields'] = {}
    json['pk'] = getattr(model, 'id')

    for col in model._sa_class_manager.mapper.mapped_table.columns:
        json['fields'][col.name] = getattr(model, col.name)

    return dumps([json])


def get_scores(db: Session):
    total = db.query(func.sum(Game.points)).scalar()
    stmt = (
        db.query(
            Participant.player,
            (
                func.round(100 * func.sum(Participant.points) / func.sum(Game.points))
            ).label("performance"),
            (func.round(100 * func.sum(Game.points) / float(total))).label(
                "participation"
            ),
        )
        .join(Game)
        .group_by(Participant.player)
        .subquery()
    )
    query = db.query(
        stmt.c.player,
        stmt.c.performance,
        stmt.c.participation,
        func.round(
            WEIGHT_PERFORMANCE * stmt.c.performance
            + WEIGHT_PARTICIPATION * stmt.c.participation
        ).label("score"),
    ).order_by("score")
    return query.all()


def get_games(db: Session):
    return db.query(Game).options(selectinload(Game.participants)).all()


def create_new_game(db: Session, obj_in: GameCreate):
    game = Game(
        name=obj_in.name,
        datetime=obj_in.datetime,
        duration=obj_in.duration,
        points=_extract_game_points(obj_in.duration),
    )
    max_rank = 0
    for participant in obj_in.participants:
        max_rank = max(max_rank, participant.rank)
    for participant in obj_in.participants:
        game.participants.append(
            Participant(
                player=participant.player,
                rank=participant.rank,
                points=game.points * (max_rank - participant.rank) / (max_rank - 1),
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
