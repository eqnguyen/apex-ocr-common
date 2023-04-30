from typing import Tuple

import numpy as np
from PIL.Image import Image
import logging

from screeninfo import get_monitors

logger = logging.getLogger(__name__)

# Resolution: 1920 x 1080
# Regions of interest
ROI_DICT = {}

ROI_VARS = {
    "TOP_ROW_START": 120,
    "PLAYER_ROW_START": 290,
    "KAKN_ROW_START": 402,
    "DAMAGE_ROW_START": 480,
    "SURV_TIME_ROW_START": 556,
    "REV_ROW_START": 632,
    "RES_ROW_START": 708,

    "TOP_ROW_HEIGHT": 62,
    "PLAYER_ROW_HEIGHT": 32,

    "SQUAD_PLACE_COL_START": 1345,
    "TOTAL_KILL_COL_START": 1600,
    "P1_COL_START": 125,
    "P2_COL_START": 725,
    "P3_COL_START": 1325,

    "SQUAD_PLACE_WIDTH": 255,
    "TOTAL_KILL_WIDTH": 220,
    "PLAYER_WIDTH": 215,
    "KAKN_WIDTH": 150,
    "DAMAGE_WIDTH": 130,
    "SURV_TIME_WIDTH": 130,
    "REV_RES_WIDTH": 60
}

def scale_rois():
    for m in get_monitors():
        primary_monitor = None
        if m.is_primary:
            primary_monitor = m
            break
    
    for key, val in ROI_VARS.items():
        if "WIDTH" in key:
            ROI_VARS[key] = val/1920 * primary_monitor.width
        elif "COL" in key:
            # scale by width
            ROI_VARS[key] = val/1920 * primary_monitor.width + primary_monitor.x
        elif "HEIGHT" in key:
            ROI_VARS[key] = val/1080 * primary_monitor.height
        elif "ROW" in key:
            # scale by height
            ROI_VARS[key] = val/1080 * primary_monitor.height + primary_monitor.y
        else:
            logger.error(f"Unknown var: {key}")

scale_rois()


# Squad placement
SQUAD_PLACE_ROI = (
    ROI_VARS["SQUAD_PLACE_COL_START"],
    ROI_VARS["TOP_ROW_START"],
    ROI_VARS["SQUAD_PLACE_COL_START"] + ROI_VARS["SQUAD_PLACE_WIDTH"],
    ROI_VARS["TOP_ROW_START"] + ROI_VARS["TOP_ROW_HEIGHT"],
)

# Total kills
TOTAL_KILLS_ROI = (
    ROI_VARS["TOTAL_KILL_COL_START"],
    ROI_VARS["TOP_ROW_START"],
    ROI_VARS["TOTAL_KILL_COL_START"] + ROI_VARS["TOTAL_KILL_WIDTH"],
    ROI_VARS["TOP_ROW_START"] + ROI_VARS["TOP_ROW_HEIGHT"],
)

