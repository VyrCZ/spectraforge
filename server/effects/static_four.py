from effects.base_effect import LightEffect
import mathutils as mu
import time

class StaticFour(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.colors = [
            self.add_parameter("Color 1", "color", "#FF0000"),
            self.add_parameter("Color 2", "color", "#FFFF00"),
            self.add_parameter("Color 3", "color", "#00FF00"),
            self.add_parameter("Color 4", "color", "#0000FF")
        ]

    def update(self):
        for i in range(len(self.pixels)):
            self.pixels[i] = self.colors[i % 4].get()