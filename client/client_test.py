import requests
from pathlib import Path
import click


@click.command()
@click.argument("filepath", required=True, type=click.Path(exists=True, dir_okay=False))
def main(filepath: Path):
    url = "http://localhost:8000/uploadfile/"
    files = {"file": open(filepath, "rb")}

    response = requests.post(url, files=files)

    print(response.json())


if __name__ == "__main__":
    main()
