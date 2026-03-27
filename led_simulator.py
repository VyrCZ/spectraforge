import socket
import pyvista as pv
import numpy as np
import time
import math
from scipy.spatial import distance
import os
import threading
import json
import traceback
import sys

# set working directory to the directory of this file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

HOST = "127.0.0.1"
PORT = 4897

class LedSimulator:
    """
    A LED simulator that connects to the server and visualizes the LEDs, without the need for a hardware setup.
    To start, run this script and the server. The simulator will hook and display data sent to the hardware.
    The server sends the setup coordinates when the client connects and whenever the setup changes.
    """
    def __init__(self):
        self._setup_coords = None
        self._pending_setup = None  # Set by receiver thread when a new setup arrives
        self._initial_setup_event = threading.Event()

        self.colors = []
        self.debug_elements = []
        self.debug_actors = []

        self.sock = self._connect_to_server()  # wait until connected

        self._receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._receiver_thread.start()

        # Wait for the server to send the initial setup before creating the plotter
        print("Waiting for setup data from server...")
        self._initial_setup_event.wait()

        self._setup_coords = self._pending_setup
        self._pending_setup = None
        self.num_points = len(self._setup_coords)
        self.colors = [[0, 0, 0] for _ in self._setup_coords]

        self._init_plotter()

    def _init_plotter(self):
        self.cloud = pv.PolyData(self._setup_coords, force_float=False)
        self.cloud["colors"] = np.array(self.colors, dtype=np.uint8)
        self.plotter = pv.Plotter()
        self.plotter.background_color = "#141414"
        self.plotter.view_xy()
        self.actor = self.plotter.add_points(self.cloud, scalars="colors", rgb=True, point_size=10)
        self.plotter.reset_camera()
        self.plotter.show(interactive_update=True)

    def start(self):
        while True:
            try:
                # Check if the setup changed while running
                if self._pending_setup is not None:
                    new_coords = self._pending_setup
                    self._pending_setup = None
                    self.plotter.close()
                    self._setup_coords = new_coords
                    self.num_points = len(self._setup_coords)
                    self.colors = [[0, 0, 0] for _ in self._setup_coords]
                    self.debug_actors = []
                    self._init_plotter()
                self.update_colors()
                time.sleep(1/60) # 60 fps
            except Exception as e:
                print(f"Error in simulation loop: {traceback.format_exc()}")
                break

    # Function to update colors dynamically
    def update_colors(self):
        # print current zoom
        # if the colors are not in range 0-255, convert them and print a warning
        for i, color in enumerate(self.colors):
            if not all(0 <= c <= 255 for c in color):
                print(f"Color {color} at index {i} is out of range, converting to 0-255")
                self.colors[i] = [max(0, min(255, int(c))) for c in color]
        self.cloud["colors"] = np.array(self.colors, dtype=np.uint8)
        self.plotter.update_scalars(self.cloud["colors"])  # Efficiently update colors
        self.draw_debug_elements(self.debug_elements)
        self.plotter.update()

    def draw_debug_elements(self, elements: dict):
        """
        Draw debug elements on the plotter.
        :param elements: List of debug elements to draw.
        """
        for actor in self.debug_actors:
            self.plotter.remove_actor(actor)
        self.debug_actors.clear()

        if not hasattr(self, "plotter"):
            return  # Plotter is not active yet, so skip drawing
        if not elements:
            return
        for element in elements:
            if element["type"] == "line":
                start = np.array(element["point1"])
                end = np.array(element["point2"])
                color = element.get("color", (255, 0, 0))
                actor = self.plotter.add_lines(np.vstack([start, end]), color=color)
                self.debug_actors.append(actor)
            elif element["type"] == "point":
                point = np.array(element["point"])
                color = element.get("color", (255, 0, 0))
                actor = self.plotter.add_points(point, color=color)
                self.debug_actors.append(actor)
            elif element["type"] == "circle":
                center = np.array(element["center"])
                radius = element["radius"]
                color = element.get("color", (255, 0, 0))
                num_points = 100
                angles = np.linspace(0, 2 * np.pi, num_points)
                circle_points = np.array([[center[0] + radius * np.cos(angle), center[1] + radius * np.sin(angle), center[2]] for angle in angles])
                actor = self.plotter.add_lines(np.vstack([circle_points, circle_points[0]]), color=color)
                self.debug_actors.append(actor)

    def _connect_to_server(self):
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((HOST, PORT))
                print(f"Connected to server at {HOST}:{PORT}")
                return sock
            except ConnectionRefusedError as e:
                print(f"Failed: {e}")
                time.sleep(1)
                
    def _receive_loop(self):
        buffer = ""
        decoder = json.JSONDecoder()
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                buffer += data.decode("utf-8")
                
                while buffer:
                    try:
                        received, idx = decoder.raw_decode(buffer)
                        # If the message contains a setup, store it for the main thread to apply
                        if "setup" in received:
                            self._pending_setup = received["setup"]
                            self._initial_setup_event.set()
                        # Extract LED colors from the received data
                        self.colors = received.get("leds", self.colors)  # Use .get() to provide a default value in case "leds" key is missing
                        self.debug_elements = received.get("debug_elements", [])
                        buffer = buffer[idx:].lstrip()
                    except json.JSONDecodeError:
                        # Incomplete JSON object, wait for more data
                        break
            except ConnectionResetError:
                print("Connection closed by server.")
                break
            except Exception as e:
                print(f"Error in receive loop: {traceback.format_exc()}")
                break
            
if __name__ == "__main__":
    sim = LedSimulator()
    sim.start()
