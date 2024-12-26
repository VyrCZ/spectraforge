from effects.base_effect import LightEffect, ParamType
import mathutils as mu
import time
import colorsys

class Rainbow(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 0.1, min=0.5, max=50, step=0.1)
        self.reverse = self.add_parameter("Reverse", ParamType.CHECKBOX, False)
        self.current_z = 0

    def update(self):
        #print(f"Running rainbow with speed {self.speed.get()} and reverse {self.reverse.get()}")
        if self.reverse.get():
            self.current_z -= self.speed.get()
        else:
            self.current_z += self.speed.get()
        if self.current_z > self.height:
            self.current_z = 0
        for i in range(len(self.pixels)):
            normalized_rgb = list(colorsys.hsv_to_rgb(mu.normalize(mu.wrap(self.coords[i][2] - self.current_z, 0, self.height), 0, self.height), 1, 1))
            self.pixels[i] = tuple([int(channel * 255) for channel in normalized_rgb])
        self.pixels.show()