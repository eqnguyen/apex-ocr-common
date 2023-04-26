import csv
import hashlib
import json
import logging
import winsound
from typing import Any, Dict, List

from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from apex_ocr.config import *

logger = logging.getLogger(__name__)
console = Console()

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


def log_and_beep(print_text: str, beep_freq: int) -> None:
    logger.info(print_text)
    if beep_freq:
        winsound.Beep(beep_freq, 500)


def display_results(results: dict) -> None:
    player_tables = [
        Table(show_header=False),
        Table(show_header=False),
        Table(show_header=False),
    ]

    for i, player in enumerate(["P1", "P2", "P3"]):
        player_tables[i].title = results[player]

        for stat in [
            "Kills",
            "Assists",
            "Knocks",
            "Damage",
            "Time Survived",
            "Revives",
            "Respawns",
        ]:
            player_tables[i].add_row(stat, str(results[player + " " + stat]))

    panel = Panel(
        Align.center(Columns(player_tables)),
        title=f"[green]Squad Placed: #{results['Place']} - [red]Squad Kills: {results['Squad Kills']}",
        padding=(1, 2),
        expand=False,
        subtitle=dict_hash(results, ["Datetime"]),
    )
    console.print(panel)


def replace_nondigits(parsed_string: List[str]) -> List[int]:
    # Making sure the fields that should be numeric are numeric
    numeric_list = []

    for s in parsed_string:
        for old, new in REPLACEMENTS:
            s = s.replace(old, new)

        try:
            numeric_list.append(int(s))
        except:
            continue

    return numeric_list


def equal_dicts(d1: dict, d2: dict, ignore_keys: List[str]) -> bool:
    ignored = set(ignore_keys)

    # Compare keys in d1 with d2 and values in d1 with values in d2
    for k1, v1 in d1.items():
        if k1 in ignored:
            continue
        if k1 not in d2 or d2[k1] != v1:
            return False

    # Compare keys in d2 with d1
    for k2 in d2:
        if k2 in ignored:
            continue
        if k2 not in d1:
            return False

    return True


def time_survived_to_seconds(survival_time: str) -> int:
    time_survived = 0
    split_text = survival_time.split(":")

    for i, value in enumerate(reversed(split_text)):
        time_survived += (60**i) * int(value)

    return time_survived


def dict_hash(dictionary: Dict[str, Any], ignore: List[str] = []) -> str:
    """MD5 hash of a dictionary.
    Taken from https://www.doc.ic.ac.uk/~nuric/coding/how-to-hash-a-dictionary-in-python.html
    """
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}

    dict_copy = dictionary.copy()

    for key in ignore:
        dict_copy.pop(key)

    encoded = json.dumps(dict_copy, sort_keys=True, default=str).encode()
    dhash.update(encoded)

    return dhash.hexdigest()


def write_to_file(filepath: Path, headers: List[str], data: dict) -> bool:
    try:
        value_list = [data[header] for header in headers]
    except KeyError as key:
        logger.error(f"{key} does not exist in data!")
        return False

    if filepath.is_file():
        # Append the game data
        write_method = "a"
        rows_to_write = [value_list]
    else:
        # Write header row then game data
        write_method = "w"
        rows_to_write = [headers, value_list]

    with open(filepath, write_method, newline="") as f:
        writer = csv.writer(f)
        for row in rows_to_write:
            writer.writerow(row)

    return True
