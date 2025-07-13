import numpy as np
import time
import math
import random
import sys
import os
# add parent directory to path so I can import my scripts from a subfolder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import modules.mathutils as mu
import legacy.tree_sim as tree_sim

class Spiral(tree_sim.Simulation):
    def __init__(self):
        super().__init__()
        self.current_z = 0
        self.current_dir = 1
        self.dir = [1, 0]
        self.selected_color = [255, 0, 0]
        self.point_radius = 0.5
        self.size = 1

    def update(self):
        self.current_z += 0.1 * self.current_dir
        self.dir = mu.rotate_direction(self.dir, 5)
        if self.current_z > self.height:
            self.current_dir = -1
        if self.current_z < 0:
            self.current_dir = 1
        dist = (self.diameter / 2) * ((self.height - self.current_z) / self.height)
        point = [dist * self.dir[0], dist * self.dir[1], self.current_z]
        for i in range(self.num_points):
            self.colors[i] = [
                channel * (1 - mu.normalize(mu.clamp(abs(math.dist(self.points[i], point)), 0, self.size), 0, self.size))
                if math.dist(self.points[i], point) > self.point_radius else channel
                for channel in self.selected_color
            ]

        self.update_colors()

lights = Spiral()
while True:
    lights.update()
    time.sleep(0.1)  # Pause for a short time to visualize changes