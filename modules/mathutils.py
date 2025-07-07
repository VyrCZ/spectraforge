#import numpy as np
import math
import colorsys

def lerp(start, end, t):
    """
    Linear interpolation between two values.
    a - start value
    b - end value
    t - interpolation factor (0.0 - 1.0)
    """
    return (1 - t) * start + t * end

def normalize(value, old_min, old_max):
    """
    Normalize a value from a given range to a 0-1 range.
    value - the value to normalize
    old_min - the minimum value of the range
    old_max - the maximum value of the range
    """
    if old_min == old_max:
        raise ValueError("old_min and old_max cannot be the same.")
    return (value - old_min) / (old_max - old_min)

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def mix_colors(color1, color2):
    """
    Blends two colors using the screen blending mode.
    
    Formula: Result = 1 - (1 - A) * (1 - B)
    """
    blended = []
    for c1, c2 in zip(color1, color2):
        result = 1 - (1 - c1 / 255.0) * (1 - c2 / 255.0)
        blended.append(int(result * 255))
    return tuple(blended)

def wrap(value, min_value, max_value):
    """
    Wraps a value around a range.
    
    For example, if min_value = 0 and max_value = 10, then wrap(12, 0, 10) = 2.
    """
    return min_value + (value - min_value) % (max_value - min_value)

def rotate_direction(direction, degrees):
    """
    Rotates a 2D vector by a given angle in degrees.
    I don't know if it actually works lmao
    """
    # Convert degrees to radians
    radians = math.radians(degrees)
    
    # Apply rotation matrix
    rotated_x = direction[0] * math.cos(radians) - direction[1] * math.sin(radians)
    rotated_y = direction[0] * math.sin(radians) + direction[1] * math.cos(radians)
    
    return [rotated_x, rotated_y]

def combine_rgb_colors(color1, color2, ratio):
    """
    Combine two RGB colors with a specific ratio using gamma-corrected blending.

    Parameters:
    color1 (tuple): The first color as an (R, G, B) tuple, where each value is in the range [0, 255].
    color2 (tuple): The second color as an (R, G, B) tuple, where each value is in the range [0, 255].
    ratio (float): The blend ratio of the second color (0 means all color1, 1 means all color2).

    Returns:
    tuple: The blended color as an (R, G, B) tuple.
    """
    if not (0 <= ratio <= 1):
        raise ValueError("Ratio must be between 0 and 1.")

    # Gamma correction constant (2.2 is a common value)
    gamma = 2.2

    def to_linear(c):
        return [(v / 255.0) ** gamma for v in c]

    def to_srgb(c):
        return [int((v ** (1 / gamma)) * 255) for v in c]

    # Convert colors to linear space
    linear1 = to_linear(color1)
    linear2 = to_linear(color2)

    # Interpolate in linear space
    blended_linear = [
        (1 - ratio) * l1 + ratio * l2
        for l1, l2 in zip(linear1, linear2)
    ]

    # Convert back to sRGB space
    blended_srgb = to_srgb(blended_linear)

    return tuple(blended_srgb)

def color_lerp(color1, color2, blend_factor):
    """
    Linearly interpolates between two colors through RGB space.
    
    color1 - the first color as an (R, G, B) tuple
    color2 - the second color as an (R, G, B) tuple
    blend_factor - the interpolation factor (0.0 - 1.0)
    """
    return tuple(
        int(lerp(c1, c2, blend_factor)) for c1, c2 in zip(color1, color2)
    )


def distance(coord1, coord2):
    """
    Calculates the Euclidean distance between two 3D or 2D coordinates.
    
    coord1 - the first coordinate as a tuple (x, y, z)
    coord2 - the second coordinate as a tuple (x, y, z)
    """
    if len(coord1) == 2 or len(coord2) == 2:
        # If the coordinates are 2D, ignore the z-axis
        return math.sqrt(
            (coord1[0] - coord2[0]) ** 2 +
            (coord1[1] - coord2[1]) ** 2
        )
    return math.sqrt(
        (coord1[0] - coord2[0]) ** 2 +
        (coord1[1] - coord2[1]) ** 2 +
        (coord1[2] - coord2[2]) ** 2
    )