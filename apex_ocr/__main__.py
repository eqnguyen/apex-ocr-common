import logging
import time
from collections import Counter, defaultdict
from datetime import datetime

import pytesseract
from config import *
from PIL import ImageGrab
from tqdm import tqdm
from utils import *

logging.captureWarnings(True)
logger = logging.getLogger("apex_ocr")


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
            time.sleep(1)

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

                for header, matcher in HEADER_MAP.items():
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

            # Write to local file
            write_to_file(STATS_FILE, results_dict)

            logger.info(f"Finished writing interpretations to {STATS_FILE.name}")
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
