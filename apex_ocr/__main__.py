import logging
import time
import traceback

import click
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

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

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        ) as pb:
            task1 = pb.add_task("Processing screenshots...", total=len(file_list))

            for screenshot_path in file_list:
                logger.info(f"Performing OCR on {screenshot_path.name}...")
                ocr_engine.process_screenshot(screenshot_path)

                pb.update(task1, advance=1)

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
        traceback.print_exc()
