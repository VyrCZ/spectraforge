import numpy as np
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

def convex_hull(points):
    """
    Computes the convex hull of a set of 2D points using the Monotone Chain algorithm.
    """
    # sort lexicographically
    pts = sorted(map(tuple, points))
    if len(pts) <= 1: 
        return pts
    def half_chain(pts):
        chain = []
        for p in pts:
            while len(chain) >= 2 and ((chain[-1][0]-chain[-2][0])*(p[1]-chain[-2][1])
                                    - (chain[-1][1]-chain[-2][1])*(p[0]-chain[-2][0])) <= 0:
                chain.pop()
            chain.append(p)
        return chain

    lower = half_chain(pts)
    upper = half_chain(reversed(pts))
    # omit last point of each (it's repeated)
    return lower[:-1] + upper[:-1]

def find_closest_edge(point, edges):
    """
    Finds the closest edge to a point in a list of edges.
    Returns the normal vector of the closest edge.
    """
    min_dist = float("inf")
    closest_edge_index = -1

    for i in range(len(edges)):
        # only use x,y components
        p1 = np.array(edges[i][:2])
        p2 = np.array(edges[(i + 1) % len(edges)][:2])
        pt = np.array(point)  # already 2D

        line_vec = p2 - p1
        point_vec = pt - p1

        line_len_sq = np.dot(line_vec, line_vec)
        if line_len_sq == 0:
            dist = np.linalg.norm(point_vec)
        else:
            t = max(0, min(1, np.dot(point_vec, line_vec) / line_len_sq))
            closest_point_on_segment = p1 + t * line_vec
            dist = np.linalg.norm(pt - closest_point_on_segment)

        if dist < min_dist:
            min_dist = dist
            closest_edge_index = i

    # recompute edge normal in 2D
    p1 = np.array(edges[closest_edge_index][:2])
    p2 = np.array(edges[(closest_edge_index + 1) % len(edges)][:2])
    edge_vec = p2 - p1
    normal = np.array([edge_vec[1], -edge_vec[0]])
    normal = normal / np.linalg.norm(normal)
    return normal

def distance_to_closest_edge(point, edges):
    """
    Calculates the distance from a point to the closest edge in a list of edges.
    """
    min_dist = float("inf")

    for i in range(len(edges)):
        # only use x,y components
        p1 = np.array(edges[i][:2])
        p2 = np.array(edges[(i + 1) % len(edges)][:2])
        pt = np.array(point[:2])

        line_vec = p2 - p1
        point_vec = pt - p1

        line_len_sq = np.dot(line_vec, line_vec)
        if line_len_sq == 0:
            dist = np.linalg.norm(point_vec)
        else:
            t = max(0, min(1, np.dot(point_vec, line_vec) / line_len_sq))
            closest_point_on_segment = p1 + t * line_vec
            dist = np.linalg.norm(pt - closest_point_on_segment)

        if dist < min_dist:
            min_dist = dist
            
    return min_dist

def point_in_poly(x, y, poly):
    """
    poly: list of (x,y,...) vertices, closed or not (this will handle both)
    returns True if point is strictly inside, False otherwise (including on the edge)
    """
    inside = False
    n = len(poly)
    for i in range(n):
        p0 = poly[i]
        x0, y0 = p0[0], p0[1]
        p1 = poly[(i+1) % n]
        x1, y1 = p1[0], p1[1]
        # Check if edge crosses horizontal ray to the right of (x,y)
        intersects = ((y0 > y) != (y1 > y)) and \
                    (x < (x1 - x0) * (y - y0) / (y1 - y0) + x0)
        if intersects:
            inside = not inside
    return inside

class Bounds:
    def __init__(self, coords):
        """
        Calculates the bounding box of a set of coordinates.
        
        coords - a list of coordinates, each coordinate is a tuple (x, y, z) or (x, y)
        Returns a tuple (min_x, max_x, min_y, max_y, min_z, max_z) or without z if 2D.
        """

        if not coords:
            return None
        
        self.coords = coords

        self.min_x = min(coord[0] for coord in coords)
        self.max_x = max(coord[0] for coord in coords)
        self.min_y = min(coord[1] for coord in coords)
        self.max_y = max(coord[1] for coord in coords)

        if len(coords[0]) == 3:  # 3D coordinates
            self.min_z = min(coord[2] for coord in coords)
            self.max_z = max(coord[2] for coord in coords)