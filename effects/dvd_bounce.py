from modules.effect import LightEffect, ParamType, EffectType
import modules.mathutils as mu
import time
import random
import numpy as np
from modules.log_manager import Log

class DVDBounce(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "DVD Bounce", EffectType.ONLY_2D)
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 50, min=1, max=25, step=1)
        self.size = self.add_parameter("Size", ParamType.SLIDER, 10, min=1, max=50, step=1) # % of height
        self.color = self.add_parameter("Color", ParamType.COLOR, "#FF0000")
        self.direction = [
            random.choice([-1, 1]),  # Randomly choose horizontal direction
            random.choice([-1, 1]),  # Randomly choose vertical direction
        ]
        # start in the center of the screen
        min_x = min(coord[0] for coord in coords)
        max_x = max(coord[0] for coord in coords)
        min_y = min(coord[1] for coord in coords)
        max_y = max(coord[1] for coord in coords)
        self.position = [
            min_x + (max_x - min_x) / 2,
            min_y + (max_y - min_y) / 2,
        ]
        self.frame_length = 1/60
        self.edges = self.convex_hull(coords)

    def convex_hull(self, points):
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
    
    def find_closest_edge(self, point, edges):
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

    def point_in_poly(self, x, y, poly):
        """
        poly: list of (x,y,...) vertices, closed or not (we’ll handle closure)
        returns True if point is strictly inside, False otherwise
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

    def update(self):
        self.renderer.clear()
        move_distance = self.speed.get() * self.frame_length * 150
        # update position
        new_pos = [
            self.position[0] + self.direction[0] * move_distance,
            self.position[1] + self.direction[1] * move_distance
        ]

        #self.renderer.debug_draw.line(list(self.position), list(new_pos), color=(0, 255, 0))
        # check bounds
        if not self.point_in_poly(new_pos[0], new_pos[1], self.edges):
            # bounce
            normal = self.find_closest_edge(new_pos, self.edges)
            
            # D′=D−2(D⋅n)n
            d = np.array(self.direction)
            dot_product = np.dot(d, normal)
            new_direction = d - 2 * dot_product * normal
            
            self.direction = new_direction.tolist()

            # After bouncing, recalculate position for one step to avoid getting stuck outside
            self.position[0] += self.direction[0] * move_distance
            self.position[1] += self.direction[1] * move_distance
        else:
            self.position = new_pos
        #Log.debug("DVD", f"Position: {self.position}, Direction: {self.direction}")
            
        max_dist = (max(coord[1] for coord in self.coords) - min(coord[1] for coord in self.coords)) * self.size.get() / 100
        for idx, coord in enumerate(self.coords):
            dist = mu.distance(self.position, coord)
            ratio = 1 - (dist / max_dist)
            if ratio < 0:
                ratio = 0
            elif ratio > 1:
                ratio = 1
            col = self.color.get()
            self.renderer[idx] = [
                int(col[0] * ratio),
                int(col[1] * ratio),
                int(col[2] * ratio)
            ]
        self.renderer.show()
        time.sleep(self.frame_length)