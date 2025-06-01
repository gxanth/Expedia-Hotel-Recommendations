import logging
import os
import sys
from pathlib import Path

from loguru import logger


class RelPathFormatter(logging.Formatter):
    def format(self, record):
        # Replace any absolute path in the message with a relative path
        if hasattr(record, "msg") and isinstance(record.msg, str):
            import re

            cwd = str(Path.cwd())
            record.msg = re.sub(rf"{cwd}/", "", record.msg)
        return super().format(record)


# Set up the log directory (default: "logs", configurable via environment variable)
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

# -------------------- Loguru Configuration --------------------

# Remove default logger
logger.remove()

# Console (cleaner): show time, level, function:line
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD}</green> | <level>{level}</level> | "
    "<magenta>[{module}.{function}]</magenta> | <cyan>{message}</cyan>",
)

# File logger
logger.add(
    LOG_DIR / "pipeline.log",
    level="DEBUG",
    rotation="1 MB",
    compression="zip",
    enqueue=True,
    format="<green>{time:YYYY-MM-DD}</green> | <level>{level}</level> | "
    "<magenta>[{module}.{function}]</magenta> | <cyan>{message}</cyan>",
)

# -------------------- Standard Logging (fallback) --------------------

_std_logger = logging.getLogger("expedia")
if not _std_logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(RelPathFormatter("%(asctime)s | %(levelname)s | %(message)s"))
    _std_logger.addHandler(handler)

_std_logger.setLevel(logging.INFO)

# Export both loggers
__all__ = ["logger", "_std_logger"]
