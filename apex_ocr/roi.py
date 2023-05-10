import logging
from datetime import datetime
from typing import Tuple, Union

import numpy as np
from PIL import ImageDraw
from PIL.Image import Image

from apex_ocr.config import DATA_DIRECTORY
from apex_ocr.utils import get_primary_monitor

logger = logging.getLogger(__name__)

# Resolution: 1920 x 1080
# Regions of interest

PRIMARY_MONITOR = get_primary_monitor()

SUMMARY_ROI = ()

TOTAL_KILLS_ROI = ()

TOP_SCREEN = ()

ROI_DICT = {}
SQUAD_PLACE_ROI = ()

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
    "REV_RES_WIDTH": 60,
}


def scale_rois(resolution: Union[Tuple[int, int], None] = None):
    # resolution means we are analyzing screenshot(s)
    if resolution:
        width, height = resolution
        x, y = 0, 0
    else:
        width, height = PRIMARY_MONITOR.width, PRIMARY_MONITOR.height
        x, y = PRIMARY_MONITOR.x, PRIMARY_MONITOR.y

    for key, val in ROI_VARS.items():
        if "WIDTH" in key or "COL" in key:
            # scale by width
            ROI_VARS[key] = val * width // 1920
        elif "HEIGHT" in key or "ROW" in key:
            # scale by height
            ROI_VARS[key] = val * height // 1080
        else:
            logger.error(f"Unknown var: {key}")

    calculate_rois(width, height, x, y)


