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
        self.edges = mu.convex_hull(coords)

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
        if not mu.point_in_poly(new_pos[0], new_pos[1], self.edges):
            # bounce
            normal = mu.find_closest_edge(new_pos, self.edges)
            
            # formula for reflection: R-> = D-> - 2(D-> . N->)N->
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