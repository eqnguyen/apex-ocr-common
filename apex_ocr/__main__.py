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

    while True:
        # Continuously grab screenshots and interpret them to identify the match summary screen
        img = preprocess_image(ImageGrab.grab(bbox=TOP_SCREEN), 3)
        text = pytesseract.image_to_string(img, config=TESSERACT_CONFIG)
        text = text.replace("\n", "").replace(" ", "").lower()

        if "summary" in text:
            log_and_beep("Match Summary screen detected", 2000)

            if "xpbreakdown" in text:
                results_dict = process_personal_summary_page(blurs)
                output_path = PERSONAL_STATS_FILE
            else:
                results_dict = process_squad_summary_page(blurs)
                output_path = SQUAD_STATS_FILE

            write_to_file(output_path, results_dict)
            logger.info(f"Finished writing interpretations to {output_path.name}")

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
