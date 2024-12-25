from effects.base_effect import LightEffect, ParamType
import mathutils as mu
import time

class Fireplace(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.color = self.add_parameter("Base Color", ParamType.COLOR, "#FF0000")
        self.level = self.add_parameter("Level", ParamType.SLIDER, self.height / 2, min=0, max=self.height)
    def update(self):
        self.pixels.fill(self.color.get())
        self.pixels.show()