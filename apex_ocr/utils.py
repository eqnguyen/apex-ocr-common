import csv
import logging
import winsound
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Tuple

import cv2
import easyocr
import numpy as np
import pytesseract
from PIL import ImageGrab
from PIL.Image import Image
from tqdm import tqdm

from apex_ocr.config import *
from apex_ocr.roi import get_rois

logger = logging.getLogger("apex_ocr")

reader = easyocr.Reader(["en"])


def process_kakn(text: str) -> Tuple[int, int, int]:

    parts = text.split("/")

    if len(parts) == 3:
        return int(parts[0]), int(parts[1]), int(parts[2])
    else:
        logger.warning(f"Kills/Assists/Knocks misinterpreted: {parts}")


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


def log_and_beep(print_text: str, beep_freq: int) -> None:
    logger.info(print_text)
    if beep_freq:
        winsound.Beep(beep_freq, 500)


def get_text_from_image_tesseract(
    image: Image, blur_amount: int, config: str = TESSERACT_CONFIG
) -> str:
    img = preprocess_image(image, blur_amount)
    text = pytesseract.image_to_string(img, config=config)
    text = text.replace("\n", "").replace(" ", "").lower()
    return text


def get_text_from_image_easyocr(
    image: Image, blur_amount: int, allowlist: str = WHITELIST_CHARS
) -> str:
    img = preprocess_image(image, blur_amount)
    try:
        text = reader.readtext(
            img, paragraph=True, detail=0, text_threshold=0.3, allowlist=allowlist
        )[0].strip()
    except:
        return "0"

    return text


def process_squad_summary_page(blurs: List[int]) -> dict:
    # Take duplicate images immediately to get the most common interpretation
    num_images = len(blurs)

    dup_images = [ImageGrab.grab() for _ in range(num_images)]

    results_dict = defaultdict(None)
    results_dict["Datetime"] = datetime.now()
    matches = defaultdict(list)

    # OCR for all the images captured, then assign interpretation to the associated stat
    for img, blur_amount in tqdm(list(zip(dup_images, blurs))):
        # Get regions of interest
        squad_place, total_kills, players = get_rois(img)

        # Get text from the images
        place_text = get_text_from_image_tesseract(squad_place, blur_amount)
        total_kills_text = get_text_from_image_tesseract(
            total_kills, blur_amount, TESSERACT_BLOCK_CONFIG
        )

        for header in SQUAD_SUMMARY_HEADERS:
            if header == "Datetime":
                continue
            elif header == "Place":
                matches[header].extend(
                    replace_nondigits(SQUAD_SUMMARY_MAP[header].findall(place_text))
                )
            elif header == "Squad Kills":
                matches[header].extend(
                    replace_nondigits(
                        SQUAD_SUMMARY_MAP[header].findall(total_kills_text)
                    )
                )
            else:
                # Player section
                player = header.split(" ")[0].lower()

                if " " not in header:
                    matches[header].append(
                        get_text_from_image_easyocr(
                            players[player]["player"],
                            blur_amount,
                        )
                    )
                else:
                    category = header.split(" ")[1].lower()

                    if category == "kills":
                        kakn_text = get_text_from_image_easyocr(
                            players[player]["kakn"],
                            blur_amount,
                            NUMERIC_WHITELIST_CHARS,
                        )
                        if (
                            len(kakn_text) == 5
                            and regex.search(r"\d+/\d+/\d+", kakn_text) is None
                        ):
                            kakn_text = "/".join(
                                [kakn_text[0], kakn_text[2], kakn_text[4]]
                            )

                        try:
                            kills, assists, knocks = process_kakn(kakn_text)
                        except:
                            continue
                        matches[player.upper() + " Kills"].append(kills)
                        matches[player.upper() + " Assists"].append(assists)
                        matches[player.upper() + " Knocks"].append(knocks)
                    elif category == "assists":
                        continue
                    elif category == "knocks":
                        continue
                    elif category == "damage":
                        matches[header].extend(
                            get_text_from_image_easyocr(
                                players[player]["damage"],
                                blur_amount,
                                NUMERIC_WHITELIST_CHARS,
                            )
                        )
                    elif category == "time":
                        time_text = pytesseract.image_to_string(
                            img, config=TESSERACT_TIME_CONFIG
                        ).strip()
                        if len(time_text) >= 3 and ":" not in time_text:
                            time_text = ":".join([time_text[:-2], time_text[-2:]])
                        matches[header].append(time_text)
                    elif category == "revives":
                        revive_text = pytesseract.image_to_string(
                            img, TESSERACT_NUM_CONFIG
                        )
                        if revive_text == "":
                            revive_text = "0"
                        matches[header].append(revive_text)
                    elif category == "respawns":
                        respawn_text = get_text_from_image_easyocr(
                            players[player]["respawns"],
                            blur_amount,
                            NUMERIC_WHITELIST_CHARS,
                        )
                        if respawn_text == "":
                            respawn_text = "0"
                        matches[header].append(respawn_text)

    # For each image, find the most common OCR text interpretation for each stat
    # If no available interpretations of the stat, assign the value "n/a"
    for k, v in matches.items():
        counts = Counter(v)
        most_common = counts.most_common(1)

        if len(most_common) > 0:
            results_dict[k] = most_common[0][0]
        else:
            results_dict[k] = "n/a"

    log_and_beep("Processing images...", 1500)

    return results_dict


def process_personal_summary_page(blurs: List[int]) -> dict:
    # Take duplicate images immediately to get the most common interpretation
    num_images = len(blurs)

    dup_images = [ImageGrab.grab() for _ in range(num_images)]
    place_images = [img.crop(PERSONAL_SQUAD_PLACED) for img in dup_images]
    xp_images = [img.crop(XP_BREAKDOWN) for img in dup_images]

    results_dict = defaultdict(None)
    results_dict["Datetime"] = datetime.now()
    matches = defaultdict(list)

    log_and_beep("Processing images...", 1500)

    # OCR for all the images captured, then assign interpretation to the associated stat
    for place_image, xp_image, blur_amount in tqdm(
        list(zip(place_images, xp_images, blurs))
    ):
        # Get text from the images
        place_text = get_text_from_image_tesseract(place_image, blur_amount)
        xp_text = get_text_from_image_tesseract(xp_image, blur_amount)

        # Concatenate the image text
        text = place_text + xp_text

        logger.debug(f"Image text, blur={blur_amount}: {text}")

        for header, matcher in PERSONAL_SUMMARY_MAP.items():
            if header == "Time Survived":
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
