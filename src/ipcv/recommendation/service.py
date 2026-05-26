"""
Background-thread wrapper so CNN inference does not block the GUI event loop.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable, Optional

from ipcv.logging_config import get_logger
from ipcv.recommendation.engine import RecommendationEngine

logger = get_logger("recommendation.service")


class RecommenderService:
    """
    Thread-safe facade around ``RecommendationEngine`` for the desktop client.

    Loads the embedding index once, serializes queries with a lock, and
    delivers results via callbacks suitable for ``tkinter.after``.
    """

    def __init__(self) -> None:
        self._engine = RecommendationEngine()
        self._ready = False
        self._init_lock = threading.Lock()
        self._query_lock = threading.Lock()
        self._init_error: Optional[str] = None

    @property
    def is_ready(self) -> bool:
        """True after ``load_index()`` completed without error."""
        return self._ready

    @property
    def init_error(self) -> Optional[str]:
        """Error message from the last failed initialization, if any."""
        return self._init_error

    def initialize(self) -> None:
        """
        Load pickles and fit NearestNeighbors.

        Idempotent: subsequent calls return immediately if already ready or failed.
        """
        with self._init_lock:
            if self._ready or self._init_error:
                return
            logger.info("Initializing recommender service")
            try:
                self._engine.load_index()
                self._ready = True
                logger.info("Recommender service ready")
            except Exception as exc:
                self._init_error = str(exc)
                logger.exception("Recommender initialization failed")

    def recommend_async(
        self,
        query_path: Path,
        on_success: Callable[[list[Path]], None],
        on_error: Callable[[str], None],
    ) -> None:
        """
        Run ``recommend`` on a worker thread and invoke a callback with results.

        Args:
            query_path: Uploaded image path.
            on_success: Called with a list of recommended ``Path`` objects.
            on_error: Called with an error message string on failure.
        """
        logger.info("Scheduling async recommendation for %s", query_path.name)

        def worker() -> None:
            try:
                self.initialize()
                if self._init_error:
                    logger.error("Cannot recommend — init error: %s", self._init_error)
                    on_error(self._init_error)
                    return
                with self._query_lock:
                    results = self._engine.recommend(query_path)
                logger.info("Async recommendation finished (%d results)", len(results))
                on_success(results)
            except Exception as exc:
                logger.exception("Async recommendation failed")
                on_error(str(exc))

        threading.Thread(target=worker, daemon=True, name="recommend-worker").start()

    def initialize_async(self, on_complete: Optional[Callable[[], None]] = None) -> None:
        """
        Preload the embedding index on a background thread at application startup.

        Args:
            on_complete: Optional callback after initialization attempt finishes.
        """
        logger.info("Scheduling background index preload")

        def worker() -> None:
            self.initialize()
            if on_complete:
                on_complete()

        threading.Thread(target=worker, daemon=True, name="index-preload").start()
