from modules.effect import LightEffect, ParamType, EffectType

class YCHeck(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "YCheck", EffectType.UNIVERSAL)
        self.miny = min(coord[1] for coord in coords)
        self.maxy = max(coord[1] for coord in coords)

    def update(self):
        for led in range(len(self.renderer)):
            b = (self.coords[led][1] - self.miny) / (self.maxy - self.miny)
            self.renderer[led] = [0, int((1 - b) * 255), 0]  # Green intensity based on y-coordinate
        self.renderer.show()