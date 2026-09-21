import numpy as np

from model.masking import apply_identity_mask, build_identity_mask


def test_build_identity_mask_when_hair_and_background_present_then_excludes_them() -> None:
    # Given
    labels = np.array([[0, 17, 1], [14, 4, 16]], dtype=np.uint8)

    # When
    mask = build_identity_mask(labels, blur_size=1)

    # Then
    assert mask.tolist() == [[0.0, 0.0, 1.0], [0.0, 1.0, 0.0]]


def test_apply_identity_mask_when_pixel_is_excluded_then_uses_neutral_background() -> None:
    # Given
    image = np.full((2, 2, 3), 200, dtype=np.uint8)
    mask = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)

    # When
    masked = apply_identity_mask(image, mask, neutral_value=32)

    # Then
    np.testing.assert_array_equal(masked[0, 0], np.array([200, 200, 200], dtype=np.uint8))
    np.testing.assert_array_equal(masked[0, 1], np.array([32, 32, 32], dtype=np.uint8))
