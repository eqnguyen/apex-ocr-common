import logging
import time
from datetime import datetime
from pathlib import Path

import click
from PIL import Image
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

from apex_ocr.config import IMAGE_EXTENSIONS, LOG_DIRECTORY
from apex_ocr.engine import ApexOCREngine
from apex_ocr.roi import scale_rois

logging.captureWarnings(True)
logger = logging.getLogger(__name__)


@click.command()
@click.argument("filepath", required=False, type=click.Path(exists=True))
@click.option("-d", "--debug", is_flag=True, show_default=True, default=False)
def main(filepath: str, debug: bool):
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

        if len(file_list) == 0:
            logger.warning(f"No images found in {file_path}")
        else:
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
                    scale_rois(Image.open(screenshot_path).size)
                    ocr_engine.process_screenshot(screenshot_path, debug)

                    pb.update(task1, advance=1)

    else:
        logger.info("Watching screen...")

        while True:
            ocr_engine.process_screenshot(debug=debug)
            time.sleep(3)


if __name__ == "__main__":
    # Configure logger
    file_handler = logging.FileHandler(
        LOG_DIRECTORY
        / f"apex_ocr_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logging.basicConfig(
        level=logging.INFO,
        format=" %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
        handlers=[
            file_handler,
            RichHandler(omit_repeated_times=False, rich_tracebacks=True),
        ],
    )

    try:
        main()
    except Exception as e:
        logger.exception(e)
