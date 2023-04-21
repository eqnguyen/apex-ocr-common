import logging
import time

import click
import yaml
from rich.logging import RichHandler

from apex_ocr.config import *
from apex_ocr.database.api import ApexDatabaseApi
from apex_ocr.engine import ApexOCREngine, SummaryType
from apex_ocr.utils import *

logging.captureWarnings(True)
logger = logging.getLogger(__name__)


# TODO: Integrate with database


@click.command()
@click.argument("filename", required=False, type=click.Path(exists=True))
def main(filename: str):
    ocr_engine = ApexOCREngine()

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

        apex_database_engine = ApexDatabaseApi(db_conn_str)

    if filename:
        file_path = Path(filename)

        logger.info(f"Performing OCR on {file_path.name}...")

        summary_type = ocr_engine.classify_summary_page(file_path)

        if summary_type == SummaryType.PERSONAL:
            # Skip personal summary page since all this information is contained on the squad
            # summary. Uncomment this section and remove "pass" if you'd like to process
            # this page.

            # results_dict = ocr_engine.process_personal_summary_page(file_path)

            pass

        elif summary_type == SummaryType.SQUAD:
            results_dict = ocr_engine.process_squad_summary_page(file_path)
            display_results(results_dict)

            if DATABASE:
                apex_database_engine.push_results(results_dict)

        else:
            results_dict = {}

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

                display_results(results_dict)

            else:
                time.sleep(1)
                continue

            if new_result:
                if write_to_file(output_path, headers, results_dict):
                    logger.info(f"Finished writing results to {output_path.name}")
                
                if DATABASE:
                    apex_database_engine.push_results(results_dict)

            else:
                logger.info("Duplicate results processed")

            # Add sleep so duplicate results aren't continuously processed
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
