"""Logging utilities for the trading bot."""
from __future__ import annotations

import logging
from pathlib import Path


LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str = "bot") -> logging.Logger:
    """Configure and return an application logger.

    The logger writes to both console and file using a consistent format. Handlers
    are added only once to prevent duplicate log entries when the function is
    called multiple times.
    """

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(logs_dir / "bot.log")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
