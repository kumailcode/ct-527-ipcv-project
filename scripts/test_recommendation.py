#!/usr/bin/env python3
"""
Headless validation of the recommendation pipeline (no GUI).

Usage (from project root, venv activated):

    python scripts/test_recommendation.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ipcv import config
from ipcv.logging_config import setup_logging, get_logger
from ipcv.recommendation.engine import RecommendationEngine
from ipcv.recommendation.paths import resolve_dataset_path

logger = get_logger("test")


def test_index() -> None:
    """Verify pickle files load and paths resolve to real images."""
    logger.info("=== Test: index load ===")
    engine = RecommendationEngine()
    engine.load_index()
    assert len(engine._filenames) == 39816
    sample = resolve_dataset_path(engine._filenames[0])
    assert sample.is_file(), sample
    logger.info("Index load: PASSED")


def test_recommend_in_dataset() -> None:
    """Run end-to-end recommendation for a catalog image."""
    logger.info("=== Test: in-dataset recommendation ===")
    try:
        import tensorflow  # noqa: F401
    except ImportError:
        logger.warning("TensorFlow not installed — skipping recommend test")
        return

    query = config.DATASET_DIR / "images" / "10000.jpg"
    engine = RecommendationEngine()
    engine.load_index()
    results = engine.recommend(query)
    assert len(results) == config.RECOMMENDATION_COUNT, results
    assert all(path.is_file() for path in results)
    assert query.resolve() not in {path.resolve() for path in results}
    logger.info("Recommend in-dataset: PASSED — %s", [p.name for p in results])


if __name__ == "__main__":
    setup_logging()
    test_index()
    test_recommend_in_dataset()
