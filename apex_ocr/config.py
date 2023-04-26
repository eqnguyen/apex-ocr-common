import re
from pathlib import Path

# Valid image extensions
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]

# Path to stats file
DATA_DIRECTORY = Path(__file__).parent.parent / "data"
DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
PERSONAL_STATS_FILE = DATA_DIRECTORY / "personal_stats.csv"
SQUAD_STATS_FILE = DATA_DIRECTORY / "squad_stats.csv"

# Bounding boxes for image grabs
TOP_SCREEN = (0, 0, 1920, 250)
PERSONAL_SQUAD_PLACED = (1450, 0, 1720, 200)
XP_BREAKDOWN = (200, 200, 1024, 625)

# Database output
DATABASE = False
DATABASE_YML_FILE = Path(__file__).parent.parent / "db.yml"

# Headers
PERSONAL_SUMMARY_HEADERS = [
    "Datetime",
    "Place",
    "Time Survived",
    "Kills",
    "Damage",
    "Revives",
    "Respawns",
    "Champions Killed",
    "Friends",
    "XP Earned",
    "Hash",
]

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
PERSONAL_SUMMARY_MAP = {
    "Place": re.compile("#([0-9]{1,2})"),
    "Time Survived": re.compile("(?:timesurvived\(){e<=2}(.*?)(?:\]|\))"),
    "Kills": re.compile("(?:kills\(){e<=1}(.*?)(?:\]|\))"),
    "Damage": re.compile("(?:damagedone\(){e<=2}(.*?)(?:\]|\))"),
    "Revives": re.compile("(?:reviveally\(){e<=2}(.*?)(?:\]|\))"),
    "Respawns": re.compile("(?:respawnally\(){e<=2}(.*?)(?:\]|\))"),
    "Champions Killed": re.compile("(?:killedchampion\(){e<=2}(.*?)(?:\]|\))"),
    "Friends": re.compile("(?:playingwithfriends\(){e<=2}(.*?)(?:\]|\))"),
    "XP Earned": re.compile("(?:totalxpearned){1}(\d+)"),
}

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
