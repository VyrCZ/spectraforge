from modules.effect import LightEffect, ParamType, EffectType
import modules.mathutils as mu
import time
from modules.log_manager import Log

class Breathing(LightEffect):
    def __init__(self, renderer, coords):
        # Init the effect
        super().__init__(renderer, coords, "Breathing", EffectType.UNIVERSAL)
        # ! Parameters will work in sandbox, however only the default values will be used and can't be changed at the moment
        self.fade_speed = self.add_parameter("Fade Speed", ParamType.SLIDER, 10, min=1, max=500, step=1)
        self.color = self.add_parameter("Color", ParamType.COLOR, "#FF0000")
        self.off_time = 0.5     # Time to wait when the effect is fully faded out
        self.t = 0              # Time variable for the breathing effect
        self.dir = 1            # Direction of the breathing effect (1 for fading in, -1 for fading out)
        #Log.debug("Sandbox/Breathing", "Breathing effect initialized with default parameters.")

    def update(self):
        #Log.debug("Sandbox/Breathing", "Updating breathing effect")
        # Update the time variable
        self.t += self.dir * self.fade_speed.get() / 10000
        # Change direction if the breathing effect is fully faded in or out
        if self.t >= 1:
            self.dir = -1
        elif self.t <= 0:
            self.dir = 1
            time.sleep(self.off_time)
        # Update the leds and the renderer
        for i in range(len(self.renderer)):
            self.renderer[i] = [mu.clamp(int(channel * self.t), 0, 255) for channel in self.color.get()]
        self.renderer.show()