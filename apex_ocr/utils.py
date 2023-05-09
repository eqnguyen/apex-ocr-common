import csv
import hashlib
import json
import logging
from typing import List

import numpy as np
import pandas as pd
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

try:
    import winsound
except ImportError:
    import os

    def beep(beep_freq: int = 500, duration: float = 0.05, volume: float = 0.5) -> int:
        return os.system(
            f"play -q -n -t alsa synth {duration} sine {beep_freq} vol {volume}"
        )

    # test if beep is able to run
    return_code = beep(volume=0)
    if return_code != 0:
        if return_code == 32512:
            logger.error(
                f"The package sox is not installed. Please install it ('sudo apt install sox')"
            )
        else:
            logger.error(
                f"sox appears to be installed, but there was some other problem with it {return_code=}"
            )

        def bad_beep(beep_freq: int = 500, duration: float = 0.05, volume: float = 0.5):
            logger.warning(f"Beep not available on this system")
            return -1

        beep = bad_beep

else:

    def beep(beep_freq: int = 500, duration: float = 0.05, volume: float = 0.5) -> int:
        return winsound.Beep(beep_freq, 500)


def log_and_beep(print_text: str, beep_freq: int) -> None:
    logger.info(print_text)
    if beep_freq:
        beep(beep_freq)


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
        subtitle=results["Hash"],
    )
    console.print(f"\n{panel}")


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


# Make a json string from the sorted dictionary then hash that string
def hash_dict(d: dict) -> str:
    """Compute sha256 hash of dictionary. Supports nested dictionaries.
    Taken from https://ardunn.us/posts/immutify_dictionary/.

    Args:
        d (dict): Input dictionary to hash.

    Returns:
        str: Hash string.
    """

    # Collapse the dictionary to a single representation
    def immutify_dictionary(d):
        d_new = {}
        for k, v in d.items():
            # convert to python native immutables
            if isinstance(v, (np.ndarray, pd.Series)):
                d_new[k] = tuple(v.tolist())

            # immutify any lists
            elif isinstance(v, list):
                d_new[k] = tuple(v)

            # recursion if nested
            elif isinstance(v, dict):
                d_new[k] = immutify_dictionary(v)

            # ensure numpy "primitives" are casted to json-friendly python natives
            else:
                # convert numpy types to native
                if hasattr(v, "dtype"):
                    d_new[k] = v.item()
                else:
                    d_new[k] = v

        return dict(sorted(d_new.items(), key=lambda item: item[0]))

    d_hashable = immutify_dictionary(d)
    s_hashable = json.dumps(d_hashable).encode("utf-8")
    m = hashlib.sha256(s_hashable).hexdigest()
    return m


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

    # TODO: Parse file for duplicate hash

    with open(filepath, write_method, newline="") as f:
        writer = csv.writer(f)
        for row in rows_to_write:
            writer.writerow(row)

    return True
