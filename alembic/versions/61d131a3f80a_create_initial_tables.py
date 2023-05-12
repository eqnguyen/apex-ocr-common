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


class Clan(Base):
    __tablename__ = "clan"

    id = Column(Integer, primary_key=True)
    tag = Column(String, nullable=False)
    name = Column(String)


class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True)
    clan_id = Column(Integer, ForeignKey("clan.id", ondelete="SET NULL"))
    name = Column(String, nullable=False)


class PlayerMatchResult(Base):
    __tablename__ = "player_match_result"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("match_result.id", ondelete="CASCADE"))
    player_id = Column(Integer, ForeignKey("player.id", ondelete="CASCADE"))
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
    datetime = Column(DateTime(timezone=True), nullable=False)
    match_type = Column(Enum(MatchType), nullable=False)
    place = Column(Integer)
    result = Column(Enum(WinLoss))
    hash = Column(String, unique=True, nullable=False)


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

    op.execute(
        """
    CREATE VIEW full_match_results AS
    SELECT mr.id,
        mr.datetime,
        mr.match_type,
        mr.place,
        mr.result,
        mr.hash,
        p1.name AS p1,
        pmr1.legend AS p1_legend,
        pmr1.kills AS p1_kills,
        pmr1.assists AS p1_assists,
        pmr1.knockdowns AS p1_knockdowns,
        pmr1.damage AS p1_damage,
        pmr1.survival_time AS p1_survival_time,
        pmr1.revives AS p1_revives,
        pmr1.respawns AS p1_respawns,
        p2.name AS p2,
        pmr2.legend AS p2_legend,
        pmr2.kills AS p2_kills,
        pmr2.assists AS p2_assists,
        pmr2.knockdowns AS p2_knockdowns,
        pmr2.damage AS p2_damage,
        pmr2.survival_time AS p2_survival_time,
        pmr2.revives AS p2_revives,
        pmr2.respawns AS p2_respawns,
        p3.name AS p3,
        pmr3.legend AS p3_legend,
        pmr3.kills AS p3_kills,
        pmr3.assists AS p3_assists,
        pmr3.knockdowns AS p3_knockdowns,
        pmr3.damage AS p3_damage,
        pmr3.survival_time AS p3_survival_time,
        pmr3.revives AS p3_revives,
        pmr3.respawns AS p3_respawns
    FROM match_result mr
    JOIN player_match_result pmr1 ON pmr1.match_id = mr.id
    JOIN player p1 ON p1.id = pmr1.player_id
    JOIN player_match_result pmr2 ON pmr1.match_id = pmr2.match_id AND pmr1.id < pmr2.id
    JOIN player p2 ON p2.id = pmr2.player_id
    JOIN player_match_result pmr3 ON pmr2.match_id = pmr3.match_id AND pmr2.id < pmr3.id
    JOIN player p3 ON p3.id = pmr3.player_id
    ORDER BY mr.datetime;
    """
    )


def downgrade() -> None:
    bind = op.get_bind()
    op.execute("DROP VIEW full_match_results;")
    Base.metadata.drop_all(bind=bind)
