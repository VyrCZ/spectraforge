import time
import board
import neopixel

# LED strip configuration:
LED_COUNT = 200      # Number of LED pixels.
LED_PIN = board.D18  # GPIO pin connected to the LEDs (using board module pin notation).
LED_BRIGHTNESS = 1.0 # Brightness level (0.0 to 1.0).

# Create a NeoPixel object.
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

import random

# Create an empty LED array
led_array = []

# Generate random colors for each LED
for _ in range(1000):
    row = []
    for _ in range(LED_COUNT):
        color = (255, 0, 0) if random.randint(0, 1) == 0 else (0, 0, 0)
        row.append(color)
    led_array.append(row)
current_index = 0
while True:
    current_colors = led_array[current_index]
    for i in range(LED_COUNT):
        strip[i] = current_colors[i]
    strip.show()
    current_index += 1
    if current_index >= 1000:
        current_index = 0
    time.sleep(0.01)

