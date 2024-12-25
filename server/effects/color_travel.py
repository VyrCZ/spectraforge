from effects.base_effect import LightEffect, ParamType
import mathutils as mu
import time

class ColorSweep(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 40, min=1, max=100, step=1)
        self.color = self.add_parameter("Color", ParamType.COLOR, "#FF0000")
        self.falloff = self.add_parameter("Falloff", ParamType.SLIDER, 10, min=1, max=50, step=1)
        self.current_pixel = self.falloff.get()

    def update(self):
        self.current_pixel += 1
        self.pixels.fill((0, 0, 0))
        for i in range(int(self.falloff.get())):
            brightness = 1 - (i / self.falloff.get())
            new_color = [channel * brightness for channel in self.color.get()]
            #print(f"Pixel: {self.current_pixel - i}, Color: {new_color}")
            self.pixels[int(mu.wrap(self.current_pixel - i, 0, len(self.pixels) - 1))] = new_color
        time.sleep(1 / self.speed.get())
        self.pixels.show()