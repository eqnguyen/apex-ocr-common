import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import sessionmaker

from apex_ocr.utils import time_survived_to_seconds

from .models import Clan, MatchResult, MatchType, Player, PlayerMatchResult

logger = logging.getLogger(__name__)


class ApexDatabaseApi:
    def __init__(self, db_conn_str) -> None:
        self.engine = create_engine(db_conn_str)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add(self, obj) -> None:
        self.session.add(obj)
        self.session.commit()

    def add_all(self, add_list) -> None:
        # Process 100 at a time to avoid connection issues
        for i in range(0, len(add_list), 100):
            self.session.add_all(add_list[i : i + 100])
        self.session.commit()

    def drop_all(self) -> None:
        self.session.query(Clan).delete()
        self.session.query(MatchResult).delete()
        self.session.query(Player).delete()
        self.session.query(PlayerMatchResult).delete()
        self.session.commit()

    def push_results(self, results: dict) -> None:
        # TODO: Check for duplicate result in the database
        # TODO: Handle different match types

        # Commit match result
        match_result = MatchResult(
            datetime=results["Datetime"],
            match_type=MatchType.BATTLE_ROYALE,
            place=results["Place"],
            hash=results["Hash"],
        )
        try:
            self.add(match_result)
        except IntegrityError:
            logger.info("Duplicate match results found in database!")
            self.session.rollback()
            return

        for p_num in ["P1", "P2", "P3"]:
            # Commit players if not already in database
            player_name = results[p_num]
            player = self.session.query(Player).filter_by(name=player_name).first()

            if player is None:
                player = Player(name=player_name)
                self.add(player)

            # Commit match player results
            time_survived = time_survived_to_seconds(
                results[p_num + " " + "Time Survived"]
            )

            player_match_result = PlayerMatchResult(
                player_id=player.id,
                match_id=match_result.id,
                kills=results[p_num + " " + "Kills"],
                assists=results[p_num + " " + "Assists"],
                knockdowns=results[p_num + " " + "Knocks"],
                damage=results[p_num + " " + "Damage"],
                survival_time=time_survived,
                revives=results[p_num + " " + "Revives"],
                respawns=results[p_num + " " + "Respawns"],
            )

            self.add(player_match_result)
