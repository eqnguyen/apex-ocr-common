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


class Clan(Base):
    __tablename__ = "clan"

    id = Column(Integer, primary_key=True)
    tag = Column(String, nullable=False)
    name = Column(String)

    players = relationship(
        "Player",
        back_populates="clan",
    )

    def __repr__(self):
        return f"Clan(id={self.id}, tag={self.tag}, name={self.name})"

    def __str__(self):
        return f"{self.name} ({self.tag})"

    def to_dict(self):
        return {"id": self.id, "tag": self.tag, "name": self.name}


class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True)
    clan_id = Column(Integer, ForeignKey("clan.id", ondelete="SET NULL"))
    name = Column(String, nullable=False)

    match_results = relationship(
        "PlayerMatchResult",
        back_populates="player",
        cascade="all, delete",
        passive_deletes=True,
    )
    clan = relationship("Clan", back_populates="players")

    def __repr__(self):
        return f"Player(id={self.id}, clan_id={self.clan_id}, name={self.name})"

    def __str__(self):
        if self.clan:
            return f"[{self.clan.tag}] {self.name}"
        else:
            return f"{self.name}"

    def to_dict(self):
        return {"id": self.id, "clan_id": self.clan_id, "name": self.name}


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

    player = relationship("Player", back_populates="match_results")
    match_result = relationship("MatchResult", back_populates="player_match_results")

    def __repr__(self):
        return (
            f"PlayerMatchResult(id={self.id}, match_result=MatchResult(id={self.match_result.id}, "
            f"datetime={self.match_result.datetime}, match_type={self.match_result.match_type}, "
            f"place={self.match_result.place}, result={self.match_result.result}, hash={self.match_result.hash}), "
            f"player=Player(id={self.player_id}, clan_id={self.player.clan_id}, name={self.player.name}), "
            f"legend={self.legend}, kills={self.kills}, assists={self.assists}, "
            f"knockdowns={self.knockdowns}, damage={self.damage}, survival_time={self.survival_time}, "
            f"revives={self.revives}, respawns={self.respawns})"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "match_id": self.match_result.id,
            "datetime": self.match_result.datetime,
            "match_type": self.match_result.match_type,
            "place": self.match_result.place,
            "result": self.match_result.result,
            "hash": self.match_result.hash,
            "player_id": self.player_id,
            "clan_id": self.player.clan_id,
            "player_name": self.player.name,
            "legend": self.legend,
            "kills": self.kills,
            "assists": self.assists,
            "knockdowns": self.knockdowns,
            "damage": self.damage,
            "survival_time": self.survival_time,
            "revives": self.revives,
            "respawns": self.respawns,
        }


class MatchResult(Base):
    __tablename__ = "match_result"

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime(timezone=True), nullable=False)
    match_type = Column(Enum(MatchType), nullable=False)
    place = Column(Integer)
    result = Column(Enum(WinLoss))
    hash = Column(String, unique=True, nullable=False)

    player_match_results = relationship(
        "PlayerMatchResult",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __repr__(self):
        return (
            f"MatchResult(id={self.id}, datetime={self.datetime}, match_type={self.match_type}, "
            f"place={self.place}, result={self.result}, hash={self.hash})"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "datetime": self.datetime,
            "match_type": self.match_type,
            "place": self.place,
            "result": self.result,
            "hash": self.hash,
        }
