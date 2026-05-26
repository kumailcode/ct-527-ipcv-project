"""
Raster asset loading for the desktop UI (header logo and future icons).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image

from ipcv import config
from ipcv.logging_config import get_logger

logger = get_logger("assets")


def load_logo_image(path: Optional[Path] = None, size: int = config.LOGO_SIZE) -> Optional[Image.Image]:
    """
    Load the header logo as a square RGBA PIL image.

    Args:
        path: Override path; defaults to ``config.LOGO_PATH``.
        size: Maximum width and height in pixels after thumbnail resize.

    Returns:
        PIL Image in RGBA mode, or None if the file is missing or unreadable.
    """
    logo_path = path or config.LOGO_PATH
    logger.info("Loading logo from %s (target size %d px)", logo_path, size)

    if not logo_path.is_file():
        logger.warning("Logo file not found: %s", logo_path)
        return None

    try:
        image = Image.open(logo_path).convert("RGBA")
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        logger.info("Logo loaded successfully (%dx%d)", image.width, image.height)
        return image
    except OSError as exc:
        logger.error("Failed to decode logo: %s", exc)
        return None
