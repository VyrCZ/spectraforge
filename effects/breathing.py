from modules.effect import LightEffect, ParamType, EffectType
import modules.mathutils as mu
import time

class Breathing(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords, "Breathing", EffectType.UNIVERSAL)
        self.fade_speed = self.add_parameter("Fade Speed", ParamType.SLIDER, 50, min=1, max=500, step=1)
        self.color = self.add_parameter("Color", ParamType.COLOR, "#FF0000")
        self.off_time = 0.5
        self.t = 0
        self.dir = 1

    def update(self):
        self.t += self.dir * self.fade_speed.get() / 10000
        if self.t >= 1:
            self.dir = -1
        elif self.t <= 0:
            self.dir = 1
            time.sleep(self.off_time)
        for i in range(len(self.pixels)):
            self.pixels[i] = [mu.clamp(int(channel * self.t), 0, 255) for channel in self.color.get()]
        self.pixels.show()