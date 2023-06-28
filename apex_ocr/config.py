import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Valid image extensions
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]

# Path to log directory
LOG_DIRECTORY = Path(__file__).parent.parent / "logs"
LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

# Path to data
DATA_DIRECTORY = Path(__file__).parent.parent / "data"
DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

GOOGLE_DRIVE_DIRECTORY = Path(__file__).parent.parent / "data" / "google_drive"
GOOGLE_DRIVE_DIRECTORY.mkdir(parents=True, exist_ok=True)

SQUAD_STATS_FILE = DATA_DIRECTORY / "squad_stats.csv"

# Database output
DATABASE = True
DATABASE_YML_FILE = Path(__file__).parent.parent / "db.yml"
