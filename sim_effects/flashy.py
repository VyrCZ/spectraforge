import numpy as np
import time
import math
import random
import sys
import os
# add parent directory to python path so I can import my scripts from inside of a subfolder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import mathutils as mu
import tree_sim

class Flashy(tree_sim.Simulation):
    """
    Random flashing between selected colors
    """
    def __init__(self):
        super().__init__() # don't forget to call the parent's init
        # define config variables
        self.color_bank = [
            [255, 0, 0],
            [0, 255, 0]
        ]

    def update(self):
        # change the colors, update the tree
        for i in range(self.num_points):
            self.colors[i] = random.choice(self.color_bank)
        self.update_colors()

lights = Flashy()
while True:
    lights.update()
    time.sleep(0.1)  # Regulate speed of the effect