# Player 1
ROI_DICT["p1"] = {}
ROI_DICT["p1"]["player"] = (
    ROI_VARS["P1_COL_START"],
    ROI_VARS["PLAYER_ROW_START"],
    ROI_VARS["P1_COL_START"] + ROI_VARS["PLAYER_WIDTH"],
    ROI_VARS["PLAYER_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p1"]["kakn"] = (
    ROI_VARS["P1_COL_START"],
    ROI_VARS["KAKN_ROW_START"],
    ROI_VARS["P1_COL_START"] + ROI_VARS["KAKN_WIDTH"],
    ROI_VARS["KAKN_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p1"]["damage"] = (
    ROI_VARS["P1_COL_START"],
    ROI_VARS["DAMAGE_ROW_START"],
    ROI_VARS["P1_COL_START"] + ROI_VARS["DAMAGE_WIDTH"],
    ROI_VARS["DAMAGE_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p1"]["survival_time"] = (
    ROI_VARS["P1_COL_START"],
    ROI_VARS["SURV_TIME_ROW_START"],
    ROI_VARS["P1_COL_START"] + ROI_VARS["SURV_TIME_WIDTH"],
    ROI_VARS["SURV_TIME_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p1"]["revives"] = (
    ROI_VARS["P1_COL_START"],
    ROI_VARS["REV_ROW_START"],
    ROI_VARS["P1_COL_START"] + ROI_VARS["REV_RES_WIDTH"],
    ROI_VARS["REV_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p1"]["respawns"] = (
    ROI_VARS["P1_COL_START"],
    ROI_VARS["RES_ROW_START"],
    ROI_VARS["P1_COL_START"] + ROI_VARS["REV_RES_WIDTH"],
    ROI_VARS["RES_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)

# Player 2
ROI_DICT["p2"] = {}
ROI_DICT["p2"]["player"] = (
    ROI_VARS["P2_COL_START"],
    ROI_VARS["PLAYER_ROW_START"],
    ROI_VARS["P2_COL_START"] + ROI_VARS["PLAYER_WIDTH"],
    ROI_VARS["PLAYER_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p2"]["kakn"] = (
    ROI_VARS["P2_COL_START"],
    ROI_VARS["KAKN_ROW_START"],
    ROI_VARS["P2_COL_START"] + ROI_VARS["KAKN_WIDTH"],
    ROI_VARS["KAKN_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p2"]["damage"] = (
    ROI_VARS["P2_COL_START"],
    ROI_VARS["DAMAGE_ROW_START"],
    ROI_VARS["P2_COL_START"] + ROI_VARS["DAMAGE_WIDTH"],
    ROI_VARS["DAMAGE_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p2"]["survival_time"] = (
    ROI_VARS["P2_COL_START"],
    ROI_VARS["SURV_TIME_ROW_START"],
    ROI_VARS["P2_COL_START"] + ROI_VARS["SURV_TIME_WIDTH"],
    ROI_VARS["SURV_TIME_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p2"]["revives"] = (
    ROI_VARS["P2_COL_START"],
    ROI_VARS["REV_ROW_START"],
    ROI_VARS["P2_COL_START"] + ROI_VARS["REV_RES_WIDTH"],
    ROI_VARS["REV_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p2"]["respawns"] = (
    ROI_VARS["P2_COL_START"],
    ROI_VARS["RES_ROW_START"],
    ROI_VARS["P2_COL_START"] + ROI_VARS["REV_RES_WIDTH"],
    ROI_VARS["RES_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)

# Player 3
ROI_DICT["p3"] = {}
ROI_DICT["p3"]["player"] = (
    ROI_VARS["P3_COL_START"],
    ROI_VARS["PLAYER_ROW_START"],
    ROI_VARS["P3_COL_START"] + ROI_VARS["PLAYER_WIDTH"],
    ROI_VARS["PLAYER_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p3"]["kakn"] = (
    ROI_VARS["P3_COL_START"],
    ROI_VARS["KAKN_ROW_START"],
    ROI_VARS["P3_COL_START"] + ROI_VARS["KAKN_WIDTH"],
    ROI_VARS["KAKN_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p3"]["damage"] = (
    ROI_VARS["P3_COL_START"],
    ROI_VARS["DAMAGE_ROW_START"],
    ROI_VARS["P3_COL_START"] + ROI_VARS["DAMAGE_WIDTH"],
    ROI_VARS["DAMAGE_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p3"]["survival_time"] = (
    ROI_VARS["P3_COL_START"],
    ROI_VARS["SURV_TIME_ROW_START"],
    ROI_VARS["P3_COL_START"] + ROI_VARS["SURV_TIME_WIDTH"],
    ROI_VARS["SURV_TIME_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p3"]["revives"] = (
    ROI_VARS["P3_COL_START"],
    ROI_VARS["REV_ROW_START"],
    ROI_VARS["P3_COL_START"] + ROI_VARS["REV_RES_WIDTH"],
    ROI_VARS["REV_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)
ROI_DICT["p3"]["respawns"] = (
    ROI_VARS["P3_COL_START"],
    ROI_VARS["RES_ROW_START"],
    ROI_VARS["P3_COL_START"] + ROI_VARS["REV_RES_WIDTH"],
    ROI_VARS["RES_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
)


def get_rois(img: Image) -> Tuple[np.ndarray, np.ndarray, dict]:
    squad_place = np.array(img.crop(SQUAD_PLACE_ROI))
    total_kill = np.array(img.crop(TOTAL_KILLS_ROI))

    players = {}

    for player in ROI_DICT.items():
        player_images = {}
        for stat in player[1].items():
            img_region = stat[1]
            player_images[stat[0]] = np.array(img.crop(img_region))
        players[player[0]] = player_images

    return squad_place, total_kill, players
