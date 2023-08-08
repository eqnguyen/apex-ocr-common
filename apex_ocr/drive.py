import logging

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
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

from apex_ocr.config import GOOGLE_DRIVE_DIRECTORY

logger = logging.getLogger("apex_ocr.drive")


def download_from_google_drive():
    gauth = GoogleAuth(
        settings={
            "client_config_backend": "file",
            "client_config_file": "client_secrets.json",
            "oauth_scope": ["https://www.googleapis.com/auth/drive"],
            "save_credentials": True,
            "save_credentials_backend": "file",
            "save_credentials_file": "credentials.json",
            "get_refresh_token": True,
        }
    )

    gauth.LoadCredentialsFile("credentials.json")

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("credentials.json")
    drive = GoogleDrive(gauth)

    folder_list = drive.ListFile({"q": "'root' in parents"}).GetList()
    for folder in folder_list:
        if folder["title"] == "screenshots":
            screenshot_id = folder["id"]
            file_list = drive.ListFile(
                {"q": f"'{screenshot_id}' in parents and trashed=false"}
            ).GetList()

            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
            ) as pb:
                task1 = pb.add_task("Downloading screenshots...", total=len(file_list))
                for file in file_list:
                    if not (GOOGLE_DRIVE_DIRECTORY / file["title"]).exists():
                        file.GetContentFile(GOOGLE_DRIVE_DIRECTORY / file["title"])
                    pb.update(task1, advance=1)


if __name__ == "__main__":
    # Configure logger
    logging.basicConfig(
        level=logging.INFO,
        format=" %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
        handlers=[
            RichHandler(omit_repeated_times=False, rich_tracebacks=True),
        ],
    )

    download_from_google_drive()
