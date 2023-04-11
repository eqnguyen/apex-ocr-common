"""Create initial tables

Revision ID: 61d131a3f80a
Revises: 
Create Date: 2023-04-11 03:55:48.505412

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum

Base = declarative_base()

# revision identifiers, used by Alembic.
revision = "61d131a3f80a"
down_revision = None
branch_labels = None
depends_on = None


class Legends(enum.Enum):
    BLOODHOUND = enum.auto()
    GIBRALTAR = enum.auto()
    LIFELINE = enum.auto()
    PATHFINDER = enum.auto()
    WRAITH = enum.auto()
    BANGALORE = enum.auto()
    CAUSTIC = enum.auto()
    MIRAGE = enum.auto()
    OCTANE = enum.auto()
    WATTSON = enum.auto()
    CRYPTO = enum.auto()
    REVENANT = enum.auto()
    LOBA = enum.auto()
    RAMPART = enum.auto()
    HORIZON = enum.auto()
    FUSE = enum.auto()
    VALKYRIE = enum.auto()
    SEER = enum.auto()
    ASH = enum.auto()
    MAD = enum.auto()
    NEWCASTLE = enum.auto()
    VANTAGE = enum.auto()
    CATALYST = enum.auto()


class MatchType(enum.Enum):
    ARENAS = enum.auto()
    BATTLE_ROYALE = enum.auto()


class WinLoss(enum.Enum):
    WIN = enum.auto()
    LOSS = enum.auto()


class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class PlayerMatchResult(Base):
    __tablename__ = "player_match_result"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("player.id"))
    match_id = Column(Integer, ForeignKey("match_result.id"))
    legend = Column(Enum(Legends))
    kills = Column(Integer, nullable=False)
    assists = Column(Integer, nullable=False)
    knockdowns = Column(Integer, nullable=False)
    damage = Column(Integer, nullable=False)
    survival_time = Column(Integer, nullable=False)
    revives = Column(Integer, nullable=False)
    respawns = Column(Integer, nullable=False)


class MatchResult(Base):
    __tablename__ = "match_result"

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime, nullable=False)
    match_type = Column(Enum(MatchType), nullable=False)
    place = Column(Integer)
    result = Column(Enum(WinLoss))
    p1_match_result_id = Column(Integer, ForeignKey("player_match_result.id"))
    p2_match_result_id = Column(Integer, ForeignKey("player_match_result.id"))
    p3_match_result_id = Column(Integer, ForeignKey("player_match_result.id"))


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
