import enum
import logging
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import DefaultDict, List, Tuple, Union

import numpy as np
import pytesseract
import yaml
from joblib import Parallel, delayed, parallel_backend
from paddleocr import PaddleOCR
from PIL import Image, ImageGrab

from apex_ocr import utils
from apex_ocr.config import (
    DATA_DIRECTORY,
    DATABASE,
    DATABASE_YML_FILE,
    SQUAD_STATS_FILE,
    SQUAD_SUMMARY_HEADERS,
    SQUAD_SUMMARY_MAP,
    TESSERACT_BLOCK_CONFIG,
    TESSERACT_CONFIG,
)
from apex_ocr.database.api import ApexDatabaseApi
from apex_ocr.preprocessing import preprocess_image
from apex_ocr.roi import SUMMARY_ROI, TOP_SCREEN, TOTAL_KILLS_ROI, get_rois

logger = logging.getLogger(__name__)


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

        self.initialize_database_engine()

    @staticmethod
    def reformat_results(results: dict) -> dict:
        # Copy dictionary
        reformatted_dict = results.copy()

        # Pop datetime because this is likely changing
        reformatted_dict.pop("Datetime")

        # Add player key to results dictionary
        reformatted_dict["players"] = {}

        # Iterate over the three players
        for player in ["P1", "P2", "P3"]:
            # Initialize nested dictionary for player
            player_name = reformatted_dict[player]
            reformatted_dict["players"][player_name] = {}

            # Remove player key from dictionary
            del reformatted_dict[player]

            # Iterate over stats for individual player
            for field in [
                "Kills",
                "Assists",
                "Knocks",
                "Damage",
                "Time Survived",
                "Revives",
                "Respawns",
            ]:
                reformatted_dict["players"][player_name] = reformatted_dict[
                    f"{player} {field}"
                ]

                # Remove key from dictionary
                del reformatted_dict[f"{player} {field}"]

        return reformatted_dict

    @staticmethod
    def process_kakn(text: str) -> Tuple[int, int, int]:
        # Try to fix misdetected slashes
        if len(text) == 5 and re.search(r"\d+/\d+/\d+", text) is None:
            text = "/".join([text[0], text[2], text[4]])

        # Remove non-numeric and non-slash characters
        text = re.sub("[^0-9/]", "", text)

        # Split text into kills/assitss/knockdowns
        parts = text.split("/")

        if len(parts) == 3:
            try:
                return int(parts[0]), int(parts[1]), int(parts[2])
            except ValueError as e:
                logger.debug(f"Kills/Assists/Knocks misinterpreted: {parts}")
                return -1, -1, -1
        else:
            logger.debug(f"Kills/Assists/Knocks misinterpreted: {parts}")
            return -1, -1, -1

    @staticmethod
    def process_time_survived(text_list: List[str]) -> List[str]:
        time_survived_list = []

        for time_text in text_list:
            try:
                if len(time_text) > 4:
                    time_text = f"{time_text[:-4]}:{time_text[-4:-2]}:{time_text[-2:]}"
                elif len(time_text) > 2:
                    time_text = f"{time_text[:-2]}:{time_text[-2:]}"
                time_survived_list.append(time_text)
            except:
                time_survived_list.append("0")

        return time_survived_list

    @staticmethod
    def text_from_image_tesseract(
        image: np.ndarray,
        blur_amount: int,
        config: str = TESSERACT_CONFIG,
        debug: bool = False,
    ) -> str:
        img = preprocess_image(image, blur_amount)
        if debug:
            Image.fromarray(img).save(
                DATA_DIRECTORY
                / f"roi_preprocessed_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            )
        text = pytesseract.image_to_string(img, config=config)
        text = text.replace("\n", "").replace(" ", "").lower()
        return text

    def initialize_database_engine(self):
        if DATABASE:
            with open(DATABASE_YML_FILE) as db_file:
                db_config = yaml.load(db_file, Loader=yaml.FullLoader)

            dialect = db_config["dialect"]
            username = db_config["username"]
            password = db_config["password"]
            hostname = db_config["hostname"]
            port = db_config["port"]
            database_name = db_config["database_name"]

            db_conn_str = (
                f"{dialect}://{username}:{password}@{hostname}:{port}/{database_name}"
            )

            self.db_conn = ApexDatabaseApi(db_conn_str)
        else:
            self.db_conn = None

    def text_from_image_paddleocr(self, image: np.ndarray, blur_amount: int) -> str:
        img = preprocess_image(image, blur_amount)
        texts = self.paddle_ocr.ocr(img, cls=False)[0]

        # Concatenate all the recognized strings together
        text = ""
        for t in texts:
            text += t[1][0]
        text = text.replace("\n", "").replace(" ", "").lower()

        return text

    def classify_summary_page(
        self, input: Union[Path, np.ndarray, None] = None, debug: bool = False
    ) -> Union[SummaryType, None]:
        if input:
            if isinstance(input, np.ndarray):
                image = Image.fromarray(input)
            elif isinstance(input, Path):
                image = Image.open(str(input))
        else:
            image = ImageGrab.grab(bbox=TOP_SCREEN)

        summary_img = np.array(image.crop(SUMMARY_ROI))
        total_kills_img = np.array(image.crop(TOTAL_KILLS_ROI))

        summary_text = self.text_from_image_paddleocr(summary_img, blur_amount=3)
        kills_text = self.text_from_image_paddleocr(total_kills_img, blur_amount=3)

        if debug:
            image.save(
                DATA_DIRECTORY
                / f"raw_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            )

            Image.fromarray(total_kills_img).save(
                DATA_DIRECTORY
                / f"preprocessed_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            )

            with open(
                DATA_DIRECTORY
                / f"text_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
                "w+",
            ) as f:
                f.write(f"{summary_text}\n{kills_text}")

        if "summary" in summary_text:
            # TODO: Classify different categories of squad summary
            if "xpbreakdown" in kills_text:
                return SummaryType.PERSONAL
            elif "totalkills" in kills_text:
                return SummaryType.SQUAD

        return None

    def process_squad_summary_page(
        self, image: Union[Path, np.ndarray, None] = None, debug: bool = False
    ) -> dict:
        if image:
            if isinstance(image, np.ndarray):
                dup_images = [Image.fromarray(image)] * self.num_images
            elif isinstance(image, Path):
                dup_images = [Image.open(image)] * self.num_images
        else:
            # Take duplicate images immediately to get the most common interpretation
            dup_images = [
                ImageGrab.grab(bbox=TOP_SCREEN) for _ in range(self.num_images)
            ]

        results_dict = defaultdict(None)
        results_dict["Datetime"] = datetime.utcnow()
        matches = defaultdict(list)

        if debug:
            dup_images[0].save(
                DATA_DIRECTORY
                / f"dup_image_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            )
        else:
            # Magic: Important when running in docker with joblib
            dup_images[0].load()

        logger.info("Processing squad summary...")

        with parallel_backend(
            "threading", n_jobs=len(self.blurs)
        ):  # , require='sharedmem'):
            # job_args = [[img, blur_amount, matches] for img, blur_amount in zip(dup_images, self.blurs)]
            # OCR for all the images captured, then assign interpretation to the associated stat
            Parallel()(
                delayed(self.process_squad_summary_page_helper)(
                    img, blur_amount, matches
                )
                for img, blur_amount in zip(dup_images, self.blurs)
            )

        # For each image, find the most common OCR text interpretation for each stat
        # If no available interpretations of the stat, assign the value "n/a"
        for k, v in matches.items():
            counts = Counter(v)
            most_common = counts.most_common(1)

            if len(most_common) > 0:
                results_dict[k] = most_common[0][0]
            else:
                results_dict[k] = "n/a"

        logger.info("Finished processing images")

        return results_dict

    def process_squad_summary_page_helper(
        self,
        img: Image.Image,
        blur_amount: int,
        matches: DefaultDict,
        debug: bool = False,
    ):
        if img is None:
            logger.error(f"img is None")
            exit(1)
        # Get regions of interest
        squad_place, total_kills, players = get_rois(img)

        if debug:
            img.save(
                DATA_DIRECTORY
                / f"img_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            )
            Image.fromarray(squad_place).save(
                DATA_DIRECTORY
                / f"squad_place_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            )
            Image.fromarray(total_kills).save(
                DATA_DIRECTORY
                / f"total_kills_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            )
            Image.fromarray(squad_place).save(
                DATA_DIRECTORY
                / f"squad_place_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            )

        # Get text from the images
        place_text = self.text_from_image_paddleocr(squad_place, blur_amount)
        total_kills_text = self.text_from_image_tesseract(
            total_kills, blur_amount, TESSERACT_BLOCK_CONFIG
        )  # Want to replace tesseract here but PaddleOCR can't handle squad kills of 1 :(

        # Get squad placement
        matches["Place"].extend(
            utils.replace_nondigits(SQUAD_SUMMARY_MAP["Place"].findall(place_text))
        )

        # Get squad kills
        matches["Squad Kills"].extend(
            utils.replace_nondigits(
                SQUAD_SUMMARY_MAP["Squad Kills"].findall(total_kills_text)
            )
        )

        # Get individual player stat
        for player, player_dict in players.items():
            # Get player username
            matches[player.upper()].append(
                self.text_from_image_paddleocr(
                    player_dict["player"],
                    blur_amount,
                )
            )

            # Get player kills/assists/knockdowns
            kakn_text = self.text_from_image_paddleocr(player_dict["kakn"], blur_amount)
            kills, assists, knocks = self.process_kakn(kakn_text)
            matches[f"{player.upper()} Kills"].append(kills)
            matches[f"{player.upper()} Assists"].append(assists)
            matches[f"{player.upper()} Knocks"].append(knocks)

            # Get player damage
            matches[f"{player.upper()} Damage"].append(
                self.text_from_image_paddleocr(player_dict["damage"], blur_amount)
            )

            # Get player survival time
            time_text = self.text_from_image_paddleocr(
                player_dict["survival_time"], blur_amount
            )
            if len(time_text) >= 3 and ":" not in time_text:
                time_text = ":".join([time_text[:-2], time_text[-2:]])
            matches[f"{player.upper()} Time Survived"].append(time_text)

            # Get player revives
            revive_text = self.text_from_image_paddleocr(
                player_dict["revives"], blur_amount
            )
            matches[f"{player.upper()} Revives"].append(revive_text)

            # Get player respawns
            respawn_text = self.text_from_image_paddleocr(
                player_dict["respawns"],
                blur_amount,
            )
            matches[f"{player.upper()} Respawns"].append(respawn_text)

    def process_screenshot(self, image: Union[Path, np.ndarray, None] = None) -> None:
        summary_type = self.classify_summary_page(image)
        results_dict = {}

        if summary_type == SummaryType.PERSONAL:
            pass

        elif summary_type == SummaryType.SQUAD:
            results_dict = self.process_squad_summary_page(image)

        if results_dict:
            d = ApexOCREngine.reformat_results(results_dict)
            results_dict["Hash"] = utils.hash_dict(d)
            utils.display_results(results_dict)

            # Currently only supporting squad stats
            # Will need to change this if there is another output filepath or format
            if utils.write_to_file(
                SQUAD_STATS_FILE, SQUAD_SUMMARY_HEADERS, results_dict
            ):
                logger.info(f"Finished writing results to {SQUAD_STATS_FILE.name}")

            if DATABASE and self.db_conn is not None:
                self.db_conn.push_results(results_dict)
