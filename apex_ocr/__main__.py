import logging
import time
import traceback

import click
from rich.logging import RichHandler
from rich.progress import track

from apex_ocr.config import *
from apex_ocr.engine import ApexOCREngine
from apex_ocr.utils import *

logging.captureWarnings(True)
logger = logging.getLogger(__name__)


@click.command()
@click.argument("filepath", required=False, type=click.Path(exists=True))
def main(filepath: str):
    ocr_engine = ApexOCREngine()

    if filepath:
        file_path = Path(filepath)
        file_list = []

        if file_path.is_file():
            file_list = [file_path]
        elif file_path.is_dir():
            file_list = sorted(
                [
                    path
                    for path in file_path.iterdir()
                    if path.is_file() and path.suffix in IMAGE_EXTENSIONS
                ]
            )

        for screenshot_path in track(file_list):
            logger.info(f"Performing OCR on {screenshot_path.name}...")
            ocr_engine.process_screenshot(screenshot_path)

    else:
        logger.info("Watching screen...")

        while True:
            ocr_engine.process_screenshot()
            time.sleep(3)
            logger.info("Watching screen...")


if __name__ == "__main__":
    # Configure logger
    logging.basicConfig(
        level=logging.DEBUG,
        format=" %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
        handlers=[RichHandler(omit_repeated_times=False, show_path=False)],
    )

    try:
        main()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.print_exc())
