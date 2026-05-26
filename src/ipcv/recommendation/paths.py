"""
Path resolution between pickle-stored filenames and the local dataset tree.
"""

from pathlib import Path

from ipcv import config
from ipcv.logging_config import get_logger

logger = get_logger("recommendation.paths")


def resolve_dataset_path(stored: str) -> Path:
    """
    Map a relative entry from ``filenames.pkl`` to an absolute filesystem path.

    Pickle entries use Windows-style separators (e.g. ``images\\10000.jpg``).
    They are joined with ``config.DATASET_DIR``.

    Args:
        stored: Relative path string from the embeddings index.

    Returns:
        Absolute ``Path`` under ``data/dataset/``.
    """
    normalized = stored.replace("\\", "/")
    resolved = config.DATASET_DIR / normalized
    logger.debug("Resolved index entry '%s' -> %s", stored, resolved)
    return resolved
