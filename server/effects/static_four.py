from effects.base_effect import LightEffect, ParamType
import mathutils as mu
import time

class StaticFour(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.colors = [
            self.add_parameter("Color 1", ParamType.COLOR, "#FF0000"),
            self.add_parameter("Color 2", ParamType.COLOR, "#FFFF00"),
            self.add_parameter("Color 3", ParamType.COLOR, "#00FF00"),
            self.add_parameter("Color 4", ParamType.COLOR, "#0000FF")
        ]

    def update(self):
        for i in range(len(self.pixels)):
            self.pixels[i] = self.colors[i % 4].get()
        self.pixels.show()