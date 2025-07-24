from modules.effect import LightEffect, ParamType, EffectType
import modules.mathutils as mu
import time
import random

class FrameFlame(LightEffect):
    def __init__(self, renderer, coords):
        super().__init__(renderer, coords, "Frame Flame", EffectType.ONLY_2D)
        self.color = self.add_parameter("Color", ParamType.COLOR, "#FF0000")
        self.reach = self.add_parameter("Reach", ParamType.SLIDER, 10, min=1, max=50, step=1) # % of height
        self.particle_percent = self.add_parameter("Particle Percent", ParamType.SLIDER, 50, min=5, max=100, step=1) # % of the remaining leds
        self.fade_time = self.add_parameter("Fade Time", ParamType.SLIDER, 700, min=300, max=1500, step=1) # ms to fade particle out
        self.edges = mu.convex_hull(coords)
        self.frame_length = 1/60
        self.particles = {}

    def update(self):
        now = time.time()
        self.renderer.clear()

        # frame
        abs_reach = self.reach.get() / 100 * self.height
        for idx, coord in enumerate(self.coords):
            dist = mu.distance_to_closest_edge(coord, self.edges)
            if dist < abs_reach:
                ratio = 1
                col = self.color.get()
                self.renderer[idx] = (
                    int(col[0] * ratio),
                    int(col[1] * ratio),
                    int(col[2] * ratio)
                )

        # Update and draw existing particles
        particles_to_remove = []
        for idx, particle in self.particles.items():
            age_ms = (now - particle["spawn_time"]) * 1000
            fade_duration_ms = particle["fade_duration"]
            if age_ms >= fade_duration_ms:
                particles_to_remove.append(idx)
                continue
            
            ratio = 1 - (age_ms / fade_duration_ms)
            col = particle["color"]
            faded_color = (
                int(col[0] * ratio),
                int(col[1] * ratio),
                int(col[2] * ratio)
            )
            # Ensure particle doesn't draw over a brighter frame pixel
            if sum(faded_color) > sum(self.renderer.leds[idx]):
                 self.renderer[idx] = faded_color

        for idx in particles_to_remove:
            del self.particles[idx]

        # Spawn new particles
        leds_not_in_frame = [idx for idx, col in enumerate(self.renderer.leds) if sum(col) == 0]
        
        max_particles = int(self.particle_percent.get() / 100 * len(leds_not_in_frame))
        
        num_to_spawn = max_particles - len(self.particles)

        if num_to_spawn > 0:
            available_leds = []
            weights = []
            # Find LEDs that are not in the frame and not already a particle
            for idx in leds_not_in_frame:
                if idx not in self.particles:
                    available_leds.append(idx)
                    weights.append(1 / (mu.distance_to_closest_edge(self.coords[idx], self.edges)**5 + 1e-6))

            if available_leds:
                # Ensure we don't try to spawn more particles than there are available LEDs
                num_to_spawn = min(num_to_spawn, len(available_leds))
                particle_indices = random.choices(available_leds, weights=weights, k=num_to_spawn)
                
                col = self.color.get()
                base_fade_speed = self.fade_time.get()
                for idx in particle_indices:
                    # Add random variation to fade speed, e.g., +/- 20%
                    fade_duration = base_fade_speed * random.uniform(0.3, 1.7)
                    self.particles[idx] = {"spawn_time": now, "color": col, "fade_duration": fade_duration}
                    # Set initial color for the new particle
                    self.renderer[idx] = col

        self.renderer.show()
        time.sleep(self.frame_length)