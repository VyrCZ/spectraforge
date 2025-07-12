from modules.effect import LightEffect, ParamType, EffectType

class StaticColor(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Static Color", EffectType.UNIVERSAL)
        self.color = self.add_parameter("Color", ParamType.COLOR, "#FF0000")

    def update(self):
        self.renderer.fill(self.color.get())
        self.renderer.show()