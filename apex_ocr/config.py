from pathlib import Path

import regex

# Path to stats file
PERSONAL_STATS_FILE = Path(__file__).parent.parent / "data" / "personal_stats.csv"
SQUAD_STATS_FILE = Path(__file__).parent.parent / "data" / "squad_stats.csv"

# Bounding boxes for image grabs
TOP_SCREEN = (0, 0, 1920, 250)
XP_BREAKDOWN = (200, 200, 1024, 625)
FULL_SCREEN = (0, 0, 1920, 1080)

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
]

SQUAD_SUMMARY_HEADERS = [
    "Datetime",
    "Place",
    "Suqad Kills",
    "Player",
    "Kills",
    "Assists",
    "Knocks",
    "Damage",
    "Time Survived",
    "Revives",
    "Respawns",
]


REPLACEMENTS = [
    ("x", ""),
    ("d", "0"),
    ("D", "0"),
    ("o", "0"),
    ("O", "0"),
    ("!", "1"),
    ("l", "1"),
    ("I", "1"),
    ("}", ")"),
    ("{", "("),
    ("]", ")"),
    ("[", "("),
    ("$", ""),
    ("'", ""),
    ('"', ""),
]

TESSERACT_CONFIG = "-c tessedit_char_whitelist=()/#01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz --psm 12"

PERSONAL_SUMMARY_MAP = {
    "Place": regex.compile("#([0-9]{1,2})"),
    "Time Survived": regex.compile("(?:timesurvived\(){e<=2}(.*?)(?:\]|\))"),
    "Kills": regex.compile("(?:kills\(){e<=1}(.*?)(?:\]|\))"),
    "Damage": regex.compile("(?:damagedone\(){e<=2}(.*?)(?:\]|\))"),
    "Revives": regex.compile("(?:reviveally\(){e<=2}(.*?)(?:\]|\))"),
    "Respawns": regex.compile("(?:respawnally\(){e<=2}(.*?)(?:\]|\))"),
    "Champions Killed": regex.compile("(?:killedchampion\(){e<=2}(.*?)(?:\]|\))"),
    "Friends": regex.compile("(?:playingwithfriends\(){e<=2}(.*?)(?:\]|\))"),
    "XP Earned": regex.compile("(?:totalxpearned){1}(\d+)"),
}

# Tuning parameters
NUM_IMAGES_PER_BLUR = 1
BLUR_LEVELS = [1, 3, 5, 7, 9]
