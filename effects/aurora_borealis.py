from modules.effect import LightEffect, ParamType, EffectType
import math
import colorsys

class AuroraBorealis(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Aurora Borealis", EffectType.UNIVERSAL)
        
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 5, min=1, max=50, step=1)
        self.density = self.add_parameter("Wave Density", ParamType.SLIDER, 2.0, min=0.5, max=10.0, step=0.5)
        
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
        self.t += self.speed.get() / 5000.0
        t = self.t
        dens = self.density.get()

        for i, (nx, ny, nz) in enumerate(self.norm_coords):
            # Curtain shape
            curve_x = math.sin(nz * dens + t) * 0.3 + 0.5
            dist = abs(nx - curve_x)
            
            # Intensity
            intensity = max(0, 1.0 - (dist * 4.0))
            vertical_fade = math.sin(ny * math.pi)
            final_brightness = intensity * vertical_fade
            
            if final_brightness <= 0.05:
                self.renderer[i] = (0, 0, 0)
                continue

            # Color: Teal/Green to Purple
            hue = 0.45 + (ny * 0.3)
            val = final_brightness * (0.8 + 0.2 * math.sin(t * 3 + nx * 5))
            
            r, g, b = colorsys.hsv_to_rgb(hue, 0.9, val)
            self.renderer[i] = (int(r * 255), int(g * 255), int(b * 255))
            
        self.renderer.show()