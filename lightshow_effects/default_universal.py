from modules.lightshow_effect import *
import modules.mathutils as mu
import colorsys
from modules.effect import EffectType

@namespace("")
class DefaultUniversal(LightshowEffects):
    def __init__(self, coords):
        super().__init__(coords)

    @l_effect(EffectType.UNIVERSAL)
    def solid_color(self, steps, color):
        frames = []
        for _ in range(steps):
            frame = [color] * len(self.coords)
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def fade(self, steps, color1, color2):
        step_r = (color2[0] - color1[0]) / steps
        step_g = (color2[1] - color1[1]) / steps
        step_b = (color2[2] - color1[2]) / steps

        frames = []
        for step in range(steps):
            intermediate_color = (
                int(color1[0] + step * step_r),
                int(color1[1] + step * step_g),
                int(color1[2] + step * step_b),
            )
            frame = [intermediate_color] * len(self.coords)
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def flash(self, steps, color1, color2):
        frames = []
        for step in range(steps):
            if step % 2 == 0:
                frame = [color1] * len(self.coords)
            else:
                frame = [color2] * len(self.coords)
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def flash2(self, steps, color1, color2):
        frames = []
        for step in range(steps):
            frame = []
            for i in range(len(self.coords)):
                if i % 2 == step % 2:
                    frame.append(color1)
                else:
                    frame.append(color2)
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def swipe_up(self, steps, color, width=100):
        current_z = 0 - width
        frames = []
        for step in range(steps):
            current_z += (self.bounds.max_z + 2 * width) / steps
            frame = [None] * len(self.coords)
            for i in range(len(self.coords)):
                dist = abs(self.coords[i][2] - current_z)
                if dist < width / 2:
                    frame[i] = mu.color_lerp((0, 0, 0), color, mu.normalize(dist, 0, width / 2))
            frames.append(frame)
        return frames
    
    @l_effect(EffectType.UNIVERSAL)
    def swipe_down(self, steps, color, width=100):
        current_z = self.bounds.max_z + width
        frames = []
        for step in range(steps):
            current_z -= (self.bounds.max_z + 2 * width) / steps
            frame = [None] * len(self.coords)
            for i in range(len(self.coords)):
                dist = abs(self.coords[i][2] - current_z)
                if dist < width / 2:
                    frame[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def swipe_right(self, steps, color, width=50):
        current_x = self.bounds.min_x - width
        frames = []
        for step in range(steps):
            current_x += (self.bounds.max_x - self.bounds.min_x + 2 * width) / steps
            frame = [None] * len(self.coords)
            for i in range(len(self.coords)):
                dist = abs(self.coords[i][0] - current_x)
                if dist < width / 2:
                    frame[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def swipe_left(self, steps, color, width=50):
        current_x = self.bounds.max_x + width
        frames = []
        for step in range(steps):
            current_x -= (self.bounds.max_x - self.bounds.min_x + 2 * width) / steps
            frame = [None] * len(self.coords)
            for i in range(len(self.coords)):
                dist = abs(self.coords[i][0] - current_x)
                if dist < width / 2:
                    frame[i] = mu.color_lerp(color, (0, 0, 0), mu.normalize(dist, 0, width / 2))
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def rainbow(self, steps, speed=10):
        current_z = 0
        frames = []
        for step in range(steps):
            current_z += speed
            if current_z > self.bounds.max_z:
                current_z = 0
            frame = [None] * len(self.coords)
            for i in range(len(self.coords)):
                normalized_rgb = list(colorsys.hsv_to_rgb(
                    mu.normalize(mu.wrap(self.coords[i][2] - current_z, 0, self.bounds.max_z), 0, self.bounds.max_z), 1, 1))
                frame[i] = tuple([int(channel * 255) for channel in normalized_rgb])
            frames.append(frame)
        return frames
    
    @l_effect(EffectType.UNIVERSAL)
    def gradient(self, steps, color1, color2, speed=10):
        current_z = 0
        frames = []
        for step in range(steps):
            current_z += speed
            if current_z > self.bounds.max_z:
                current_z = 0
            frame = [None] * len(self.coords)
            for i in range(len(self.coords)):
                normalized_rgb = mu.color_lerp(color1, color2, mu.normalize(mu.wrap(self.coords[i][2] - current_z, 0, self.bounds.max_z), 0, self.bounds.max_z))
                frame[i] = normalized_rgb
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def string_up(self, steps, color, trail_length=25):
        current_pixel = -trail_length
        frames = []
        for step in range(steps):
            current_pixel += int((len(self.coords) + 2 * trail_length) / steps)
            frame = [None] * len(self.coords)
            for i in range(trail_length):
                pos = current_pixel + i
                if pos < len(self.coords) and pos >= 0:
                    frame[pos] = mu.color_lerp((0, 0, 0), color, mu.normalize(i, 0, trail_length))
            frames.append(frame)
        return frames
    
    @l_effect(EffectType.UNIVERSAL)
    def string_down(self, steps, color, trail_length=25):
        current_pixel = len(self.coords) + trail_length
        frames = []
        for step in range(steps):
            current_pixel -= int((len(self.coords) + 2 * trail_length) / steps)
            frame = [None] * len(self.coords)
            for i in range(trail_length):
                pos = current_pixel - i
                if pos < len(self.coords) and pos >= 0:
                    frame[pos] = mu.color_lerp((0, 0, 0), color, mu.normalize(i, 0, trail_length))
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def split_vertical(self, steps, color1, color2):
        mid_x = (self.bounds.min_x + self.bounds.max_x) / 2
        frames = []
        for step in range(steps):
            frame = [None] * len(self.coords)
            for i in range(len(self.coords)):
                if self.coords[i][0] < mid_x:
                    frame[i] = color1
                else:
                    frame[i] = color2
            frames.append(frame)
        return frames