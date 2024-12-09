import numpy as np
import math

def lerp(a, b, t):
    return (1 - t) * a + t * b

def normalize(value, old_min, old_max):
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
    c1 = np.array(color1) / 255.0
    c2 = np.array(color2) / 255.0
    blended = 1 - (1 - c1) * (1 - c2)
    return tuple((blended * 255).astype(int))

def wrap(value, min_value, max_value):
    """
    Wraps a value around a range.
    
    For example, if min_value = 0 and max_value = 10, then wrap(12, 0, 10) = 2.
    """
    return min_value + (value - min_value) % (max_value - min_value)

def rotate_direction(direction, degrees):
    # Convert degrees to radians
    radians = math.radians(degrees)
    
    # Apply rotation matrix
    rotated_x = direction[0] * math.cos(radians) - direction[1] * math.sin(radians)
    rotated_y = direction[0] * math.sin(radians) + direction[1] * math.cos(radians)
    
    return [rotated_x, rotated_y]
