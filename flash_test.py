import time
import board
import neopixel
import colorsys
import random

# LED strip configuration:
LED_COUNT = 200      # Number of LED pixels.
LED_PIN = board.D18  # GPIO pin connected to the LEDs (using board module pin notation).
LED_BRIGHTNESS = 1 # Brightness level (0.0 to 1.0).

# Create a NeoPixel object.
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

coords = []
with open('coordinates.txt', 'r') as f:
    for coord in f.readlines():
        coords.append([float(value) for value in coord.strip().split(',')])  # Convert to float

# Function to convert HSV to RGB tuple.
def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def wrap(value, start, end):
    range_size = end - start
    return ((value - start) % range_size) + start

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def normalize(value, old_min, old_max):
    if old_min == old_max:
        raise ValueError("old_min and old_max cannot be the same.")
    return (value - old_min) / (old_max - old_min)

def lerp(start, end, t):
    return (1 - t) * start + t * end

# Function to cycle colors on the strip.
def flash_test(strip, speed):
    offset = True
    colors = [
        (255, 0, 0),
        (0, 255, 0)
    ]
    while True:
        offset = not offset
        for i in range(LED_COUNT):
            strip[i] = colors[i % 2 == offset]
        # Show the updated strip
        strip.show()
        time.sleep(speed)


# Main program logic.
if __name__ == '__main__':
    try:
        # Set the speed for the color cycle (0.001 is slow, 0.01 is faster).
        speed = 0.05
        flash_test(strip, speed)
    except KeyboardInterrupt:
        # Turn off all LEDs when the program is interrupted.
        strip.fill((0, 0, 0))
        strip.show()
        print("LEDs turned off.")
