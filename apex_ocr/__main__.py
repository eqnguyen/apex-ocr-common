import logging
import time

import click
from tqdm import tqdm

from apex_ocr.config import *
from apex_ocr.engine import ApexOCREngine, SummaryType
from apex_ocr.utils import *

logging.captureWarnings(True)
logger = logging.getLogger("apex_ocr")


# TODO: Integrate with database


@click.command()
@click.argument("filename", required=False, type=click.Path(exists=True))
def main(filename: str):
    ocr_engine = ApexOCREngine()

    if filename:
        file_path = Path(filename)

        logger.info(f"Performing OCR on {file_path.name}...")

        summary_type = ocr_engine.classify_summary_page(file_path)

        if summary_type == SummaryType.PERSONAL:
            results = ocr_engine.process_personal_summary_page(file_path)
        elif summary_type == SummaryType.SQUAD:
            results = ocr_engine.process_squad_summary_page(file_path)
        else:
            results = {}

    else:
        logger.info("Watching screen...")

        last_personal_results = {}
        last_squad_results = {}

        while True:
            # Initialize boolean flag for new result
            new_result = False

            # Continuously grab screenshots and interpret them to identify the match summary screen
            summary_type = ocr_engine.classify_summary_page()

            if summary_type == SummaryType.PERSONAL:
                # Skip personal summary page since all this information is contained on the squad
                # summary. Uncomment this section and remove "continue" if you'd like to process
                # this page.

                # log_and_beep("Personal summary screen detected", 2000)
                # results_dict = ocr_engine.process_personal_summary_page()
                # output_path = PERSONAL_STATS_FILE
                # headers = PERSONAL_SUMMARY_HEADERS

                # if not equal_dicts(last_personal_results, results_dict, ["Datetime"]):
                #     last_personal_results = results_dict.copy()
                #     new_result = True
                continue

            elif summary_type == SummaryType.SQUAD:
                log_and_beep("Squad summary screen detected", 2000)
                results_dict = ocr_engine.process_squad_summary_page()
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
