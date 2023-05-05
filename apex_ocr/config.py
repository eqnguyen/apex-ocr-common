import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Valid image extensions
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]

# Path to stats file
DATA_DIRECTORY = Path(__file__).parent.parent / "data"
DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

SQUAD_STATS_FILE = DATA_DIRECTORY / "squad_stats.csv"

# Database output
DATABASE = False
DATABASE_YML_FILE = Path(__file__).parent.parent / "db.yml"

# Headers
SQUAD_SUMMARY_HEADERS = [
    "Datetime",
    "Place",
    "Squad Kills",
    "P1",
    "P1 Kills",
    "P1 Assists",
    "P1 Knocks",
    "P1 Damage",
    "P1 Time Survived",
    "P1 Revives",
    "P1 Respawns",
    "P2",
    "P2 Kills",
    "P2 Assists",
    "P2 Knocks",
    "P2 Damage",
    "P2 Time Survived",
    "P2 Revives",
    "P2 Respawns",
    "P3",
    "P3 Kills",
    "P3 Assists",
    "P3 Knocks",
    "P3 Damage",
    "P3 Time Survived",
    "P3 Revives",
    "P3 Respawns",
    "Hash",
]

# Regular expressions
SQUAD_SUMMARY_MAP = {
    "Place": re.compile("#([0-9]{1,2})"),
    "Squad Kills": re.compile("(?:totalkills){1}([dDoO!lI0-9]{1,2})"),
    "Player": re.compile("#([0-9]{1,2})"),
    "Kills/Assists/Knocks": re.compile(
        "(?:kills/assists/knocks){1}([dDoO!lI0-9]{1,2}/[dDoO!lI0-9]{1,2}/[dDoO!lI0-9]{1,2})"
    ),
    "Damage": re.compile("(?:amagedealt){1}(\d+)"),
    "Time Survived": re.compile("(?:survivaltime){1}(\d+)"),
    "Revives": re.compile("(?:revivegiven){1}(\d+)"),
    "Respawns": re.compile("(?:respawngiven){1}(\d+)"),
}
