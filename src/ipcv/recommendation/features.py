"""
Deep learning feature extraction using ResNet50 (Google Colab notebook parity).

Produces L2-normalized 2048-dimensional vectors suitable for Euclidean
nearest-neighbor search in embedding space.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Union

import numpy as np
from numpy.linalg import norm

from ipcv.logging_config import get_logger

if TYPE_CHECKING:
    import tensorflow.keras

logger = get_logger("recommendation.features")


def build_model() -> "tensorflow.keras.Sequential":
    """
    Construct a frozen ResNet50 backbone with global max pooling.

    Weights are ImageNet-pretrained. The classification head is removed;
    ``GlobalMaxPool2D`` reduces spatial maps to a single vector per image.

    Returns:
        Keras ``Sequential`` model ready for ``predict``.

    Raises:
        ImportError: If TensorFlow is not installed (requires Python 3.11/3.12).
    """
    logger.info("Building ResNet50 feature extraction model")
    try:
        import tensorflow
        from tensorflow.keras.applications.resnet50 import ResNet50
        from tensorflow.keras.layers import GlobalMaxPool2D
    except ImportError as exc:
        logger.error("TensorFlow import failed")
        raise ImportError(
            "TensorFlow is required for recommendations. "
            "Use Python 3.11 or 3.12 and run: pip install -r requirements.txt"
        ) from exc

    backbone = ResNet50(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    backbone.trainable = False
    model = tensorflow.keras.Sequential([backbone, GlobalMaxPool2D()])
    logger.info("ResNet50 model ready (frozen weights, output dim=2048)")
    return model


def extract_features(
    img_path: Union[str, Path],
    model: "tensorflow.keras.Sequential",
) -> np.ndarray:
    """
    Encode one image into a unit-length feature vector.

    Pipeline: load 224x224 RGB -> ``preprocess_input`` -> forward pass ->
    flatten -> divide by L2 norm (same as Colab ``extract_features``).

    Args:
        img_path: Path to a product image on disk.
        model: Model returned by ``build_model()``.

    Returns:
        One-dimensional ``numpy`` array of normalized features.
    """
    from tensorflow.keras.applications.resnet50 import preprocess_input
    from tensorflow.keras.preprocessing import image

    logger.info("Extracting CNN features for: %s", img_path)
    img = image.load_img(str(img_path), target_size=(224, 224))
    img_array = image.img_to_array(img)
    expanded = np.expand_dims(img_array, axis=0)
    preprocessed = preprocess_input(expanded)
    logger.debug("Running ResNet50 forward pass")
    result = model.predict(preprocessed, verbose=0).flatten()
    normalized = result / norm(result)
    logger.info("Feature vector computed (length=%d, L2 norm=%.4f)", len(normalized), norm(normalized))
    return normalized
