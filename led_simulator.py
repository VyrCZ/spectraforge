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

# set working directory to the directory of this file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

HOST = "127.0.0.1"
PORT = 4897

class LedSimulator:
    def __init__(self):
        current_setup = "the_wall.json"
        setup_path = os.path.join("config/setups", current_setup)
        self.current_setup = Setup.from_json("the_wall", json.load(open(setup_path)))
        self.coords = self.current_setup.coords
        self.num_points = len(self.coords)

        # Initialize colors as white (RGB: [255, 255, 255])
        self.colors = [[0, 0, 0] for _ in self.coords]
        self.sock = self._connect_to_server()  # wait until connected
        
        self._receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._receiver_thread.start()
        
        # Create plotter and point cloud after connection succeeded
        self.cloud = pv.PolyData(self.coords, force_float=False)
        self.cloud['colors'] = np.array(self.colors, dtype=np.uint8)
        self.plotter = pv.Plotter()
        self.plotter.background_color = "#050505"
        self.plotter.view_xy()
        self.actor = self.plotter.add_points(self.cloud, scalars='colors', rgb=True)
        self.plotter.reset_camera()
        self.plotter.show(interactive_update=True)

    def start(self):
        while True:
            try:
                self.update_colors()
                time.sleep(1/60) # 60 fps
            except Exception as e:
                print(f"Error in simulation loop: {traceback.format_exc()}")
                break

    # Function to update colors dynamically
    def update_colors(self):
        # print current zoom
        self.cloud['colors'] = np.array(self.colors, dtype=np.uint8)
        self.plotter.update_scalars(self.cloud['colors'])  # Efficiently update colors
        self.plotter.update()

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
                buffer += data.decode('utf-8')
                
                while buffer:
                    try:
                        received, idx = decoder.raw_decode(buffer)
                        self.colors = received
                        buffer = buffer[idx:].lstrip()
                    except json.JSONDecodeError:
                        # Incomplete JSON object, wait for more data
                        break
            except ConnectionResetError:
                print("Connection closed by server.")
                break
            except Exception as e:
                print(f"Error in receive loop: {e}")
                break
            
if __name__ == "__main__":
    sim = LedSimulator()
    sim.start()
