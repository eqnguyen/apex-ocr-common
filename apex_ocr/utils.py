import csv
import logging
import winsound
from collections import Counter, defaultdict
from datetime import datetime
from typing import List

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageGrab
from tqdm import tqdm

from apex_ocr.config import *

logger = logging.getLogger("apex_ocr")


def process_squad_placed(text_list: List[str]) -> List[str]:
    # For deciphering single-digit squad placement from multi-digit squad placement
    squad_placed_list = []
    for text in text_list:
        try:
            numeric_place = int(text)
            if numeric_place == 2 or numeric_place == 20:
                squad_placed_list.append(20)
            elif numeric_place == 1 or numeric_place == 10:
                squad_placed_list.append(10)
            elif numeric_place > 20:
                squad_placed_list.append(int(text[0]))
            else:
                squad_placed_list.append(numeric_place)
        except:
            squad_placed_list.append(0)
    return squad_placed_list


def process_time_survived(text_list: List[str]) -> List[str]:
    time_survived_list = []

    for time_text in text_list:
        try:
            if len(time_text) > 4:
                time_text = (
                    time_text[:-4] + ":" + time_text[-4:-2] + ":" + time_text[-2:]
                )
            elif len(time_text) > 2:
                time_text = time_text[:-2] + ":" + time_text[-2:]
            time_survived_list.append(time_text)
        except:
            time_survived_list.append("0")

    return time_survived_list


def preprocess_image(img: Image, blur_amount: int) -> Image:
    img = img.convert("RGB")
    opencv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    opencv_thr_img = cv2.threshold(
        opencv_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    if blur_amount > 0:
        return cv2.GaussianBlur(opencv_thr_img, (blur_amount, blur_amount), 0)
    else:
        return opencv_thr_img


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


def write_to_file(filepath: Path, data: dict) -> None:
    value_list = [data[header] for header in PERSONAL_SUMMARY_HEADERS]

    if filepath.is_file():
        # Append the game data
        write_method = "a"
        rows_to_write = [value_list]
    else:
        # Write header row then game data
        write_method = "w"
        rows_to_write = [PERSONAL_SUMMARY_HEADERS, value_list]

    with open(filepath, write_method, newline="") as f:
        writer = csv.writer(f)
        for row in rows_to_write:
            writer.writerow(row)


def log_and_beep(print_text: str, beep_freq: int) -> None:
    logger.info(print_text)
    if beep_freq:
        winsound.Beep(beep_freq, 500)


def process_squad_summary_page(blurs: List[int]) -> dict:
    # Take duplicate images immediately to get the most common (mode) interpretation later
    dup_images = [
        ImageGrab.grab(bbox=XP_BREAKDOWN)
        for _ in range(NUM_IMAGES_PER_BLUR * len(BLUR_LEVELS))
    ]

    results_dict = defaultdict(None)
    results_dict["Datetime"] = datetime.now()
    matches = defaultdict(list)

    log_and_beep("Processing images...", 1500)

    return results_dict


def process_personal_summary_page(blurs: List[int]) -> dict:
    # Take duplicate images immediately to get the most common (mode) interpretation later
    dup_images = [
        ImageGrab.grab(bbox=XP_BREAKDOWN)
        for _ in range(NUM_IMAGES_PER_BLUR * len(BLUR_LEVELS))
    ]

    results_dict = defaultdict(None)
    results_dict["Datetime"] = datetime.now()
    matches = defaultdict(list)

    log_and_beep("Processing images...", 1500)

    # OCR for all the images captured, then assign interpretation to the associated stat
    for image, blur_amount in tqdm(list(zip(dup_images, blurs))):
        # Preprocess the images
        img = preprocess_image(image, blur_amount)
        text = pytesseract.image_to_string(img, config=TESSERACT_CONFIG)
        text = text.replace("\n", "").replace(" ", "").lower()

        logger.debug(f"Image text, blur={blur_amount}: {text}")

        for header, matcher in PERSONAL_SUMMARY_MAP.items():
            if header == "Squad Placed":
                parsed_text = process_squad_placed(matcher.findall(text))
            elif header == "Time Survived":
                parsed_text = process_time_survived(matcher.findall(text))
            else:
                parsed_text = replace_nondigits(matcher.findall(text))
            matches[header].extend(parsed_text)

    # For each image, find the most common OCR text interpretation for each stat
    # If no available interpretations of the stat, assign the value "n/a"
    for k, v in matches.items():
        counts = Counter(v)
        most_common = counts.most_common(1)

        if len(most_common) > 0:
            results_dict[k] = most_common[0][0]
        else:
            results_dict[k] = "n/a"

    log_and_beep(
        f"Finished processing images: {results_dict}",
        1000,
    )

    return results_dict
