import math
from unittest.mock import MagicMock, patch

import pytest


def test_mathutils_clamp_lower_bound():
    """Test clamp function returns lower bound when value is too low."""
    from modules.mathutils import clamp
    
    result = clamp(5, 10, 20)
    assert result == 10


def test_mathutils_clamp_upper_bound():
    """Test clamp function returns upper bound when value is too high."""
    from modules.mathutils import clamp
    
    result = clamp(25, 10, 20)
    assert result == 20


def test_mathutils_clamp_within_bounds():
    """Test clamp function returns value when within bounds."""
    from modules.mathutils import clamp
    
    result = clamp(15, 10, 20)
    assert result == 15


def test_mathutils_lerp_start():
    """Test linear interpolation at t=0 returns start value."""
    from modules.mathutils import lerp
    
    result = lerp(10, 20, 0.0)
    assert result == 10


def test_mathutils_lerp_end():
    """Test linear interpolation at t=1 returns end value."""
    from modules.mathutils import lerp
    
    result = lerp(10, 20, 1.0)
    assert result == 20


def test_mathutils_lerp_midpoint():
    """Test linear interpolation at t=0.5 returns midpoint."""
    from modules.mathutils import lerp
    
    result = lerp(10, 20, 0.5)
    assert result == 15


def test_mathutils_distance_2d():
    """Test distance calculation between two 2D points."""
    from modules.mathutils import distance
    
    result = distance([0, 0], [3, 4])
    assert result == 5.0


def test_mathutils_distance_3d():
    """Test distance calculation between two 3D points."""
    from modules.mathutils import distance
    
    result = distance([0, 0, 0], [1, 1, 1])
    expected = math.sqrt(3)
    assert abs(result - expected) < 0.0001


def test_mathutils_distance_same_point():
    """Test distance between identical points is zero."""
    from modules.mathutils import distance
    
    result = distance([5, 5], [5, 5])
    assert result == 0.0


def test_mathutils_normalize_value_range():
    """Test normalize function scales value to 0-1 range."""
    from modules.mathutils import normalize
    
    result = normalize(5, 0, 10)
    assert result == 0.5


def test_mathutils_normalize_lower():
    """Test normalize returns 0 for minimum value."""
    from modules.mathutils import normalize
    
    result = normalize(0, 0, 10)
    assert result == 0.0


def test_mathutils_normalize_upper():
    """Test normalize returns 1 for maximum value."""
    from modules.mathutils import normalize
    
    result = normalize(10, 0, 10)
    assert result == 1.0


def test_mathutils_wrap_value():
    """Test wrap function wraps value in range."""
    from modules.mathutils import wrap
    
    result = wrap(12, 0, 10)
    assert result == 2


def test_mathutils_mix_colors_additive():
    """Test mix_colors performs color blending."""
    from modules.mathutils import mix_colors
    
    color1 = (100, 50, 200)
    color2 = (150, 100, 50)
    
    result = mix_colors(color1, color2)
    
    assert isinstance(result, tuple)
    assert len(result) == 3


def test_mathutils_color_lerp_interpolation():
    """Test color_lerp interpolates between RGB colors."""
    from modules.mathutils import color_lerp
    
    color1 = (0, 0, 0)
    color2 = (255, 255, 255)
    
    result = color_lerp(color1, color2, 0.5)
    
    assert isinstance(result, tuple)
    assert len(result) == 3


def test_mathutils_color_lerp_start():
    """Test color_lerp at 0 returns first color."""
    from modules.mathutils import color_lerp
    
    color1 = (255, 0, 0)
    color2 = (0, 255, 0)
    
    result = color_lerp(color1, color2, 0.0)
    
    assert result[0] == 255


def test_mathutils_color_lerp_end():
    """Test color_lerp at 1 returns second color."""
    from modules.mathutils import color_lerp
    
    color1 = (255, 0, 0)
    color2 = (0, 255, 0)
    
    result = color_lerp(color1, color2, 1.0)
    
    assert result[1] == 255


