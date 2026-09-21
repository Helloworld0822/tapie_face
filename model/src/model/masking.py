"""Identity-region masking that suppresses hair and scene pixels."""

from typing import Final

import cv2
import numpy as np
from numpy.typing import NDArray

type ImageArray = NDArray[np.uint8]
type LabelArray = NDArray[np.uint8]
type MaskArray = NDArray[np.float32]

_IDENTITY_CLASS_IDS: Final[tuple[int, ...]] = (
    1,  # skin
    2,  # left eyebrow
    3,  # right eyebrow
    4,  # left eye
    5,  # right eye
    6,  # eyeglasses
    7,  # left ear
    8,  # right ear
    10,  # nose
    11,  # mouth
    12,  # upper lip
    13,  # lower lip
)


def build_identity_mask(labels: LabelArray, *, blur_size: int = 7) -> MaskArray:
    """Keep facial components while excluding background, hair, neck, and clothing."""
    binary = np.isin(labels, _IDENTITY_CLASS_IDS).astype(np.float32)
    if blur_size <= 1:
        return np.asarray(binary, dtype=np.float32)
    kernel_size = blur_size if blur_size % 2 == 1 else blur_size + 1
    blurred = cv2.GaussianBlur(binary, (kernel_size, kernel_size), sigmaX=0)
    return np.asarray(np.clip(blurred, 0.0, 1.0), dtype=np.float32)


def apply_identity_mask(
    image: ImageArray,
    mask: MaskArray,
    *,
    neutral_value: int = 32,
) -> ImageArray:
    """Blend excluded pixels into a neutral field instead of transparent black."""
    alpha = np.asarray(mask[..., np.newaxis], dtype=np.float32)
    neutral = np.full_like(image, neutral_value, dtype=np.uint8)
    blended = image.astype(np.float32) * alpha + neutral.astype(np.float32) * (1.0 - alpha)
    return np.asarray(np.rint(blended), dtype=np.uint8)
