import numpy as np
import time
import math
import random
import sys
import os
# add parent directory to path so I can import my scripts from a subfolder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import mathutils as mu
import tree_sim

class Grow(tree_sim.Simulation):
    def __init__(self):
        super().__init__()
        self.active_color = None
        self.growing = False
        self.reset()

    def reset(self):
        self.growing = not self.growing
        if self.growing:
            self.active_color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        self.random_point = random.choice(self.points)
        self.current_size = 0 if self.growing else 4

    def update(self):
        self.current_size += 0.1 if self.growing else -0.1
        if self.current_size >= 4 or self.current_size <= 0:
            self.reset()
        if self.current_size <= 0:
            self.current_size = 0.1
        self.current_size = round(self.current_size, 1)
        print(self.current_size)
        for i in range(self.num_points):
            active_color = [channel * (1 - mu.normalize(mu.clamp(abs(math.dist(self.points[i], self.random_point)), 0, self.current_size), 0, self.current_size)) for channel in self.active_color]
            self.colors[i] = active_color  # Update specific point's color

        self.update_colors()

lights = Grow()
while True:
    lights.update()
    time.sleep(0.1)  # Pause for a short time to visualize changes