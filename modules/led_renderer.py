import os
import socket
import json
import threading
from modules.setup import Setup
from modules.log_manager import Log

class DummyNeoPixel():
    """
    A replacement for the NeoPixel class when running on Windows or for debugging purposes.
    This class simulates the behavior of NeoPixel without actual hardware interaction.
    """
    def __init__(self, pin, num_leds, auto_write):
        self.num_leds = num_leds
        self.pixels = [(0, 0, 0)] * num_leds
        self.auto_write = auto_write

    def show(self):
        pass

class LEDRenderer:
    def __init__(self, setup: Setup):
        led_count = len(setup.coords)
        self.led_count = led_count
        self.leds = [(0, 0, 0)] * led_count
        Log.info("LEDRenderer", f"Initializing LEDRenderer with {led_count} LEDs.")

        # Setup a led simulator server if running on Windows
        if os.name == 'nt':
            self._clients = []
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            HOST = "127.0.0.1"
            PORT = 4897
            try:
                self._server_socket.bind((HOST, PORT))
                self._server_socket.listen()
                Log.info("LEDRenderer", f"Server listening on {HOST}:{PORT}")
                
                accept_thread = threading.Thread(target=self._accept_connections)
                accept_thread.daemon = True
                accept_thread.start()
            except Exception as e:
                Log.error("LEDRenderer", f"Failed to start server on {HOST}:{PORT}. {e}")
                self._server_socket = None
        else:
            from neopixel import NeoPixel
            import board
            # LED Configuration
            PIN = board.D18
            self._pixels = NeoPixel(PIN, self.led_count, auto_write=False)

    def _accept_connections(self):
        while True:
            try:
                client_socket, addr = self._server_socket.accept()
                Log.info("LEDRenderer", f"New connection from {addr}")
                self._clients.append(client_socket)
            except Exception as e:
                Log.error("LEDRenderer", f"Error accepting connections: {e}")
                break

    # add dictionary-like access to the self.leds for the code i already wrote with pixels in mind
    def __getitem__(self, index):
        return self.leds[index]
    
    def __setitem__(self, index, value):
        if isinstance(value, tuple) and len(value) == 3:
            self.leds[index] = value
        elif isinstance(value, list) and len(value) == 3:
            self.leds[index] = tuple(value)
        else:
            raise ValueError("Value must be a tuple of (R, G, B)")
        
    def __len__(self):
        return self.led_count

    def fill(self, color: tuple[int, int, int]):
        for i in range(self.led_count):
            self.leds[i] = color

    def clear(self):
        self.fill((0, 0, 0))

    def show(self):
        if os.name == 'nt':
            if self._clients:
            # Send the current LED colors to all connected clients
                message = json.dumps(self.leds).encode('utf-8')
                disconnected_clients = []
                for client in self._clients:
                    try:
                        client.sendall(message)
                    except Exception:
                        disconnected_clients.append(client)
                
                for client in disconnected_clients:
                    Log.info("LEDRenderer", f"Client {client.getpeername()} disconnected.")
                    self._clients.remove(client)
        else:
        # Update the hardware display
            for i in range(self.led_count):
                self._pixels[i] = self.leds[i]
            self._pixels.show()