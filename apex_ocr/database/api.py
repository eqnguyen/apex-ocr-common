from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

from .models import MatchResult, Player, PlayerMatchResult


class ApexDatabaseApi:
    def __init__(self, db_conn_str) -> None:
        self.engine = create_engine(db_conn_str)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add(self, obj):
        self.session.add(obj)
        self.session.commit()

    def add_all(self, add_list):
        # Process 100 at a time to avoid connection issues
        for i in range(0, len(add_list), 100):
            self.session.add_all(add_list[i : i + 100])
        self.session.commit()