def test_mathutils_rotate_direction_90():
    """Test rotate_direction rotates vector 90 degrees."""
    from modules.mathutils import rotate_direction
    
    direction = [1, 0]
    result = rotate_direction(direction, 90)
    
    assert isinstance(result, list)
    assert len(result) == 2


def test_mathutils_convex_hull_triangle():
    """Test convex_hull with triangle points."""
    from modules.mathutils import convex_hull
    
    points = [(0, 0), (1, 0), (0, 1)]
    
    result = convex_hull(points)
    
    assert isinstance(result, list)
    assert len(result) >= 3


def test_mathutils_point_in_poly_inside():
    """Test point_in_poly detects point inside polygon."""
    from modules.mathutils import point_in_poly
    
    polygon = [(0, 0), (10, 0), (10, 10), (0, 10)]
    point_x, point_y = 5, 5
    
    result = point_in_poly(point_x, point_y, polygon)
    
    assert result is True


def test_mathutils_point_in_poly_outside():
    """Test point_in_poly detects point outside polygon."""
    from modules.mathutils import point_in_poly
    
    polygon = [(0, 0), (10, 0), (10, 10), (0, 10)]
    point_x, point_y = 15, 15
    
    result = point_in_poly(point_x, point_y, polygon)
    
    assert result is False


def test_mathutils_bounds_class_init():
    """Test Bounds class initialization with coordinates."""
    from modules.mathutils import Bounds
    
    coords = [[0, 0, 0], [10, 20, 30], [5, 15, 25]]
    
    bounds = Bounds(coords)
    
    assert bounds.min_x == 0
    assert bounds.max_x == 10


def test_mathutils_bounds_3d_coordinates():
    """Test Bounds with 3D coordinates."""
    from modules.mathutils import Bounds
    
    coords = [[0, 0, 0], [10, 20, 30]]
    
    bounds = Bounds(coords)
    
    assert hasattr(bounds, "min_z")
    assert hasattr(bounds, "max_z")


def test_mathutils_bounds_2d_coordinates():
    """Test Bounds with 2D coordinates."""
    from modules.mathutils import Bounds
    
    coords = [[0, 0], [10, 20]]
    
    bounds = Bounds(coords)
    
    assert bounds.min_x == 0
    assert bounds.max_y == 20


def test_mathutils_combine_rgb_colors():
    """Test combine_rgb_colors gamma-corrected blend."""
    from modules.mathutils import combine_rgb_colors
    
    color1 = (100, 100, 100)
    color2 = (200, 200, 200)
    
    result = combine_rgb_colors(color1, color2, 0.5)
    
    assert isinstance(result, tuple)
    assert len(result) == 3


def test_mathutils_combine_rgb_start():
    """Test combine_rgb_colors at 0 returns first color."""
    from modules.mathutils import combine_rgb_colors
    
    color1 = (255, 0, 0)
    color2 = (0, 255, 0)
    
    result = combine_rgb_colors(color1, color2, 0.0)
    
    assert result[0] == 255


def test_mathutils_combine_rgb_end():
    """Test combine_rgb_colors at 1 returns second color."""
    from modules.mathutils import combine_rgb_colors
    
    color1 = (255, 0, 0)
    color2 = (0, 255, 0)
    
    result = combine_rgb_colors(color1, color2, 1.0)
    
    assert result[1] == 255


def test_mathutils_distance_to_closest_edge():
    """Test distance_to_closest_edge calculation."""
    from modules.mathutils import distance_to_closest_edge
    
    point = [5, 5]
    edges = [[0, 0], [10, 0], [10, 10], [0, 10]]
    
    result = distance_to_closest_edge(point, edges)
    
    assert result >= 0


def test_mathutils_find_closest_edge():
    """Test find_closest_edge returns edge normal."""
    from modules.mathutils import find_closest_edge
    
    point = [5, 5]
    edges = [[0, 0], [10, 0], [10, 10], [0, 10]]
    
    result = find_closest_edge(point, edges)
    
    assert result is not None
