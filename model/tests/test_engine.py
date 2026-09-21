import pytest

from model.engine import _decode_image
from model.errors import InvalidImageError


@pytest.mark.parametrize("image_bytes", [b"", b"not an image"])
def test_decode_when_image_bytes_are_invalid_then_raises_pipeline_error(image_bytes: bytes) -> None:
    # Given
    invalid_image = image_bytes

    # When / Then
    with pytest.raises(InvalidImageError):
        _ = _decode_image(invalid_image)
