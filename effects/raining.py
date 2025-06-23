from effects.base_effect import LightEffect, ParamType
import math
import random

class RainEffect(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.color = self.add_parameter("Droplet Color", ParamType.COLOR, "#0000FF")
        self.speed = self.add_parameter("Speed", ParamType.SLIDER, 5, min=1, max=10, step=1)  # Fall speed
        self.amount = self.add_parameter("Amount", ParamType.SLIDER, 5, min=1, max=20, step=1)  # Droplet count
        self.threshold = self.add_parameter("Z Threshold", ParamType.SLIDER, 20, min=5, max=50, step=1)
        
        # Precompute top LEDs (highest 20 by Z coordinate)
        self.top_leds = self._get_top_leds()
        self.droplets = []  # List to track active droplets as (led_index, frame_count)

    def _get_top_leds(self):
        return sorted(range(len(self.coords)), key=lambda i: self.coords[i][2], reverse=True)[:20]

    def _find_next_led(self, current_idx, z_threshold):
        current_coord = self.coords[current_idx]
        closest_led = None
        min_dist = float('inf')

        for i, coord in enumerate(self.coords):
            if coord[2] < current_coord[2] - z_threshold:  # Z difference must meet threshold
                xy_dist = math.sqrt((coord[0] - current_coord[0])**2 + (coord[1] - current_coord[1])**2)
                z_diff = current_coord[2] - coord[2]
                cone_radius = z_diff / 5  # Defines the conical search shape

                if xy_dist <= cone_radius and xy_dist < min_dist:
                    min_dist = xy_dist
                    closest_led = i

        return closest_led

    def update(self):
        color = self.color.get()
        speed = int(self.speed.get())
        amount = int(self.amount.get())
        z_threshold = int(self.threshold.get())

        new_pixels = [(0, 0, 0)] * len(self.pixels)

        # Update existing droplets
        updated_droplets = []
        for led_idx, frame_count in self.droplets:
            if frame_count >= speed:
                next_led = self._find_next_led(led_idx, z_threshold)
                if next_led is not None:
                    updated_droplets.append((next_led, 0))  # Move droplet down
                    new_pixels[next_led] = color
            else:
                updated_droplets.append((led_idx, frame_count + 1))
                new_pixels[led_idx] = color

        # Add new droplets
        for _ in range(amount):
            new_droplet = random.choice(self.top_leds)
            updated_droplets.append((new_droplet, 0))
            new_pixels[new_droplet] = color

        # Update droplet list and pixels
        self.droplets = updated_droplets
        self.pixels[:] = new_pixels
        self.pixels.show()
