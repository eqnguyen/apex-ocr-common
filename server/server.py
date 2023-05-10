import logging
import shutil
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, UploadFile
from rich.logging import RichHandler
from werkzeug.utils import secure_filename

from apex_ocr.config import IMAGE_EXTENSIONS
from apex_ocr.engine import ApexOCREngine

logging.captureWarnings(True)
logger = logging.getLogger(__name__)

app = FastAPI()
engine = ApexOCREngine()
uploads_path = Path(__file__).parent / "uploads"
uploads_path.mkdir(parents=True, exist_ok=True)


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    filename = Path(secure_filename(file.filename))

    if filename.suffix in IMAGE_EXTENSIONS:
        # Save file to disk
        file_path = uploads_path / secure_filename(file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process screenshot
        results = engine.process_screenshot(file_path)
        return {"results": results}


if __name__ == "__main__":
    # Configure logger
    logging.basicConfig(
        level=logging.INFO,
        format=" %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
        handlers=[RichHandler(omit_repeated_times=False, rich_tracebacks=True)],
    )

    try:
        uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.exception(e)
