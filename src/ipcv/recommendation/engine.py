"""
Embedding index loader and nearest-neighbor recommendation engine.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
from sklearn.neighbors import NearestNeighbors

from ipcv import config
from ipcv.logging_config import get_logger
from ipcv.recommendation.features import build_model, extract_features
from ipcv.recommendation.paths import resolve_dataset_path

logger = get_logger("recommendation.engine")


class RecommendationEngine:
    """
    Search precomputed catalog embeddings for images visually similar to a query.

    Attributes:
        _filenames: Relative paths aligned with rows of the embedding matrix.
        _feature_matrix: NumPy array of shape (N, 2048).
        _neighbors: Fitted scikit-learn ``NearestNeighbors`` index.
        _model: Lazy-loaded Keras model for query encoding.
    """

    def __init__(self) -> None:
        self._filenames: list[str] = []
        self._feature_matrix: np.ndarray | None = None
        self._neighbors: NearestNeighbors | None = None
        self._model = None

    def load_index(self) -> None:
        """
        Load ``filenames.pkl`` and ``embeddings.pkl``, then fit the search index.

        Raises:
            FileNotFoundError: If either pickle file is missing.
            ValueError: If filename and embedding counts differ.
        """
        logger.info("Loading recommendation index")
        if not config.FILENAMES_PATH.is_file():
            raise FileNotFoundError(f"Missing {config.FILENAMES_PATH}")
        if not config.EMBEDDINGS_PATH.is_file():
            raise FileNotFoundError(f"Missing {config.EMBEDDINGS_PATH}")

        with open(config.FILENAMES_PATH, "rb") as handle:
            self._filenames = pickle.load(handle)
        logger.info("Loaded %d catalog filenames", len(self._filenames))

        with open(config.EMBEDDINGS_PATH, "rb") as handle:
            embeddings = pickle.load(handle)

        self._feature_matrix = np.array(embeddings)
        logger.info(
            "Embedding matrix shape: %s (dtype=%s)",
            self._feature_matrix.shape,
            self._feature_matrix.dtype,
        )

        if len(self._filenames) != len(self._feature_matrix):
            raise ValueError(
                f"filenames ({len(self._filenames)}) and embeddings "
                f"({len(self._feature_matrix)}) length mismatch"
            )

        neighbor_k = min(config.NEIGHBOR_SEARCH_K, len(self._feature_matrix))
        logger.info("Fitting NearestNeighbors (k=%d, metric=euclidean, algorithm=brute)", neighbor_k)
        self._neighbors = NearestNeighbors(
            n_neighbors=neighbor_k,
            algorithm="brute",
            metric="euclidean",
        )
        self._neighbors.fit(self._feature_matrix)
        logger.info("Search index ready")

    def _ensure_model(self) -> None:
        """Instantiate the CNN on first query to speed up application startup."""
        if self._model is None:
            logger.info("First query — loading ResNet50 weights")
            self._model = build_model()

    def recommend(self, query_path: Path) -> list[Path]:
        """
        Find the top visually similar products in the catalog for a query image.

        Args:
            query_path: User-uploaded image path.

        Returns:
            Up to ``RECOMMENDATION_COUNT`` absolute paths under ``data/dataset/``.
            Skips the query file itself when it exists in the catalog (Colab parity).

        Raises:
            RuntimeError: If ``load_index()`` was not called successfully.
        """
        if self._neighbors is None or self._feature_matrix is None:
            raise RuntimeError("Index not loaded; call load_index() first")

        logger.info("Starting recommendation for query: %s", query_path.name)
        self._ensure_model()
        query_features = extract_features(query_path, self._model)
        query_resolved = query_path.resolve()

        distances, indices = self._neighbors.kneighbors([query_features])
        logger.info("Nearest-neighbor search complete (candidates=%d)", len(indices[0]))

        results: list[Path] = []
        for rank, index in enumerate(indices[0], start=1):
            distance = float(distances[0][rank - 1])
            candidate = resolve_dataset_path(self._filenames[index])
            if not candidate.is_file():
                logger.warning("Skipping missing file at index %d: %s", index, candidate)
                continue
            if candidate.resolve() == query_resolved:
                logger.info("Skipping self-match: %s", candidate.name)
                continue
            logger.info(
                "Rank %d: %s (euclidean distance=%.4f)",
                len(results) + 1,
                candidate.name,
                distance,
            )
            results.append(candidate)
            if len(results) >= config.RECOMMENDATION_COUNT:
                break

        logger.info("Returning %d recommendations", len(results))
        return results
