from effects.base_effect import LightEffect
import time

class Lightshow(LightEffect):
    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.queue = []  # Holds actions to be executed
        self.start_time = None  # Records the start time of the light show
        self.running_countdown = True
        self.countdown = 3

        # Add actions to the queue
        #self.add_action(0.0, self.swipe, "right", (255, 0, 0), 2)  # Swipe right in 2 seconds
        self.add_action(1, self.fade_all, (0, 0, 255), 0.5)
        self.add_action(2, self.fade_all, (0, 0, 255), 0.5)
        self.add_action(3, self.fade_all, (0, 0, 255), 0.5)

    def add_action(self, start_time, action, *args, **kwargs):
        """
        Schedule an action to be executed.

        :param start_time: Time (in seconds) relative to the start of the light show
        :param action: Function to execute
        :param args: Positional arguments for the action
        :param kwargs: Keyword arguments for the action
        """
        self.queue.append((start_time, action, args, kwargs))
        self.queue.sort(key=lambda a: a[0])  # Ensure actions are sorted by start_time

    def swipe(self, pixels, coords, direction, color, duration):
        """
        Swipe effect: Lights up LEDs in sequence from left to right or right to left.
        """
        num_pixels = len(pixels)
        step_duration = duration / num_pixels
        for i in range(num_pixels):
            if direction == "right":
                pixels[i] = color
            elif direction == "left":
                pixels[num_pixels - i - 1] = color
            pixels.show()
            time.sleep(step_duration)

    def fade_all(self, pixels, coords, color, duration):
        """
        Fade all effect: Gradually changes all LEDs to the specified color.
        """
        steps = 50
        r_step = color[0] / steps
        g_step = color[1] / steps
        b_step = color[2] / steps
        for i in range(steps):
            fade_color = (
                int(color[0] - i * r_step),
                int(color[1] - i * g_step),
                int(color[2] - i * b_step),
            )
            pixels.fill(fade_color)
            pixels.show()
            time.sleep(duration / steps)
        pixels.fill(color)
        pixels.show()

    def update(self):
        """
        Main loop: Executes actions at the correct time.
        """
        # countdown
        if self.running_countdown:
            while self.countdown > 0:
                self.countdown -= 1
                self.pixels.fill(int(255 * self.countdown / 3)), (int(255 * self.countdown / 3)), (int(255 * self.countdown / 3))
                self.pixels.show()
                time.sleep(1)
            self.running_countdown = False
            self.pixels.fill((0, 0, 0))
            self.pixels.show()
            self.start_time = time.time()

        current_time = time.time() - self.start_time  # Calculate elapsed time
        while self.queue and current_time >= self.queue[0][0]:
            _, action, args, kwargs = self.queue.pop(0)  # Get the next action
            action(self.pixels, self.coords, *args, **kwargs)  # Execute the action
