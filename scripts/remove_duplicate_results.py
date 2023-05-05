from pathlib import Path

import click
import pandas as pd


@click.command()
@click.argument(
    "filepath",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
def remove_duplicate_results(filepath: Path) -> None:
    if filepath.exists() and filepath.suffix == ".csv":
        results_df = pd.read_csv(filepath)
        results_df = results_df.drop_duplicates(subset="Hash", keep="first")
        results_df.to_csv(filepath, index=False)


if __name__ == "__main__":
    remove_duplicate_results()
