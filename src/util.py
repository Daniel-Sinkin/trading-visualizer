from glm import vec3


def hex_to_rgb(hex_color: str) -> vec3:
    """
    Converts a hex color to an RGB color.

    Example:
    >>> hex_to_rgb("#FF0000") == vec3(1.0, 0.0, 0.0)
    """

    assert len(hex_color) == 7, "Hex color must be in the format #RRGGBB"
    assert all(
        c in "0123456789ABCDEF" for c in hex_color[1:]
    ), "Hex color must be in the format #RRGGBB"
    assert hex_color[0] == "#", "Hex color must be in the format #RRGGBB"

    hex_color = hex_color.removeprefix("#")

    # Convert the hex color to an integer and split into RGB components
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    assert all(
        0 <= c <= 255 for c in (r, g, b)
    ), "RGB values must be in the range [0, 255]"

    # Normalize the RGB values to the range [0, 1] for glm.vec3
    return vec3(r / 255.0, g / 255.0, b / 255.0)
