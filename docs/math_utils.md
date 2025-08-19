# MathUtils Documentation

This module provides a collection of utility functions for mathematical computations commonly used in the xmas-lights project, including interpolation, normalization, color blending, geometry, and vector operations.

Each function below lists its signature, parameters, return value, examples, and any raised exceptions.

---

## lerp(start, end, t)

Linear interpolation between two numeric values.

Signature:
```python
lerp(start: float, end: float, t: float) -> float
```

Parameters:
- start (float): Start value.
- end (float): End value.
- t (float): Interpolation factor in the range \[0.0, 1.0\].

Returns:
- float: The interpolated value.

Example:
```python
lerp(0, 10, 0.25)  # -> 2.5
```

---

## normalize(value, old_min, old_max)

Normalize a value from a given range to the \[0, 1\] range.

Signature:
```python
normalize(value: float, old_min: float, old_max: float) -> float
```

Parameters:
- value (float): The value to normalize.
- old_min (float): The minimum value of the input range.
- old_max (float): The maximum value of the input range.

Returns:
- float: Normalized value in the range \[0, 1\].

Raises:
- ValueError: If old_min is equal to old_max.

Example:
```python
normalize(5, 0, 10)  # -> 0.5
```

---

## clamp(value, min_value, max_value)

Clamp a numeric value to a specified inclusive range.

Signature:
```python
clamp(value: float, min_value: float, max_value: float) -> float
```

Parameters:
- value (float): The value to clamp.
- min_value (float): Minimum allowed value.
- max_value (float): Maximum allowed value.

Returns:
- float: The clamped value.

Example:
```python
clamp(12, 0, 10)  # -> 10
```

---

## mix_colors(color1, color2)

Blend two colors using the "screen" blending mode.

Signature:
```python
mix_colors(color1: tuple[int, int, int], color2: tuple[int, int, int]) -> tuple[int, int, int]
```

Parameters:
- color1 (tuple): First color as an (R, G, B) tuple with values in \[0, 255\].
- color2 (tuple): Second color as an (R, G, B) tuple with values in \[0, 255\].

Returns:
- tuple: The blended color as an (R, G, B) tuple with integer channels in \[0, 255\].

Notes:
- Uses the formula Result = 1 - (1 - A) * (1 - B) applied per channel in normalized \[0, 1\] space.

Example:
```python
mix_colors((255, 0, 0), (0, 0, 255))  # -> blended RGB tuple
```

---

## wrap(value, min_value, max_value)

Wrap a numeric value around a closed-open interval \[min_value, max_value\).

Signature:
```python
wrap(value: float, min_value: float, max_value: float) -> float
```

Parameters:
- value (float): The value to wrap.
- min_value (float): Lower bound of the range (inclusive).
- max_value (float): Upper bound of the range (exclusive).

Returns:
- float: The wrapped value.

Example:
```python
wrap(12, 0, 10)  # -> 2
```

---

## rotate_direction(direction, degrees)

Rotate a 2D vector by an angle in degrees.

Signature:
```python
rotate_direction(direction: Sequence[float], degrees: float) -> list[float]
```

Parameters:
- direction (list or tuple): A 2D vector \[x, y\].
- degrees (float): Angle in degrees to rotate the vector (positive rotates counter-clockwise).

Returns:
- list: The rotated vector as \[x', y'\].

Example:
```python
rotate_direction([1, 0], 90)  # -> approx \[0.0, 1.0\]
```

---

## combine_rgb_colors(color1, color2, ratio)

Blend two RGB colors using gamma-corrected linear-space interpolation for perceptually accurate results.

Signature:
```python
combine_rgb_colors(color1: tuple[int, int, int], color2: tuple[int, int, int], ratio: float) -> tuple[int, int, int]
```

Parameters:
- color1 (tuple): First color as an (R, G, B) tuple with values in \[0, 255\].
- color2 (tuple): Second color as an (R, G, B) tuple with values in \[0, 255\].
- ratio (float): Blend ratio of the second color (0.0 returns color1, 1.0 returns color2).

