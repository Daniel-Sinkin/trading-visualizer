import pytest
from glm import vec3

from src.util import hex_to_rgb


def test_hex_to_rgb_valid():
    assert hex_to_rgb("#FF0000") == vec3(1.0, 0.0, 0.0)
    assert hex_to_rgb("#00FF00") == vec3(0.0, 1.0, 0.0)
    assert hex_to_rgb("#0000FF") == vec3(0.0, 0.0, 1.0)
    assert hex_to_rgb("#FFFFFF") == vec3(1.0, 1.0, 1.0)
    assert hex_to_rgb("#000000") == vec3(0.0, 0.0, 0.0)
    assert hex_to_rgb("#123456") == vec3(0.07058824, 0.20392157, 0.3372549)


def test_hex_to_rgb_invalid_length():
    with pytest.raises(AssertionError, match="Hex color must be in the format #RRGGBB"):
        hex_to_rgb("#FFF")


def test_hex_to_rgb_invalid_characters():
    with pytest.raises(AssertionError, match="Hex color must be in the format #RRGGBB"):
        hex_to_rgb("#GGGGGG")


def test_hex_to_rgb_missing_hash():
    with pytest.raises(AssertionError, match="Hex color must be in the format #RRGGBB"):
        hex_to_rgb("123456")


if __name__ == "__main__":
    pytest.main()
