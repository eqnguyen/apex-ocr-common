from typing import Tuple

import numpy as np
from PIL.Image import Image

# Resolution: 1920 x 1080
# Regions of interest
ROI_DICT = {}

TOP_ROW_START = 120
PLAYER_ROW_START = 290
KAKN_ROW_START = 402
DAMAGE_ROW_START = 480
SURV_TIME_ROW_START = 556
REV_ROW_START = 632
RES_ROW_START = 708

TOP_ROW_HEIGHT = 62
PLAYER_ROW_HEIGHT = 32

SQUAD_PLACE_COL_START = 1345
TOTAL_KILL_COL_START = 1600
P1_COL_START = 125
P2_COL_START = 725
P3_COL_START = 1325

SQUAD_PLACE_WIDTH = 255
TOTAL_KILL_WIDTH = 220
PLAYER_WIDTH = 215
KAKN_WIDTH = 150
DAMAGE_WIDTH = 130
SURV_TIME_WIDTH = 130
REV_RES_WIDTH = 60

# Squad placement
SQUAD_PLACE_ROI = (
    SQUAD_PLACE_COL_START,
    TOP_ROW_START,
    SQUAD_PLACE_COL_START + SQUAD_PLACE_WIDTH,
    TOP_ROW_START + TOP_ROW_HEIGHT,
)

# Total kills
TOTAL_KILLS_ROI = (
    TOTAL_KILL_COL_START,
    TOP_ROW_START,
    TOTAL_KILL_COL_START + TOTAL_KILL_WIDTH,
    TOP_ROW_START + TOP_ROW_HEIGHT,
)

# Player 1
ROI_DICT["p1"] = {}
ROI_DICT["p1"]["player"] = (
    P1_COL_START,
    PLAYER_ROW_START,
    P1_COL_START + PLAYER_WIDTH,
    PLAYER_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p1"]["kakn"] = (
    P1_COL_START,
    KAKN_ROW_START,
    P1_COL_START + KAKN_WIDTH,
    KAKN_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p1"]["damage"] = (
    P1_COL_START,
    DAMAGE_ROW_START,
    P1_COL_START + DAMAGE_WIDTH,
    DAMAGE_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p1"]["survival_time"] = (
    P1_COL_START,
    SURV_TIME_ROW_START,
    P1_COL_START + SURV_TIME_WIDTH,
    SURV_TIME_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p1"]["revives"] = (
    P1_COL_START,
    REV_ROW_START,
    P1_COL_START + REV_RES_WIDTH,
    REV_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p1"]["respawns"] = (
    P1_COL_START,
    RES_ROW_START,
    P1_COL_START + REV_RES_WIDTH,
    RES_ROW_START + PLAYER_ROW_HEIGHT,
)

# Player 2
ROI_DICT["p2"] = {}
ROI_DICT["p2"]["player"] = (
    P2_COL_START,
    PLAYER_ROW_START,
    P2_COL_START + PLAYER_WIDTH,
    PLAYER_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p2"]["kakn"] = (
    P2_COL_START,
    KAKN_ROW_START,
    P2_COL_START + KAKN_WIDTH,
    KAKN_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p2"]["damage"] = (
    P2_COL_START,
    DAMAGE_ROW_START,
    P2_COL_START + DAMAGE_WIDTH,
    DAMAGE_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p2"]["survival_time"] = (
    P2_COL_START,
    SURV_TIME_ROW_START,
    P2_COL_START + SURV_TIME_WIDTH,
    SURV_TIME_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p2"]["revives"] = (
    P2_COL_START,
    REV_ROW_START,
    P2_COL_START + REV_RES_WIDTH,
    REV_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p2"]["respawns"] = (
    P2_COL_START,
    RES_ROW_START,
    P2_COL_START + REV_RES_WIDTH,
    RES_ROW_START + PLAYER_ROW_HEIGHT,
)

# Player 3
ROI_DICT["p3"] = {}
ROI_DICT["p3"]["player"] = (
    P3_COL_START,
    PLAYER_ROW_START,
    P3_COL_START + PLAYER_WIDTH,
    PLAYER_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p3"]["kakn"] = (
    P3_COL_START,
    KAKN_ROW_START,
    P3_COL_START + KAKN_WIDTH,
    KAKN_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p3"]["damage"] = (
    P3_COL_START,
    DAMAGE_ROW_START,
    P3_COL_START + DAMAGE_WIDTH,
    DAMAGE_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p3"]["survival_time"] = (
    P3_COL_START,
    SURV_TIME_ROW_START,
    P3_COL_START + SURV_TIME_WIDTH,
    SURV_TIME_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p3"]["revives"] = (
    P3_COL_START,
    REV_ROW_START,
    P3_COL_START + REV_RES_WIDTH,
    REV_ROW_START + PLAYER_ROW_HEIGHT,
)
ROI_DICT["p3"]["respawns"] = (
    P3_COL_START,
    RES_ROW_START,
    P3_COL_START + REV_RES_WIDTH,
    RES_ROW_START + PLAYER_ROW_HEIGHT,
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
