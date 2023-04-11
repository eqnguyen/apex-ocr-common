import enum
import logging
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Tuple, Union

import numpy as np
import pytesseract
from paddleocr import PaddleOCR
from PIL import Image, ImageGrab
from tqdm import tqdm

from apex_ocr.config import *
from apex_ocr.preprocessing import *
from apex_ocr.roi import get_rois
from apex_ocr.utils import *

logger = logging.getLogger("ApexOCREngine")


class SummaryType(enum.Enum):
    SQUAD = 1
    PERSONAL = 2


class ApexOCREngine:
    def __init__(self, n_images_per_blur: int = 1, blur_levels=[0, 3, 5, 7]) -> None:
        self.paddle_ocr = PaddleOCR(
            use_angle_cls=True, lang="en", show_log=False, debug=False
        )

        self.blurs = []
        for blur_level in blur_levels:
            self.blurs.extend([blur_level] * n_images_per_blur)

        self.num_images = len(self.blurs)

    @staticmethod
    def preprocess_image(image: np.ndarray, blur_amount: int = 0) -> np.ndarray:
        grayscale_img = grayscale(image)
        threshold_img = thresholding(grayscale_img)

        if blur_amount > 0:
            return cv2.GaussianBlur(threshold_img, (blur_amount, blur_amount), 0)
        else:
            return threshold_img

    @staticmethod
    def process_kakn(text: str) -> Tuple[int, int, int]:
        parts = text.split("/")

        if len(parts) == 3:
            return int(parts[0]), int(parts[1]), int(parts[2])
        else:
            logger.warning(f"Kills/Assists/Knocks misinterpreted: {parts}")
            return -1, -1, -1

    @staticmethod
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

    @staticmethod
    def classify_summary_page(
        image: Union[Path, np.ndarray, None] = None
    ) -> Union[SummaryType, None]:
        if image:
            if isinstance(image, np.ndarray):
                img = image
            elif isinstance(image, Path):
                img = cv2.imread(str(image))
        else:
            img = np.array(ImageGrab.grab(bbox=TOP_SCREEN))

        img = ApexOCREngine.preprocess_image(img, blur_amount=3)
        text = pytesseract.image_to_string(img, config=TESSERACT_CONFIG)
        text = text.replace("\n", "").replace(" ", "").lower()

        if "summary" in text:
            if "xpbreakdown" in text:
                return SummaryType.PERSONAL
            elif "totalkills" in text:
                return SummaryType.SQUAD
        else:
            return None

    @staticmethod
    def text_from_image_tesseract(
        image: np.ndarray, blur_amount: int, config: str = TESSERACT_CONFIG
    ) -> str:
        img = ApexOCREngine.preprocess_image(image, blur_amount)
        text = pytesseract.image_to_string(img, config=config)
        text = text.replace("\n", "").replace(" ", "").lower()
        return text

    def text_from_image_paddleocr(self, image: np.ndarray, blur_amount: int) -> str:
        img = self.preprocess_image(image, blur_amount)
        texts = self.paddle_ocr.ocr(img, det=False, cls=False)[0]

        # Concatenate all the recognized strings together
        text = ""
        for t in texts:
            text += t[0]
        text = text.replace("\n", "").replace(" ", "").lower()

        return text

    def process_squad_summary_page(
        self, image: Union[Path, np.ndarray, None] = None
    ) -> dict:
        if image:
            if isinstance(image, np.ndarray):
                dup_images = [Image.fromarray(image)] * self.num_images
            elif isinstance(image, Path):
                dup_images = [Image.open(image)] * self.num_images
        else:
            # Take duplicate images immediately to get the most common interpretation
            dup_images = [ImageGrab.grab() for _ in range(self.num_images)]

        results_dict = defaultdict(None)
        results_dict["Datetime"] = datetime.now()
        matches = defaultdict(list)

        # OCR for all the images captured, then assign interpretation to the associated stat
        for img, blur_amount in tqdm(list(zip(dup_images, self.blurs))):
            # Get regions of interest
            squad_place, total_kills, players = get_rois(img)

            # Get text from the images
            place_text = self.text_from_image_tesseract(squad_place, blur_amount)
            total_kills_text = self.text_from_image_tesseract(
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
                            self.text_from_image_paddleocr(
                                players[player]["player"],
                                blur_amount,
                            )
                        )
                    else:
                        category = header.split(" ")[1].lower()

                        if category == "kills":
                            kakn_text = self.text_from_image_paddleocr(
                                players[player]["kakn"], blur_amount
                            )
                            if (
                                len(kakn_text) == 5
                                and regex.search(r"\d+/\d+/\d+", kakn_text) is None
                            ):
                                kakn_text = "/".join(
                                    [kakn_text[0], kakn_text[2], kakn_text[4]]
                                )

                            try:
                                kills, assists, knocks = self.process_kakn(kakn_text)
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
                            matches[header].append(
                                self.text_from_image_paddleocr(
                                    players[player]["damage"], blur_amount
                                )
                            )
                        elif category == "time":
                            time_text = self.text_from_image_paddleocr(
                                players[player]["survival_time"], blur_amount
                            )
                            if len(time_text) >= 3 and ":" not in time_text:
                                time_text = ":".join([time_text[:-2], time_text[-2:]])
                            matches[header].append(time_text)
                        elif category == "revives":
                            revive_text = self.text_from_image_paddleocr(
                                players[player]["revives"], blur_amount
                            )
                            matches[header].append(revive_text)
                        elif category == "respawns":
                            respawn_text = self.text_from_image_paddleocr(
                                players[player]["respawns"],
                                blur_amount,
                            )
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

        log_and_beep(
            f"Finished processing images: {results_dict}",
            1000,
        )

        return results_dict

    def process_personal_summary_page(
        self, image: Union[Path, np.ndarray, None] = None
    ) -> dict:
        if image:
            if isinstance(image, np.ndarray):
                dup_images = [Image.fromarray(image)] * self.num_images
            elif isinstance(image, Path):
                dup_images = [Image.open(image)] * self.num_images
        else:
            # Take duplicate images immediately to get the most common interpretation
            dup_images = [ImageGrab.grab() for _ in range(self.num_images)]

        place_images = [np.array(img.crop(PERSONAL_SQUAD_PLACED)) for img in dup_images]
        xp_images = [np.array(img.crop(XP_BREAKDOWN)) for img in dup_images]

        results_dict = defaultdict(None)
        results_dict["Datetime"] = datetime.now()
        matches = defaultdict(list)

        log_and_beep("Processing images...", 1500)

        # OCR for all the images captured, then assign interpretation to the associated stat
        for place_image, xp_image, blur_amount in tqdm(
            list(zip(place_images, xp_images, self.blurs))
        ):
            # Get text from the images
            place_text = self.text_from_image_paddleocr(place_image, blur_amount)
            xp_text = self.text_from_image_tesseract(xp_image, blur_amount)

            # Concatenate the image text
            text = place_text + xp_text

            logger.debug(f"Image text, blur={blur_amount}: {text}")

            for header, matcher in PERSONAL_SUMMARY_MAP.items():
                if header == "Time Survived":
                    parsed_text = self.process_time_survived(matcher.findall(text))
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
