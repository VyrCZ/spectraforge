from modules.effect import LightEffect, ParamType, EffectType
import colorsys

class BarTest(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "BarTest", EffectType.UNIVERSAL)
        self.bar_count = self.add_parameter("Bar Count", ParamType.SLIDER, 8, min=4, max=64, step=1)
        self.minx = min(coord[0] for coord in coords)
        self.maxx = max(coord[0] for coord in coords)

    def update(self):
        self.thresholds = []
        step = 1 / int(self.bar_count.get())
        for i in range(int(self.bar_count.get())):
            self.thresholds.append(step * i)
        for led in range(len(self.renderer)):
            hue_full = (self.coords[led][0] - self.minx) / (self.maxx - self.minx)
            # floor the hue to the nearest threshold
            hue = min(self.thresholds, key=lambda x: abs(x - hue_full))
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            self.renderer[led] = [int(r * 255), int(g * 255), int(b * 255)]
        self.renderer.show()