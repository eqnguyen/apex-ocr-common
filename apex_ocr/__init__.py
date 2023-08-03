import logging
from rich.logging import RichHandler

__version__ = "1.2.0"

logging.captureWarnings(True)

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
