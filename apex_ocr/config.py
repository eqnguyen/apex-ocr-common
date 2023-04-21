from pathlib import Path

import regex

# Path to stats file
PERSONAL_STATS_FILE = Path(__file__).parent.parent / "data" / "personal_stats.csv"
SQUAD_STATS_FILE = Path(__file__).parent.parent / "data" / "squad_stats.csv"

# Bounding boxes for image grabs
TOP_SCREEN = (0, 0, 1920, 250)
PERSONAL_SQUAD_PLACED = (1450, 0, 1720, 200)
XP_BREAKDOWN = (200, 200, 1024, 625)

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

WHITELIST_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789[]-_/"
NUMERIC_WHITELIST_CHARS = "DIOdilo0123456789!/"
TESSERACT_CONFIG = "-c tessedit_char_whitelist=()/#01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz --psm 11"
TESSERACT_BLOCK_CONFIG = "-c tessedit_char_whitelist=()/#01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz --psm 6"
TESSERACT_RESULT_CONFIG = "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789[]-_# --psm 6"
TESSERACT_PLAYER_CONFIG = "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789[]-_# --psm 7"
TESSERACT_KAKN_CONFIG = "-c tessedit_char_whitelist=/0123456789 --psm 7"
TESSERACT_TIME_CONFIG = "-c tessedit_char_whitelist=:0123456789 --psm 7"
TESSERACT_NUM_CONFIG = "-c tessedit_char_whitelist=0123456789 --psm 7"

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

SQUAD_SUMMARY_MAP = {
    "Place": regex.compile("#([0-9]{1,2})"),
    "Squad Kills": regex.compile("(?:totalkills){1}([dDoO!lI0-9]{1,2})"),
    "Player": regex.compile("#([0-9]{1,2})"),
    "Kills/Assists/Knocks": regex.compile(
        "(?:kills/assists/knocks){1}([dDoO!lI0-9]{1,2}/[dDoO!lI0-9]{1,2}/[dDoO!lI0-9]{1,2})"
    ),
    "Damage": regex.compile("(?:amagedealt){1}(\d+)"),
    "Time Survived": regex.compile("(?:survivaltime){1}(\d+)"),
    "Revives": regex.compile("(?:revivegiven){1}(\d+)"),
    "Respawns": regex.compile("(?:respawngiven){1}(\d+)"),
}