def calculate_rois(width: int, height: int, x: int, y: int):
    global SQUAD_PLACE_ROI, TOTAL_KILLS_ROI, ROI_DICT, SUMMARY_ROI, TOP_SCREEN

    logger.warning(SUMMARY_ROI)
    SUMMARY_ROI = (
        x + width // 3,
        y,
        x + width * 2 // 3,
        y + height // 10,
    )
    logger.warning(SUMMARY_ROI)

    TOP_SCREEN = (
        x,
        y,
        x + width,
        y + height,
    )

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
    ROI_DICT["P1"] = {}
    ROI_DICT["P1"]["player"] = (
        ROI_VARS["P1_COL_START"],
        ROI_VARS["PLAYER_ROW_START"],
        ROI_VARS["P1_COL_START"] + ROI_VARS["PLAYER_WIDTH"],
        ROI_VARS["PLAYER_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P1"]["kakn"] = (
        ROI_VARS["P1_COL_START"],
        ROI_VARS["KAKN_ROW_START"],
        ROI_VARS["P1_COL_START"] + ROI_VARS["KAKN_WIDTH"],
        ROI_VARS["KAKN_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P1"]["damage"] = (
        ROI_VARS["P1_COL_START"],
        ROI_VARS["DAMAGE_ROW_START"],
        ROI_VARS["P1_COL_START"] + ROI_VARS["DAMAGE_WIDTH"],
        ROI_VARS["DAMAGE_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P1"]["survival_time"] = (
        ROI_VARS["P1_COL_START"],
        ROI_VARS["SURV_TIME_ROW_START"],
        ROI_VARS["P1_COL_START"] + ROI_VARS["SURV_TIME_WIDTH"],
        ROI_VARS["SURV_TIME_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P1"]["revives"] = (
        ROI_VARS["P1_COL_START"],
        ROI_VARS["REV_ROW_START"],
        ROI_VARS["P1_COL_START"] + ROI_VARS["REV_RES_WIDTH"],
        ROI_VARS["REV_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P1"]["respawns"] = (
        ROI_VARS["P1_COL_START"],
        ROI_VARS["RES_ROW_START"],
        ROI_VARS["P1_COL_START"] + ROI_VARS["REV_RES_WIDTH"],
        ROI_VARS["RES_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )

    # Player 2
    ROI_DICT["P2"] = {}
    ROI_DICT["P2"]["player"] = (
        ROI_VARS["P2_COL_START"],
        ROI_VARS["PLAYER_ROW_START"],
        ROI_VARS["P2_COL_START"] + ROI_VARS["PLAYER_WIDTH"],
        ROI_VARS["PLAYER_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P2"]["kakn"] = (
        ROI_VARS["P2_COL_START"],
        ROI_VARS["KAKN_ROW_START"],
        ROI_VARS["P2_COL_START"] + ROI_VARS["KAKN_WIDTH"],
        ROI_VARS["KAKN_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P2"]["damage"] = (
        ROI_VARS["P2_COL_START"],
        ROI_VARS["DAMAGE_ROW_START"],
        ROI_VARS["P2_COL_START"] + ROI_VARS["DAMAGE_WIDTH"],
        ROI_VARS["DAMAGE_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P2"]["survival_time"] = (
        ROI_VARS["P2_COL_START"],
        ROI_VARS["SURV_TIME_ROW_START"],
        ROI_VARS["P2_COL_START"] + ROI_VARS["SURV_TIME_WIDTH"],
        ROI_VARS["SURV_TIME_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P2"]["revives"] = (
        ROI_VARS["P2_COL_START"],
        ROI_VARS["REV_ROW_START"],
        ROI_VARS["P2_COL_START"] + ROI_VARS["REV_RES_WIDTH"],
        ROI_VARS["REV_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P2"]["respawns"] = (
        ROI_VARS["P2_COL_START"],
        ROI_VARS["RES_ROW_START"],
        ROI_VARS["P2_COL_START"] + ROI_VARS["REV_RES_WIDTH"],
        ROI_VARS["RES_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )

    # Player 3
    ROI_DICT["P3"] = {}
    ROI_DICT["P3"]["player"] = (
        ROI_VARS["P3_COL_START"],
        ROI_VARS["PLAYER_ROW_START"],
        ROI_VARS["P3_COL_START"] + ROI_VARS["PLAYER_WIDTH"],
        ROI_VARS["PLAYER_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P3"]["kakn"] = (
        ROI_VARS["P3_COL_START"],
        ROI_VARS["KAKN_ROW_START"],
        ROI_VARS["P3_COL_START"] + ROI_VARS["KAKN_WIDTH"],
        ROI_VARS["KAKN_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P3"]["damage"] = (
        ROI_VARS["P3_COL_START"],
        ROI_VARS["DAMAGE_ROW_START"],
        ROI_VARS["P3_COL_START"] + ROI_VARS["DAMAGE_WIDTH"],
        ROI_VARS["DAMAGE_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P3"]["survival_time"] = (
        ROI_VARS["P3_COL_START"],
        ROI_VARS["SURV_TIME_ROW_START"],
        ROI_VARS["P3_COL_START"] + ROI_VARS["SURV_TIME_WIDTH"],
        ROI_VARS["SURV_TIME_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P3"]["revives"] = (
        ROI_VARS["P3_COL_START"],
        ROI_VARS["REV_ROW_START"],
        ROI_VARS["P3_COL_START"] + ROI_VARS["REV_RES_WIDTH"],
        ROI_VARS["REV_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )
    ROI_DICT["P3"]["respawns"] = (
        ROI_VARS["P3_COL_START"],
        ROI_VARS["RES_ROW_START"],
        ROI_VARS["P3_COL_START"] + ROI_VARS["REV_RES_WIDTH"],
        ROI_VARS["RES_ROW_START"] + ROI_VARS["PLAYER_ROW_HEIGHT"],
    )


def get_rois(img: Image, debug: bool = False) -> Tuple[np.ndarray, dict]:
    if debug:
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, 50, 50), width=3)
        draw.rectangle(SQUAD_PLACE_ROI, width=3)

    squad_place = np.array(img.crop(SQUAD_PLACE_ROI))

    players = {}

    for player in ROI_DICT.items():
        player_images = {}
        for stat in player[1].items():
            img_region = stat[1]
            player_images[stat[0]] = np.array(img.crop(img_region))
            if debug:
                draw.rectangle(img_region, width=3)
                draw.text(img_region[:1], stat)
        players[player[0]] = player_images

    if debug:
        image_path = DATA_DIRECTORY / f"rois_img_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.png"
        logger.debug(f"Debug roi image saved: {image_path}")
        img.save(image_path)

    return squad_place, players
