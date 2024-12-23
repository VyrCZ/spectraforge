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

# Function to convert HSV to RGB tuple.
def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def wrap(value, start, end):
    range_size = end - start
    return ((value - start) % range_size) + start

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

# Function to cycle colors on the strip.
def wave(strip, speed, color):
    falloff = 10  # Number of LEDs to fade out
    current_pos = 0
    strip_length = len(strip)
    
    while True:
        # Wrap the current position to stay within bounds
        current_pos = (current_pos + 1) % strip_length
        
        for i in range(strip_length):
            # Calculate distance with wrapping
            distance = min(abs(i - current_pos), strip_length - abs(i - current_pos))
            
            # Compute brightness based on distance
            brightness = max(0, 1 - distance / falloff)
            
            # Set the pixel color with adjusted brightness
            strip[i] = (
                int(color[0] * brightness),
                int(color[1] * brightness),
                int(color[2] * brightness)
            )
        
        # Show the updated strip
        strip.show()
        time.sleep(speed)

# Main program logic.
if __name__ == '__main__':
    try:
        # Set the speed for the color cycle (0.001 is slow, 0.01 is faster).
        speed = 0.05
        color = (255, 0, 0)
        wave(strip, speed, color)
    except KeyboardInterrupt:
        # Turn off all LEDs when the program is interrupted.
        strip.fill((0, 0, 0))
        strip.show()
        print("LEDs turned off.")
