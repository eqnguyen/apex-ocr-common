from typing import Tuple

import numpy as np
from PIL.Image import Image

# Resolution: 1920 x 1080
# Regions of interest
roi = {}

top_row_start = 120
player_row_start = 290
kakn_row_start = 402
damage_row_start = 480
surv_time_row_start = 556
rev_row_start = 632
res_row_start = 708

top_row_height = 62
player_row_height = 32

squad_place_col_start = 1345
total_kill_col_start = 1600
p1_col_start = 125
p2_col_start = 725
p3_col_start = 1325

squad_place_width = 255
total_kill_width = 220
player_width = 215
kakn_width = 150
damage_width = 130
surv_time_width = 130
rev_res_width = 60

# Squad placement
squad_place_roi = (
    squad_place_col_start,
    top_row_start,
    squad_place_col_start + squad_place_width,
    top_row_start + top_row_height,
)

# Total kills
total_kills_roi = (
    total_kill_col_start,
    top_row_start,
    total_kill_col_start + total_kill_width,
    top_row_start + top_row_height,
)

# Player 1
roi["p1"] = {}
roi["p1"]["player"] = (
    p1_col_start,
    player_row_start,
    p1_col_start + player_width,
    player_row_start + player_row_height,
)
roi["p1"]["kakn"] = (
    p1_col_start,
    kakn_row_start,
    p1_col_start + kakn_width,
    kakn_row_start + player_row_height,
)
roi["p1"]["damage"] = (
    p1_col_start,
    damage_row_start,
    p1_col_start + damage_width,
    damage_row_start + player_row_height,
)
roi["p1"]["survival_time"] = (
    p1_col_start,
    surv_time_row_start,
    p1_col_start + surv_time_width,
    surv_time_row_start + player_row_height,
)
roi["p1"]["revives"] = (
    p1_col_start,
    rev_row_start,
    p1_col_start + rev_res_width,
    rev_row_start + player_row_height,
)
roi["p1"]["respawns"] = (
    p1_col_start,
    res_row_start,
    p1_col_start + rev_res_width,
    res_row_start + player_row_height,
)

# Player 2
roi["p2"] = {}
roi["p2"]["player"] = (
    p2_col_start,
    player_row_start,
    p2_col_start + player_width,
    player_row_start + player_row_height,
)
roi["p2"]["kakn"] = (
    p2_col_start,
    kakn_row_start,
    p2_col_start + kakn_width,
    kakn_row_start + player_row_height,
)
roi["p2"]["damage"] = (
    p2_col_start,
    damage_row_start,
    p2_col_start + damage_width,
    damage_row_start + player_row_height,
)
roi["p2"]["survival_time"] = (
    p2_col_start,
    surv_time_row_start,
    p2_col_start + surv_time_width,
    surv_time_row_start + player_row_height,
)
roi["p2"]["revives"] = (
    p2_col_start,
    rev_row_start,
    p2_col_start + rev_res_width,
    rev_row_start + player_row_height,
)
roi["p2"]["respawns"] = (
    p2_col_start,
    res_row_start,
    p2_col_start + rev_res_width,
    res_row_start + player_row_height,
)

# Player 3
roi["p3"] = {}
roi["p3"]["player"] = (
    p3_col_start,
    player_row_start,
    p3_col_start + player_width,
    player_row_start + player_row_height,
)
roi["p3"]["kakn"] = (
    p3_col_start,
    kakn_row_start,
    p3_col_start + kakn_width,
    kakn_row_start + player_row_height,
)
roi["p3"]["damage"] = (
    p3_col_start,
    damage_row_start,
    p3_col_start + damage_width,
    damage_row_start + player_row_height,
)
roi["p3"]["survival_time"] = (
    p3_col_start,
    surv_time_row_start,
    p3_col_start + surv_time_width,
    surv_time_row_start + player_row_height,
)
roi["p3"]["revives"] = (
    p3_col_start,
    rev_row_start,
    p3_col_start + rev_res_width,
    rev_row_start + player_row_height,
)
roi["p3"]["respawns"] = (
    p3_col_start,
    res_row_start,
    p3_col_start + rev_res_width,
    res_row_start + player_row_height,
)


def get_rois(img: Image) -> Tuple[np.ndarray, np.ndarray, dict]:
    squad_place = np.array(img.crop(squad_place_roi))
    total_kill = np.array(img.crop(total_kills_roi))

    players = {}

    for player in roi.items():
        player_images = {}
        for stat in player[1].items():
            img_region = stat[1]
            player_images[stat[0]] = np.array(img.crop(img_region))
        players[player[0]] = player_images

    return squad_place, total_kill, players
