import time
import board
import neopixel
import colorsys

# LED strip configuration:
LED_COUNT = 200      # Number of LED pixels.
LED_PIN = board.D18  # GPIO pin connected to the LEDs (using board module pin notation).
LED_BRIGHTNESS = 1.0 # Brightness level (0.0 to 1.0).

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
def red_wave(strip, speed):
    current_z = 0  # Initialize position along the Z-axis
    current_dir = 1
    height = max([coord[2] for coord in coords])  # Maximum Z-axis value

    while True:
        current_z += 20 * current_dir
        if current_z > height:
            current_dir = -1
        if current_z < 0:
            current_dir = 1

        for i in range(LED_COUNT):
            # Example: Assign random color to each point
            # new_color[1] -> Z position same as current_z = 0; Z distance from current_z same as height = 125
            new_color = [lerp(0, 127, normalize(clamp(abs(coords[i][2] - current_z), 0, height), 0, height)),
                         0, 0]
            strip[i] = new_color  # Update specific point's color
        # Show the updated strip
        strip.show()
        time.sleep(speed)


# Main program logic.
if __name__ == '__main__':
    try:
        # Set the speed for the color cycle (0.001 is slow, 0.01 is faster).
        speed = 0.05
        red_wave(strip, speed)
    except KeyboardInterrupt:
        # Turn off all LEDs when the program is interrupted.
        strip.fill((0, 0, 0))
        strip.show()
        print("LEDs turned off.")
