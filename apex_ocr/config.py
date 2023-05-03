import re
from pathlib import Path

# Valid image extensions
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]

from screeninfo import get_monitors

# Path to stats file
DATA_DIRECTORY = Path(__file__).parent.parent / "data"
DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

SQUAD_STATS_FILE = DATA_DIRECTORY / "squad_stats.csv"

primary_monitor = None
for m in get_monitors():
    if m.is_primary:
        primary_monitor = m
        break

SUMMARY_ROI = (
    primary_monitor.width / 3,
    0,
    2 / 3 * primary_monitor.width,
    primary_monitor.height / 10,
)

TOTAL_KILLS_ROI = (
    primary_monitor.width * 5 / 6,
    primary_monitor.height / 10,
    primary_monitor.width,
    primary_monitor.height * 2 / 10,
)

TOP_SCREEN = (
    primary_monitor.x,
    primary_monitor.y,
    primary_monitor.x + primary_monitor.width,
    primary_monitor.y + primary_monitor.height,
)

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

# Tesseract configurations
TESSERACT_CONFIG = "-c tessedit_char_whitelist=()/#01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz --psm 11"
TESSERACT_BLOCK_CONFIG = "-c tessedit_char_whitelist=()/#01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz --psm 6"

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
