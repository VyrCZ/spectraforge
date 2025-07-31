from modules.lightshow_effect import *
import modules.mathutils as mu
import colorsys
from modules.effect import EffectType

@namespace("")
class Default3D(LightshowEffects):
    def __init__(self, coords):
        super().__init__(coords)

    @l_effect(EffectType.ONLY_3D)
    def swipe_forward(self, steps, color, width=50):
        current_y = self.bounds.min_y - width
        frames = []
        for step in range(steps):
            current_y += (self.bounds.max_y - self.bounds.min_y + 2 * width) / steps
            frame = [None] * len(self.coords)
            for i in range(len(self.coords)):
                dist = abs(self.coords[i][1] - current_y)
                if dist < width / 2:
                    frame[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
            frames.append(frame)
        return frames

    @l_effect(EffectType.ONLY_3D)
    def swipe_backward(self, steps, color, width=50):
        current_y = self.bounds.max_y + width
        frames = []
        for step in range(steps):
            current_y -= (self.bounds.max_y - self.bounds.min_y + 2 * width) / steps
            frame = [None] * len(self.coords)
            for i in range(len(self.coords)):
                dist = abs(self.coords[i][1] - current_y)
                if dist < width / 2:
                    frame[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
            frames.append(frame)
        return frames