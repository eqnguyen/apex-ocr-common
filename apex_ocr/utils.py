import csv
import hashlib
import json
import logging
import winsound
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from screeninfo import Monitor, get_monitors

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


def get_primary_monitor() -> Monitor:
    primary_monitor = Monitor(0, 0, 0, 0)
    for m in get_monitors():
        if m.is_primary:
            primary_monitor = m
            break
    else:
        logger.exception("No primary monitor detected!")

    return primary_monitor


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
            player_tables[i].add_row(stat, str(results[f"{player} {stat}"]))

    panel = Panel(
        Align.center(Columns(player_tables)),
        title=f"[green]Squad Placed: #{results['Place']} - [red]Squad Kills: {results['Squad Kills']}",
        padding=(1, 2),
        expand=False,
        subtitle=results["Hash"],
    )
    console.print("\n")
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
        try:
            time_survived += (60**i) * int(value)
        except ValueError:
            raise ValueError(
                f"ValueError: Invalid survival time string: {survival_time}"
            )

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
