from pathlib import Path

import click
import pandas as pd

from apex_ocr.engine import ApexOCREngine


@click.command()
@click.argument(
    "filepath",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
def remove_invalid_results(filepath: Path) -> None:
    if filepath.exists() and filepath.suffix == ".csv":
        results_df = pd.read_csv(filepath)
        results_df = results_df[
            results_df.apply(
                lambda row: ApexOCREngine.is_valid_results(row.to_dict()), axis=1
            )
        ]
        results_df.to_csv(filepath, index=False)


if __name__ == "__main__":
    remove_invalid_results()
