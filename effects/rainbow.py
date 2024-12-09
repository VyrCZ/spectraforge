import numpy as np
import time
import math
import colorsys
import sys
import os
# add parent directory to path so I can import my scripts from a subfolder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import mathutils as mu
import tree_sim

class RedWave(tree_sim.Simulation):
    def __init__(self):
        super().__init__()
        self.current_z = 0

    def update(self):
        self.current_z += 0.1
        if self.current_z > self.height:
            self.current_z = 0
        for i in range(self.num_points):
            #new_color = [255, 0, 0]
            #new_color[0] = lerp(0, 255, 1 - normalize(clamp(abs(self.points[i][2] - self.current_z), 0, self.height/2), 0, self.height/2))
            normalized_rgb = list(colorsys.hsv_to_rgb(mu.normalize(mu.wrap(self.points[i][2] - self.current_z, 0, self.height), 0, self.height), 1, 1))
            self.colors[i] = [int(channel * 255) for channel in normalized_rgb]
        self.update_colors()

lights = RedWave()
while True:
    lights.update()
    time.sleep(0.1)  # Pause for a short time to visualize changes