import logging

import gradio as gr
from PIL import Image
from PIL import ImageDraw
import json
from pathlib import Path

from utils import raise_error

logger = logging.getLogger(__name__)

RESOLUTION_DIR = Path("/home/apex/apex-ocr-common/apex_ocr/data/")


def adjust_image_bbox(min_x, min_y, max_x, max_y, image, bbox_label):
    if image is None or bbox_label is None or bbox_label == "":
        return image
    logger.info(f"{(min_x, min_y, max_x, max_y)=}")

    template_img = Image.fromarray(image)
    draw = ImageDraw.Draw(template_img)
    draw.rectangle((min_x, min_y, max_x, max_y), width=3)
    draw.text((max_x, max_y), bbox_label)

    return template_img


def adjust_slider_vals(image, bbox_label: str, x_min, y_min, x_max, y_max):
    if not(image is None or bbox_label is None or bbox_label == ""):
        width, height = Image.fromarray(image).size
        squad_place_roi, rois, total_kills_roi = load_bbox_template_file(width, height)

        if bbox_label == "Squad_Place":
            x_min, y_min, x_max, y_max = squad_place_roi
        elif bbox_label == "Total_Kills":
            x_min, y_min, x_max, y_max = total_kills_roi
        else:
            player, attribute = bbox_label.split(' ')
            if player in rois:
                if attribute in rois[player]:
                    x_min, y_min, x_max, y_max = rois[player][attribute]

    return gr.update(value = x_min), gr.update(value = y_min), gr.update(value = x_max), gr.update(value = y_max)


def adjust_slider_maximums(image):
    if image is None:
        x_max, y_max = 100, 100
    else:
        x_max, y_max = Image.fromarray(image).size
    return gr.update(maximum = x_max), gr.update(maximum = y_max), gr.update(maximum = x_max), gr.update(maximum = y_max)


def load_bbox_template_file(width, height):
    rois = {}
    res_file_name = f"{width}x{height}x0x0.json"
    resolution_file = RESOLUTION_DIR / res_file_name
    if resolution_file.exists():
        logger.info(f"ROI precalculated")
        rois = json.loads(resolution_file.read_text())
    return rois


def store_bbox_template_data(image, x_min:int, y_min:int, x_max:int, y_max:int, bbox_label: str):
    width, height = Image.fromarray(image).size
    squad_place_roi, rois, total_kills_roi = load_bbox_template_file(width, height)

    if bbox_label == "Squad_Place":
        squad_place_roi = x_min, y_min, x_max, y_max
    elif bbox_label == "Total_Kills":
        total_kills_roi = x_min, y_min, x_max, y_max
    else:
        player, attribute = bbox_label.split(' ')
        if player not in rois:
            rois[player] = {}
        rois[player][attribute] = [x_min, y_min, x_max, y_max]

    res_file_name = f"{width}x{height}x0x0.json"
    resolution_file = RESOLUTION_DIR / res_file_name
    with open(resolution_file, 'w') as f:
        f.write(json.dumps([squad_place_roi, rois, total_kills_roi], indent=4, sort_keys=True))

    return apply_bbox_template(image)


def apply_bbox_template(image):
    if image is None:
        return image
    bbox_img = Image.fromarray(image)
    
    width, height = bbox_img.size
    squad_place_roi, rois, total_kills_roi = load_bbox_template_file(width, height)

    draw = ImageDraw.Draw(bbox_img)

    draw.rectangle(squad_place_roi, width=3)
    draw.text(squad_place_roi[2:], "Squad Place")
    draw.rectangle(total_kills_roi, width=3)
    draw.text(total_kills_roi[2:], "Total Kills")

    for player, attributes in rois.items():
        for attr, (min_x, min_y, max_x, max_y) in attributes.items():
            draw.rectangle((min_x, min_y, max_x, max_y), width=3)
            draw.text((max_x, max_y), f"{player} {attr}")
    
    return bbox_img