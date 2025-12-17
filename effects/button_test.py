from modules.effect import LightEffect, ParamType, EffectType
import modules.mathutils as mu
import time

class ButtonTest(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Button Test", EffectType.UNIVERSAL)
        self.color = self.add_parameter("Color", ParamType.COLOR, "#FF0000")
        self.toggle = self.add_parameter("Toggle", ParamType.BUTTON, None, onClick=self.toggle_effect)
        self.leds_on = True
        self.off_time = 0.5
        self.t = 0
        self.dir = 1

    def update(self):
        if self.leds_on:
            self.renderer.fill(self.color.get())
        else:
            self.renderer.clear()
        self.renderer.show()

    def toggle_effect(self):
        self.leds_on = not self.leds_on