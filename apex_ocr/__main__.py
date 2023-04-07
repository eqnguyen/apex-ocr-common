import logging
import time

from tqdm import tqdm

from apex_ocr.config import *
from apex_ocr.utils import *

logging.captureWarnings(True)
logger = logging.getLogger("apex_ocr")

# TODO: Add specific ROI for squad placement


def main():
    logger.info("Watching screen...")

    blurs = []
    for blur_level in BLUR_LEVELS:
        blurs.extend([blur_level] * NUM_IMAGES_PER_BLUR)

    last_personal_results = {}
    last_squad_results = {}

    while True:
        # Initialize boolean flag for new result
        new_result = False

        # Continuously grab screenshots and interpret them to identify the match summary screen
        img = preprocess_image(ImageGrab.grab(bbox=TOP_SCREEN), 3)
        text = pytesseract.image_to_string(img, config=TESSERACT_CONFIG)
        text = text.replace("\n", "").replace(" ", "").lower()

        if "summary" in text:
            if "xpbreakdown" in text:
                log_and_beep("Personal summary screen detected", 2000)
                results_dict = process_personal_summary_page(blurs)
                output_path = PERSONAL_STATS_FILE
                headers = PERSONAL_SUMMARY_HEADERS

                if not equal_dicts(last_personal_results, results_dict, ["Datetime"]):
                    last_personal_results = results_dict.copy()
                    new_result = True

            elif "totalkills" in text:
                log_and_beep("Squad summary screen detected", 2000)
                results_dict = process_squad_summary_page(blurs)
                output_path = SQUAD_STATS_FILE
                headers = SQUAD_SUMMARY_HEADERS

                if not equal_dicts(last_squad_results, results_dict, ["Datetime"]):
                    last_squad_results = results_dict.copy()
                    new_result = True

            else:
                time.sleep(1)
                continue

            if new_result:
                if write_to_file(output_path, headers, results_dict):
                    logger.info(f"Finished writing results to {output_path.name}")
            else:
                logger.info("Duplicate results processed")

            # Add sleep so duplicate results aren't continuously processed
            time.sleep(3)

            logger.info("Watching screen...")


if __name__ == "__main__":
    # Configure logger
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    handler.setStream(tqdm)
    handler.terminator = ""

    logging.basicConfig(level=logging.DEBUG, handlers=[handler])

    try:
        main()
    except Exception as e:
        logger.error(e)
