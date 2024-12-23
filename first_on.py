import board
import neopixel

# Define the number of LEDs and the pin connected to the Neopixel strip
num_leds = 200
pin = board.D18

# Create a Neopixel object with the specified number of LEDs and pin
pixels = neopixel.NeoPixel(pin, num_leds, auto_write=False)

# Turn on all LEDs with the specified color
#pixels.fill(color)
pixels[0] = (255, 0, 0)
pixels[50] = (0, 255, 0)
pixels[127] = (0, 0, 255)
pixels.show()
