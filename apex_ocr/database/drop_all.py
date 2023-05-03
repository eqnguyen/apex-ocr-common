import yaml

from apex_ocr.config import DATABASE, DATABASE_YML_FILE
from apex_ocr.database.api import ApexDatabaseApi


def drop():
    with open(DATABASE_YML_FILE) as db_file:
        db_config = yaml.load(db_file, Loader=yaml.FullLoader)

    dialect = db_config["dialect"]
    username = db_config["username"]
    password = db_config["password"]
    hostname = db_config["hostname"]
    port = db_config["port"]
    database_name = db_config["database_name"]

    db_conn_str = f"{dialect}://{username}:{password}@{hostname}:{port}/{database_name}"

    db_conn = ApexDatabaseApi(db_conn_str)
    db_conn.drop_all()

    print("Dropped all rows from database")


if __name__ == "__main__":
    drop()
