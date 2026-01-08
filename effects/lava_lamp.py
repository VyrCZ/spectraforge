from modules.effect import LightEffect, ParamType, EffectType
import modules.mathutils as mu
import math
import colorsys

class LavaLamp(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Lava Lamp", EffectType.UNIVERSAL)
        
        # Parameters
        self.blob_speed = self.add_parameter("Speed", ParamType.SLIDER, 5, min=1, max=50, step=1)
        self.core_color = self.add_parameter("Core Color", ParamType.COLOR, "#FF3200")
        self.bg_color = self.add_parameter("BG Color", ParamType.COLOR, "#0A0014")
        
        self.t = 0
        
        # Pre-calculate normalized coordinates (0.0 to 1.0)
        xs, ys, zs = zip(*coords)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)
        
        width = (max_x - min_x) or 1
        height = (max_y - min_y) or 1
        depth = (max_z - min_z) or 1
        
        self.norm_coords = []
        for x, y, z in coords:
            nx = (x - min_x) / width
            ny = (y - min_y) / height
            nz = (z - min_z) / depth
            self.norm_coords.append((nx, ny, nz))

    def update(self):
        # Update time (speed scale adjusted for framerate)
        self.t += self.blob_speed.get() / 5000.0
        t = self.t

        # Blob centers moving in 0.0-1.0 space
        b1 = (0.5 + 0.4 * math.sin(t), 0.5 + 0.3 * math.cos(t * 1.3), 0.5 + 0.4 * math.sin(t * 0.7))
        b2 = (0.5 + 0.3 * math.sin(t * 1.2 + 2), 0.5 + 0.4 * math.cos(t * 0.9), 0.5 + 0.3 * math.cos(t * 1.5))
        b3 = (0.5 + 0.4 * math.cos(t * 0.8), 0.5 + 0.2 * math.sin(t * 1.1), 0.5 + 0.4 * math.sin(t + 4))

        bg = self.bg_color.get()
        core = self.core_color.get()

        for i, (nx, ny, nz) in enumerate(self.norm_coords):
            # Calculate inverse square distance (Metaballs)
            d1 = 1.0 / (((nx - b1[0])**2 + (ny - b1[1])**2 + (nz - b1[2])**2) + 0.05)
            d2 = 1.0 / (((nx - b2[0])**2 + (ny - b2[1])**2 + (nz - b2[2])**2) + 0.05)
            d3 = 1.0 / (((nx - b3[0])**2 + (ny - b3[1])**2 + (nz - b3[2])**2) + 0.05)
            
            intensity = (d1 + d2 + d3) / 40.0
            t_val = max(0.0, min(1.0, intensity))
            
            # Lerp between background and core color
            # Assuming mu.color_lerp handles standard RGB tuples
            self.renderer[i] = mu.color_lerp(bg, core, t_val)
            
        self.renderer.show()