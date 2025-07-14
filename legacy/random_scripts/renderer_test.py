from modules.led_renderer import LEDRenderer

renderer = LEDRenderer(30)  # Example with 30 LEDs
renderer.leds[0] = (255, 0, 0)  # Set the first LED to red