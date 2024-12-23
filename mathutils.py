#import numpy as np
import math

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

# def mix_colors(color1, color2):
#     """
#     Blends two colors using the screen blending mode.
    
#     Formula: Result = 1 - (1 - A) * (1 - B)
#     """
#     c1 = np.array(color1) / 255.0
#     c2 = np.array(color2) / 255.0
#     blended = 1 - (1 - c1) * (1 - c2)
#     return tuple((blended * 255).astype(int))

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
