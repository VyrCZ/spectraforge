from modules.effect import LightEffect, ParamType, EffectType
import modules.mathutils as mu
import time
import colorsys

class Rainbow(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Rainbow", EffectType.UNIVERSAL)
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 0.1, min=0.5, max=50, step=0.1)
        self.reverse = self.add_parameter("Reverse", ParamType.CHECKBOX, False)
        self.current_y = 0

    def update(self):
        #print(f"Running rainbow with speed {self.speed.get()} and reverse {self.reverse.get()}")
        if self.reverse.get():
            self.current_y -= self.speed.get()
        else:
            self.current_y += self.speed.get()
        if self.current_y > self.height:
            self.current_y = 0
        for i in range(len(self.renderer.leds)):
            normalized_rgb = list(colorsys.hsv_to_rgb(mu.normalize(mu.wrap(self.coords[i][1] - self.current_y, 0, self.height), 0, self.height), 1, 1))
            self.renderer.leds[i] = tuple([int(channel * 255) for channel in normalized_rgb])
        self.renderer.show()