Returns:
- tuple: The gamma-corrected blended color as an (R, G, B) tuple with integer channels in \[0, 255\].

Raises:
- ValueError: If ratio is not in \[0.0, 1.0\].

Implementation details:
- Uses a gamma value of 2.2.
- Converts sRGB to linear space, interpolates there, then converts back to sRGB.

Example:
```python
combine_rgb_colors((255, 0, 0), (0, 0, 255), 0.5)  # -> perceptual midpoint color
```

---

## color_lerp(color1, color2, blend_factor)

Linear interpolation between two colors in sRGB space (per-channel).

Signature:
```python
color_lerp(color1: tuple[int, int, int], color2: tuple[int, int, int], blend_factor: float) -> tuple[int, int, int]
```

Parameters:
- color1 (tuple): First color (R, G, B).
- color2 (tuple): Second color (R, G, B).
- blend_factor (float): Interpolation factor in \[0.0, 1.0\].

Returns:
- tuple: The interpolated sRGB color with integer channels.

Note:
- This is a straight per-channel lerp in sRGB space (not gamma-corrected).

---

## distance(coord1, coord2)

Compute Euclidean distance between two 2D or 3D coordinates.

Signature:
```python
distance(coord1: Sequence[float], coord2: Sequence[float]) -> float
```

Parameters:
- coord1 (tuple): First coordinate (x, y) or (x, y, z).
- coord2 (tuple): Second coordinate (x, y) or (x, y, z).

Returns:
- float: Euclidean distance.

---

## convex_hull(points)

Compute the convex hull of a set of 2D points using the Monotone Chain algorithm.

Signature:
```python
convex_hull(points: Sequence[Sequence[float]]) -> list[tuple[float, float]]
```

Parameters:
- points (iterable): Iterable of 2D points, e.g., \[(x, y), ...\].

Returns:
- list: Vertices of the convex hull in counter-clockwise order.

---

## find_closest_edge(point, edges)

Find the closest edge (segment) of a polygon to a point and return the outward normal of that edge.

Signature:
```python
find_closest_edge(point: Sequence[float], edges: Sequence[Sequence[float]]) -> numpy.ndarray
```

Parameters:
- point (tuple): A 2D point (x, y).
- edges (list): Polygon vertices as a sequence of points.

Returns:
- numpy.ndarray: Unit normal vector (2D) of the closest edge.

Notes:
- Uses projection to find closest point on each segment.

---

## distance_to_closest_edge(point, edges)

Compute the minimal distance from a point to any edge of a polygon.

Signature:
```python
distance_to_closest_edge(point: Sequence[float], edges: Sequence[Sequence[float]]) -> float
```

Parameters:
- point (tuple): A 2D point (x, y).
- edges (list): Polygon vertices as a sequence of points.

Returns:
- float: Minimum distance.

---

## point_in_poly(x, y, poly)

Point-in-polygon test using the ray-casting algorithm.

Signature:
```python
point_in_poly(x: float, y: float, poly: Sequence[Sequence[float]]) -> bool
```

Parameters:
- x (float): X coordinate of the point.
- y (float): Y coordinate of the point.
- poly (list): Polygon vertices as \[(x, y), ...\].

Returns:
- bool: True if the point is strictly inside the polygon, False if outside or on the edge.

---

## Bounds

Class to compute axis-aligned bounding box for a set of coordinates.

Usage:
```python
b = Bounds(coords)
# attributes: min_x, max_x, min_y, max_y, (min_z, max_z if 3D)
```

Notes:
- Provide a non-empty list of coordinates. Coordinates can be 2D (x, y) or 3D (x, y, z).
- If coords is empty, the constructor returns None (current behavior).

---

If you want, I can:
- update the module docstring to match this doc,
- add usage examples as runnable snippets, or
- generate unit tests validating behavior for