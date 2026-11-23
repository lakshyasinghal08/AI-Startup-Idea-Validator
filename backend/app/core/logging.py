"""
Structured Logging Configuration
================================
Purpose:
    Configures standardized logging format, handlers, and log levels
    across the entire application lifecycle.

Milestone Notes:
    - Milestone 1: Standard console logger with timestamp and level formatting.
    - Future Milestones: Integrate JSON log formatters for centralized monitoring
      (e.g., Datadog, CloudWatch, or Render Log Streams).
"""

import logging
import os
import sys

# Ensure backend root directory is in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../.."))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.config import settings


def setup_logging() -> logging.Logger:
    """
    Initializes and returns the root application logger.
    """
    logger = logging.getLogger("startup_validator")
    
    # Avoid duplicate handlers if reloaded
    if not logger.handlers:
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


logger = setup_logging()

if __name__ == "__main__":
    logger.info("Structured Logger Module Loaded and Initialized Successfully!")
