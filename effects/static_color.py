from modules.effect import LightEffect, ParamType, EffectType

class StaticColor(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords, "Static Color", EffectType.UNIVERSAL)
        self.color = self.add_parameter("Color", ParamType.COLOR, "#FF0000")

    def update(self):
        self.pixels.fill(self.color.get())
        self.pixels.show()