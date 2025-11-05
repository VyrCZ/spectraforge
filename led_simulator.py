import socket
import pyvista as pv
import numpy as np
import time
import math
from scipy.spatial import distance
import os
from modules.setup import Setup
import threading
import json
import traceback
from modules.config_manager import Config
import sys

# set working directory to the directory of this file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

HOST = "127.0.0.1"
PORT = 4897

class LedSimulator:
    """
    A LED simulator that connects to the server and visualizes the LEDs, without the need for a hardware setup.
    To start, run this script and the server. The simulator will hook and display data sent to the hardware.
    """
    def __init__(self):
        Config().load() # this config doesn't change when the instance running in server.py does, reload here
        self.current_setup_name = Config().config["current_setup"]
        self.setup_path = "config/setups/" + self.current_setup_name + ".json"
        self.current_setup = Setup.from_json(self.current_setup_name, json.load(open(self.setup_path)))
        self.last_conf_change = os.path.getmtime(Config.CONFIG_PATH)
        self.coords = self.current_setup.coords
        self.num_points = len(self.coords)

        # Initialize colors as white (RGB: [255, 255, 255])
        self.colors = [[0, 0, 0] for _ in self.coords]
        self.debug_elements = []
        self.debug_actors = []
        self.sock = self._connect_to_server()  # wait until connected
        
        self._receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._receiver_thread.start()
        
        # Create plotter and point cloud after connection succeeded
        self.cloud = pv.PolyData(self.coords, force_float=False)
        self.cloud["colors"] = np.array(self.colors, dtype=np.uint8)
        self.plotter = pv.Plotter()
        self.plotter.background_color = "#050505"
        #self.plotter.background_color = "#FFFFFF"
        self.plotter.view_xy()
        #self.plotter.add_axes(interactive=False)
        #self.actor = self.plotter.add_points(self.cloud, scalars="colors", rgb=True, point_size=10, style="points_gaussian", emissive=True, render_points_as_spheres=True)
        self.actor = self.plotter.add_points(self.cloud, scalars="colors", rgb=True, point_size=10)
        self.plotter.reset_camera()
        self.plotter.show(interactive_update=True)

    def check_setup(self):
        """
        A function that checks if the setup has changed.
        """
        mod_time = os.path.getmtime(Config.CONFIG_PATH)
        if(mod_time != self.last_conf_change):
            Config().load()
            setup_name = Config().config["current_setup"]
            print(f"{setup_name} | {self.current_setup_name}")
            sys.stdout.flush()
            if(setup_name != self.current_setup_name):
                self.plotter.close()
                self.__init__()

    #def close_plot(self):
        

    def start(self):
        while True:
            try:
                self.check_setup()
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
