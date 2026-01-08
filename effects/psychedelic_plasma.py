from modules.effect import LightEffect, ParamType, EffectType
import math
import colorsys

class PsychedelicPlasma(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Psychedelic Plasma", EffectType.UNIVERSAL)
        
        self.speed_param = self.add_parameter("Speed", ParamType.SLIDER, 10, min=1, max=100, step=1)
        self.scale_param = self.add_parameter("Scale", ParamType.SLIDER, 3.0, min=0.1, max=10.0, step=0.1)
        self.brightness_param = self.add_parameter("Brightness", ParamType.SLIDER, 1.0, min=0.0, max=1.0, step=0.05)
        
        self.t = 0
        
        # Normalize Coords
        xs, ys, zs = zip(*coords)
        min_x, width = min(xs), (max(xs) - min(xs)) or 1
        min_y, height = min(ys), (max(ys) - min(ys)) or 1
        min_z, depth = min(zs), (max(zs) - min(zs)) or 1
        
        self.norm_coords = []
        for x, y, z in coords:
            self.norm_coords.append(((x-min_x)/width, (y-min_y)/height, (z-min_z)/depth))

    def update(self):
        self.t += self.speed_param.get() / 2000.0
        t = self.t
        scale = self.scale_param.get()
        bri = self.brightness_param.get()

        for i, (nx, ny, nz) in enumerate(self.norm_coords):
            # 3D Noise formula using sine wave interference
            v = math.sin(scale * nx + t)
            v += math.sin(scale * ny + t)
            v += math.sin(scale * nz + t)
            v += math.sin(scale * (nx + ny + nz) + t)
            
            # Map value to hue
            hue = ((v / 4.0) + 0.5 + (t * 0.05)) % 1.0
            
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, bri)
            self.renderer[i] = (int(r * 255), int(g * 255), int(b * 255))
            
        self.renderer.show()