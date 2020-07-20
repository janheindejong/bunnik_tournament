"""SQLAlchemy models"""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    datetime = Column(DateTime)
    duration = Column(Integer)
    points = Column(Integer)
    participants = relationship("Participant")


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True)
    player = Column(String)
    rank = Column(Integer)
    points = Column(Float)
    game_id = Column(Integer, ForeignKey("games.id"))
