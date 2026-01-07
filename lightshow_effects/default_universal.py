from modules.lightshow_effects import LightshowEffects, l_effect, namespace, CustomParamType
import modules.mathutils as mu
import colorsys
from modules.effect import EffectType

# not typing CustomParamType.Color 100 times
Color = CustomParamType.Color

@namespace("")
class DefaultUniversal(LightshowEffects):
    def __init__(self, coords):
        super().__init__(coords)

    @l_effect(EffectType.UNIVERSAL)
    def solid_color(self, steps: int, color: Color = Color.white):
        frames = []
        for _ in range(steps):
            frame = [(color[0], color[1], color[2], color[3])] * len(self.coords)
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def fade(self, steps: int, color_from: Color = Color.white, color_to: Color = Color.white):
        step_r = (color_to[0] - color_from[0]) / steps
        step_g = (color_to[1] - color_from[1]) / steps
        step_b = (color_to[2] - color_from[2]) / steps
        step_a = (color_to[3] - color_from[3]) / steps

        frames = []
        for step in range(steps):
            intermediate_color = (
                int(color_from[0] + step * step_r),
                int(color_from[1] + step * step_g),
                int(color_from[2] + step * step_b),
                int(color_from[3] + step * step_a),
            )
            frame = [intermediate_color] * len(self.coords)
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def flash_full(self, steps: int, color1: Color = Color.white, color2: Color = Color.white):
        frames = []
        for step in range(steps):
            if step % 2 == 0:
                frame = [(color1[0], color1[1], color1[2], color1[3])] * len(self.coords)
            else:
                frame = [(color2[0], color2[1], color2[2], color2[3])] * len(self.coords)
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def flash_individual(self, steps: int, color1: Color = Color.white, color2: Color = Color.white):
        frames = []
        for step in range(steps):
            frame = []
            for i in range(len(self.coords)):
                if i % 2 == step % 2:
                    frame.append((color1[0], color1[1], color1[2], color1[3]))
                else:
                    frame.append((color2[0], color2[1], color2[2], color2[3]))
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def swipe_up(self, steps: int, color: Color = Color.white, width: int = 100, background_color: Color = Color.transparent):
        current_z = 0 - width
        frames = []
        for step in range(steps):
            current_z += (self.bounds.max_z + 2 * width) / steps
            frame = [background_color] * len(self.coords)
            for i in range(len(self.coords)):
                dist = abs(self.coords[i][2] - current_z)
                if dist < width / 2:
                    lerp_color = mu.color_lerp(background_color, (color[0], color[1], color[2], color[3]), mu.normalize(dist, 0, width / 2))
                    frame[i] = lerp_color
            frames.append(frame)
        return frames
    
    @l_effect(EffectType.UNIVERSAL)
    def swipe_down(self, steps: int, color: Color = Color.white, width: int = 100, background_color: Color = Color.transparent):
        current_z = self.bounds.max_z + width
        frames = []
        for step in range(steps):
            current_z -= (self.bounds.max_z + 2 * width) / steps
            frame = [background_color] * len(self.coords)
            for i in range(len(self.coords)):
                dist = abs(self.coords[i][2] - current_z)
                if dist < width / 2:
                    lerp_color = mu.color_lerp((color[0], color[1], color[2], color[3]), background_color, mu.normalize(dist, 0, width / 2))
                    frame[i] = lerp_color
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def swipe_right(self, steps: int, color: Color = Color.white, width: int = 50, background_color: Color = Color.transparent):
        current_x = self.bounds.min_x - width
        frames = []
        for step in range(steps):
            current_x += (self.bounds.max_x - self.bounds.min_x + 2 * width) / steps
            frame = [background_color] * len(self.coords)
            for i in range(len(self.coords)):
                dist = abs(self.coords[i][0] - current_x)
                if dist < width / 2:
                    lerp_color = mu.color_lerp((color[0], color[1], color[2], color[3]), background_color, mu.normalize(dist, 0, width / 2))
                    frame[i] = lerp_color
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def swipe_left(self, steps: int, color: Color = Color.white, width: int = 50, background_color: Color = Color.transparent):
        current_x = self.bounds.max_x + width
        frames = []
        for step in range(steps):
            current_x -= (self.bounds.max_x - self.bounds.min_x + 2 * width) / steps
            frame = [background_color] * len(self.coords)
            for i in range(len(self.coords)):
                dist = abs(self.coords[i][0] - current_x)
                if dist < width / 2:
                    lerp_color = mu.color_lerp((color[0], color[1], color[2], color[3]), background_color, mu.normalize(dist, 0, width / 2))
                    frame[i] = lerp_color
            frames.append(frame)
        return frames

    # swipe_arrow effects: pointy lead (arrow head)
    @l_effect(EffectType.UNIVERSAL)
    def swipe_arrow_up(self, steps: int, color: Color = Color.white, width: int = 100, head_length: int = 50, background_color: Color = Color.transparent):
        current_z = 0 - width
        center_x = (self.bounds.min_x + self.bounds.max_x) / 2
        center_y = (self.bounds.min_y + self.bounds.max_y) / 2
        frames = []
        for step in range(steps):
            current_z += (self.bounds.max_z + 2 * width) / steps
            frame = [background_color] * len(self.coords)
            for i in range(len(self.coords)):
                dz = current_z - self.coords[i][2]  # distance behind tip
                if dz >= 0 and dz <= head_length:
                    allowed_radius = (dz / head_length) * (width / 2)
                    lateral = ((self.coords[i][0] - center_x) ** 2 + (self.coords[i][1] - center_y) ** 2) ** 0.5
                    if lateral <= allowed_radius:
                        strength = 1.0 - mu.normalize(dz, 0, head_length)  # tip strongest
                        lerp_color = mu.color_lerp(background_color, (color[0], color[1], color[2], color[3]), strength)
                        frame[i] = lerp_color
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def swipe_arrow_down(self, steps: int, color: Color = Color.white, width: int = 100, head_length: int = 50, background_color: Color = Color.transparent):
        current_z = self.bounds.max_z + width
        center_x = (self.bounds.min_x + self.bounds.max_x) / 2
        center_y = (self.bounds.min_y + self.bounds.max_y) / 2
        frames = []
        for step in range(steps):
            current_z -= (self.bounds.max_z + 2 * width) / steps
            frame = [background_color] * len(self.coords)
            for i in range(len(self.coords)):
                dz = self.coords[i][2] - current_z  # distance behind tip
                if dz >= 0 and dz <= head_length:
                    allowed_radius = (dz / head_length) * (width / 2)
                    lateral = ((self.coords[i][0] - center_x) ** 2 + (self.coords[i][1] - center_y) ** 2) ** 0.5
                    if lateral <= allowed_radius:
                        strength = 1.0 - mu.normalize(dz, 0, head_length)
                        lerp_color = mu.color_lerp(background_color, (color[0], color[1], color[2], color[3]), strength)
                        frame[i] = lerp_color
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def swipe_arrow_right(self, steps: int, color: Color = Color.white, width: int = 50, head_length: int = 50, background_color: Color = Color.transparent):
        current_x = self.bounds.min_x - width
        center_y = (self.bounds.min_y + self.bounds.max_y) / 2
        center_z = (self.bounds.min_z + self.bounds.max_z) / 2
        frames = []
        for step in range(steps):
            current_x += (self.bounds.max_x - self.bounds.min_x + 2 * width) / steps
            frame = [background_color] * len(self.coords)
            for i in range(len(self.coords)):
                dz = current_x - self.coords[i][0]  # distance behind tip along x
                if dz >= 0 and dz <= head_length:
                    allowed_radius = (dz / head_length) * (width / 2)
                    lateral = ((self.coords[i][1] - center_y) ** 2 + (self.coords[i][2] - center_z) ** 2) ** 0.5
                    if lateral <= allowed_radius:
                        strength = 1.0 - mu.normalize(dz, 0, head_length)
                        lerp_color = mu.color_lerp(background_color, (color[0], color[1], color[2], color[3]), strength)
                        frame[i] = lerp_color
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def swipe_arrow_left(self, steps: int, color: Color = Color.white, width: int = 50, head_length: int = 50, background_color: Color = Color.transparent):
        current_x = self.bounds.max_x + width
        center_y = (self.bounds.min_y + self.bounds.max_y) / 2
        center_z = (self.bounds.min_z + self.bounds.max_z) / 2
        frames = []
        for step in range(steps):
            current_x -= (self.bounds.max_x - self.bounds.min_x + 2 * width) / steps
            frame = [background_color] * len(self.coords)
            for i in range(len(self.coords)):
                dz = self.coords[i][0] - current_x  # distance behind tip along x
                if dz >= 0 and dz <= head_length:
                    allowed_radius = (dz / head_length) * (width / 2)
                    lateral = ((self.coords[i][1] - center_y) ** 2 + (self.coords[i][2] - center_z) ** 2) ** 0.5
                    if lateral <= allowed_radius:
                        strength = 1.0 - mu.normalize(dz, 0, head_length)
                        lerp_color = mu.color_lerp(background_color, (color[0], color[1], color[2], color[3]), strength)
                        frame[i] = lerp_color
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def rainbow(self, steps: int, speed: float = 10, background_color: Color = Color.transparent):
        current_y = 0
        frames = []
        for step in range(steps):
            current_y += speed
            if current_y > self.bounds.max_y:
                current_y = 0
            frame = [background_color] * len(self.coords)
            for i in range(len(self.coords)):
                normalized_rgb = list(colorsys.hsv_to_rgb(
                    mu.normalize(mu.wrap(self.coords[i][1] - current_y, 0, self.bounds.max_y), 0, self.bounds.max_y), 1, 1))
                frame[i] = tuple([int(channel * 255) for channel in normalized_rgb] + [255])
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def gradient(self, steps: int, color_from: Color = Color.white, color_to: Color = Color.white, speed: float = 10, background_color: Color = Color.transparent):
        current_y = 0
        frames = []
        for step in range(steps):
            current_y += speed
            if current_y > self.bounds.max_y:
                current_y = 0
            frame = [background_color] * len(self.coords)
            for i in range(len(self.coords)):
                normalized_rgb = mu.color_lerp((color_from[0], color_from[1], color_from[2], color_from[3]), (color_to[0], color_to[1], color_to[2], color_to[3]), mu.normalize(mu.wrap(self.coords[i][1] - current_y, 0, self.bounds.max_y), 0, self.bounds.max_y))
                frame[i] = normalized_rgb
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def string_up(self, steps: int, color: Color = Color.white, trail_length: int = 25, background_color: Color = Color.transparent):
        current_pixel = -trail_length
        frames = []
        for step in range(steps):
            current_pixel += int((len(self.coords) + 2 * trail_length) / steps)
            frame = [background_color] * len(self.coords)
            for i in range(trail_length):
                pos = current_pixel + i
                if pos < len(self.coords) and pos >= 0:
                    lerp_color = mu.color_lerp(background_color, (color[0], color[1], color[2], color[3]), mu.normalize(i, 0, trail_length))
                    frame[pos] = lerp_color
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def string_down(self, steps: int, color: Color = Color.white, trail_length: int = 25, background_color: Color = Color.transparent):
        current_pixel = len(self.coords) + trail_length
        frames = []
        for step in range(steps):
            current_pixel -= int((len(self.coords) + 2 * trail_length) / steps)
            frame = [background_color] * len(self.coords)
            for i in range(trail_length):
                pos = current_pixel - i
                if pos < len(self.coords) and pos >= 0:
                    lerp_color = mu.color_lerp(background_color, (color[0], color[1], color[2], color[3]), mu.normalize(i, 0, trail_length))
                    frame[pos] = lerp_color
            frames.append(frame)
        return frames

    @l_effect(EffectType.UNIVERSAL)
    def split_vertical(self, steps: int, color_from: Color = Color.white, color_to: Color = Color.white, background_color: Color = Color.transparent):
        mid_x = (self.bounds.min_x + self.bounds.max_x) / 2
        frames = []
        for step in range(steps):
            frame = [background_color] * len(self.coords)
            for i in range(len(self.coords)):
                if self.coords[i][0] < mid_x:
                    frame[i] = (color_from[0], color_from[1], color_from[2], color_from[3])
                else:
                    frame[i] = (color_to[0], color_to[1], color_to[2], color_to[3])
            frames.append(frame)
        return frames