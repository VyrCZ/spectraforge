# MathUtils Documentation

This module provides a collection of utility functions for mathematical computations, including linear interpolation, normalization, color blending, and vector rotation.

# Functions

## lerp(start, end, t)

Linear interpolation between two values.

### Parameters:
  - start (float): Start value.
  - end (float): End value.
  - t (float): Interpolation factor (range: 0.0 to 1.0).
### Returns:
  - (float): The interpolated value.

## normalize(value, old_min, old_max)**

Normalizes a value from a given range to a \[0, 1\] range.

### Parameters:
  - value (float): The value to normalize.
  - old_min (float): The minimum value of the range.
  - old_max (float): The maximum value of the range.
### Returns:
  - (float): Normalized value in the range \[0, 1\].
- **Raises:**
  - ValueError: If old_min is equal to old_max.

## clamp(value, min_value, max_value)**

Clamps a value to a specified range.

### Parameters:
  - value (float): The value to clamp.
  - min_value (float): Minimum allowed value.
  - max_value (float): Maximum allowed value.
### Returns:
  - (float): The clamped value.

## mix_colors(color1, color2)**

Blends two colors using the screen blending mode.

### Parameters:
  - color1 (tuple): First color as an (R, G, B) tuple, where each value is in the range \[0, 255\].
  - color2 (tuple): Second color as an (R, G, B) tuple, where each value is in the range \[0, 255\].
### Returns:
  - (tuple): The blended color as an (R, G, B) tuple.

## wrap(value, min_value, max_value)**

Wraps a value around a range.

### Parameters:
  - value (float): The value to wrap.
  - min_value (float): The lower bound of the range.
  - max_value (float): The upper bound of the range.
### Returns:
  - (float): The wrapped value.

## rotate_direction(direction, degrees)**

Rotates a 2D vector by a given angle in degrees.

### Parameters:
  - direction (list): A 2D vector \[x, y\].
  - degrees (float): The angle to rotate the vector, in degrees.
### Returns:
  - (list): The rotated vector as \[x', y'\].

## combine_rgb_colors(color1, color2, ratio)**

Combines two RGB colors with a specific ratio using gamma-corrected blending.

### Parameters:
  - color1 (tuple): The first color as an (R, G, B) tuple, where each value is in the range \[0, 255\].
  - color2 (tuple): The second color as an (R, G, B) tuple, where each value is in the range \[0, 255\].
  - ratio (float): The blend ratio of the second color (0 means all color1, 1 means all color2).
### Returns:
  - (tuple): The blended color as an (R, G, B) tuple.
- **Raises:**
  - ValueError: If ratio is not in the range \[0, 1\].

**Implementation Details:**

- Gamma correction is applied to ensure perceptually accurate blending. A gamma value of 2.2 is used.
- Intermediate values are computed in linear space before converting back to sRGB space.