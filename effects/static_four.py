from modules.effect import LightEffect, ParamType, EffectType
import modules.mathutils as mu
import time

class StaticFour(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Static Four", EffectType.PRIMARILY_3D)
        self.colors = [
            self.add_parameter("Color 1", ParamType.COLOR, "#FF0000"),
            self.add_parameter("Color 2", ParamType.COLOR, "#FFFF00"),
            self.add_parameter("Color 3", ParamType.COLOR, "#00FF00"),
            self.add_parameter("Color 4", ParamType.COLOR, "#0000FF")
        ]

    def update(self):
        for i in range(len(self.renderer)):
            self.renderer[i] = self.colors[i % 4].get()
        self.renderer.show()