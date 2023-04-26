import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


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
    clan_id = Column(Integer, ForeignKey("clan.id"))
    name = Column(String, nullable=False)

    match_results = relationship("PlayerMatchResult", back_populates="player")
    clan = relationship("Clan", back_populates="players")


class Clan(Base):
    __tablename__ = "clan"

    id = Column(Integer, primary_key=True)
    tag = Column(String, nullable=False)
    name = Column(String)

    players = relationship("Player", back_populates="clan")


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

    player = relationship("Player", back_populates="match_results")
    match_result = relationship("MatchResult", back_populates="player_match_results")


class MatchResult(Base):
    __tablename__ = "match_result"

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime, nullable=False)
    match_type = Column(Enum(MatchType), nullable=False)
    place = Column(Integer)
    result = Column(Enum(WinLoss))
    hash = Column(String, nullable=False)

    player_match_results = relationship("PlayerMatchResult")
