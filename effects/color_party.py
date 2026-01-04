from modules.effect import LightEffect, ParamType, EffectType
import random
import colorsys
import time

class ColorParty(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Color Party", EffectType.UNIVERSAL)
        self.fade_speed = self.add_parameter("Fade Speed", ParamType.SLIDER, 5, min=1, max=10, step=0.1)
        self.button = self.add_parameter("Party Time!", ParamType.BUTTON, None, onClick=self.on_button_press)
        # frame delay in milliseconds to decouple from host update speed
        self.frame_delay = 50
        # range 0-1
        self.hue = 0
        self.value = 0

    def update(self):
        color = colorsys.hsv_to_rgb(self.hue, 1, self.value)
        self.value -= self.fade_speed.get() / 100.0
        if self.value < 0:
            self.value = 0
            self.hue = random.random()
        # convert color to 0-255
        color = [int(c * 255) for c in color]
        self.renderer.fill(color)
        self.renderer.show()
        # sleep to enforce a consistent frame delay (ms -> s)
        time.sleep(self.frame_delay / 1000.0)

    def on_button_press(self):
        print("Party Time!")
        self.value = 1.0
        self.hue = random.random()