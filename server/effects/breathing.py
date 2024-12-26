from effects.base_effect import LightEffect, ParamType
import mathutils as mu
import time

class Breathing(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        # define config variables
        self.fade_speed = self.add_parameter("Fade Speed", ParamType.SLIDER, 0.025, min=0.01, max=0.1, step=0.01)
        self.color = self.add_parameter("Color", ParamType.COLOR, "#FF0000")
        self.off_time = 0.5
        self.t = 0
        self.dir = 1

    def update(self):
        # change the colors, update the tree
        self.t += self.dir * self.fade_speed.get()
        if self.t >= 1:
            self.dir = -1
        elif self.t <= 0:
            self.dir = 1
            time.sleep(self.off_time)
        for i in range(len(self.pixels)):
            self.pixels[i] = [mu.clamp(int(channel * self.t), 0, 255) for channel in self.color.get()]
        self.pixels.show()