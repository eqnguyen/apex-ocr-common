import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Valid image extensions
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]

ROOT_DIR = Path(__file__).parent.parent 

# Path to log directory
LOG_DIRECTORY = ROOT_DIR / "logs"
LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

# Path to data
DATA_DIRECTORY = ROOT_DIR / "data"
# DATA_DIRECTORY = Path("/home/apex/apex-ocr-common") / "data"
DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

GOOGLE_DRIVE_DIRECTORY = DATA_DIRECTORY / "google_drive"
GOOGLE_DRIVE_DIRECTORY.mkdir(parents=True, exist_ok=True)

SQUAD_STATS_FILE = DATA_DIRECTORY / "squad_stats.csv"

# Database output
DATABASE = False
DATABASE_YML_FILE = ROOT_DIR / "db.yml"

# Parallel run settings
PARALLEL = False

# ROI Files
RESOLUTION_DIR = DATA_DIRECTORY / "rois"
RESOLUTION_DIR.mkdir(parents=True, exist_ok=True)

USER_DEFINED_REOLUTION_DIR = RESOLUTION_DIR / "user_defined"
USER_DEFINED_REOLUTION_DIR.mkdir(parents=True, exist_ok=True)
