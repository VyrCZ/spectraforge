import numpy as np
import time
import math
import random
import sys
import os
# add parent directory to path so I can import my scripts from a subfolder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mathutils import *
import tree_sim

class Flashy(tree_sim.Simulation):
    def __init__(self):
        super().__init__()
        self.color_bank = [
            [255, 0, 0],
            [0, 255, 0]
        ]

    def update(self):
        for i in range(self.num_points):
            self.colors[i] = random.choice(self.color_bank)

        self.update_colors()

lights = Flashy()
while True:
    lights.update()
    time.sleep(0.1)  # Pause for a short time to visualize changes