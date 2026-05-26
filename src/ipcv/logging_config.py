"""
Central logging configuration for demo and debugging.

Call ``setup_logging()`` once at application startup. All modules use
``logging.getLogger("ipcv")`` or ``logging.getLogger("ipcv.<module>")``.
"""

from __future__ import annotations

import logging
import sys


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Configure the root ``ipcv`` logger with a console handler.

    Args:
        level: Logging level (default INFO for step-by-step demo output).

    Returns:
        The configured ``ipcv`` logger instance.
    """
    logger = logging.getLogger("ipcv")
    if logger.handlers:
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Return a child logger under the ``ipcv`` namespace.

    Args:
        name: Submodule name (e.g. ``recommendation.engine``).

    Returns:
        Logger instance for the given module path.
    """
    return logging.getLogger(f"ipcv.{name}")
