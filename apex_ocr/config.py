import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Valid image extensions
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]

# Path to stats file
DATA_DIRECTORY = Path(__file__).parent.parent / "data"
DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

SQUAD_STATS_FILE = DATA_DIRECTORY / "squad_stats.csv"

# Database output
DATABASE = False
DATABASE_YML_FILE = Path(__file__).parent.parent / "db.yml"
