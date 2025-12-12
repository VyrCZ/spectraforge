from modules.engine import Engine
from modules.engine_manager import EngineManager
from modules.log_manager import Log
import modules.mathutils as mu

from typing import Tuple, List, Optional
from PIL import Image
import cv2
import threading
import time

class VideoEngine(Engine):
    """
    A self-driving video engine.
    It spawns its own background thread to process video frames, 
    so it works even if the main thread is blocked by a Server.
    """

    def __init__(self, renderer, setup):
        Log.info("EngineVideo", "EngineVideo initialized.")
        self.renderer = renderer
        
        # Threading & Playback State
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.video_cap = None
        
        # Config (Updated default)
        self.current_mode = "fill"  # Renamed from "cover"
        self.current_radius = 1
        self.target_fps = 30.0
        
        self.on_setup_changed(setup)

    def on_setup_changed(self, setup):
        Log.debug("EngineVideo", f"Setup changed to {setup.name}")
        self.setup = setup
        self.coords = setup.coords
        self.bounds = mu.Bounds(setup.coords)

    def on_enable(self):
        Log.info("EngineVideo", "EngineVideo enabled.")

    def on_disable(self):
        Log.info("EngineVideo", "EngineVideo disabled. Stopping playback.")
        self._stop_playback()

    # --- INTERNAL HELPERS ---

    def _stop_playback(self):
        """
        Stops the background thread and releases video resources.
        This is a blocking call to ensure clean shutdown.
        """
        # 1. Signal thread to stop
        if self._playback_thread and self._playback_thread.is_alive():
            Log.debug("EngineVideo", "Stopping background video thread...")
            self._stop_event.set()
            self._playback_thread.join(timeout=2.0)
            if self._playback_thread.is_alive():
                 Log.warn("EngineVideo", "Thread did not stop gracefully!")
            else:
                 Log.debug("EngineVideo", "Thread stopped.")
        
        self._playback_thread = None
        
        # 2. Release OpenCV
        if self.video_cap:
            self.video_cap.release()
            self.video_cap = None

    def _map_image_internal(self, img, mode, radius):
        """Internal mapping logic (same as before)."""
        if not self.coords: return

        img_w, img_h = img.size
        pixels = img.load()

        x_min, x_max = self.bounds.min_x, self.bounds.max_x
        y_min, y_max = self.bounds.min_y, self.bounds.max_y
        
        led_width = max(1.0, x_max - x_min)
        led_height = max(1.0, y_max - y_min)
        
        led_center_x = (x_min + x_max) / 2.0
        led_center_y = (y_min + y_max) / 2.0
        img_center_x, img_center_y = img_w / 2.0, img_h / 2.0

        scale_w = img_w / led_width
        scale_h = img_h / led_height
        
        # Updated Logic Check: Use 'fill' and 'fit'
        if mode == "fill":
            scale = min(scale_w, scale_h) # Fill/Cover strategy
        elif mode == "fit":
            scale = max(scale_w, scale_h) # Fit/Contain strategy
        else:
             raise ValueError("mode must be 'fill' or 'fit'")

        leds = self.renderer.leds
        count = min(len(leds), len(self.coords))

        for i in range(count):
            coord = self.coords[i]
            u = int(img_center_x + ((coord[0] - led_center_x) * scale))
            v = int(img_center_y + (-(coord[1] - led_center_y) * scale)) # Flip Y
            u = max(0, min(u, img_w - 1))
            v = max(0, min(v, img_h - 1))

            if radius <= 0:
                leds[i] = pixels[u, v]
            else:
                r, g, b, c = 0, 0, 0, 0
                for pu in range(max(0, u - radius), min(img_w, u + radius + 1)):
                    for pv in range(max(0, v - radius), min(img_h, v + radius + 1)):
                        pr, pg, pb = pixels[pu, pv]
                        r += pr; g += pg; b += pb; c += 1
                if c > 0: leds[i] = (r//c, g//c, b//c)

    def _video_loop(self):
        """The main loop that runs in the background thread."""
        Log.info("EngineVideo", "Video thread started.")
        
        frame_interval = 1.0 / self.target_fps
        
        while not self._stop_event.is_set():
            start_time = time.time()
            
            if self.video_cap and self.video_cap.isOpened():
                ret, frame = self.video_cap.read()
                
                if not ret:
                    # Loop video
                    self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                # Process Frame
                try:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(frame_rgb)
                    self._map_image_internal(pil_img, self.current_mode, self.current_radius)
                    
                    # PUSH TO HARDWARE
                    self.renderer.show()
                except Exception as e:
                    Log.error("EngineVideo", f"Error processing frame: {e}")
            
            # FPS Control
            elapsed = time.time() - start_time
            sleep_time = max(0.0, frame_interval - elapsed)
            time.sleep(sleep_time)

        Log.info("EngineVideo", "Video thread exiting.")

    # --- PUBLIC API ---

    @EngineManager.requires_active
    def display_img(self, path: str, mode: str = "fill", sample_radius: int = 1):
        """Stops any video and displays a static image."""
        self._stop_playback() # Ensure no video thread fights us
        
        try:
            img = Image.open(path).convert("RGB")
            self._map_image_internal(img, mode, sample_radius)
            self.renderer.show()
            Log.info("EngineVideo", f"Static image displayed: {path} (mode={mode})")
        except Exception as e:
            Log.error("EngineVideo", f"Failed to load image: {e}")

    @EngineManager.requires_active
    def display_video(self, path: str, mode: str = "fill", sample_radius: int = 1):
        """Stops any current media and starts the video thread."""
        # 1. Clean up old thread/video
        self._stop_playback()
        
        # 2. Setup new video
        Log.info("EngineVideo", f"Opening video: {path}")
        self.video_cap = cv2.VideoCapture(path)
        if not self.video_cap.isOpened():
            Log.error("EngineVideo", f"Failed to open video: {path}")
            return

        # 3. Configure State (uses new default 'fill')
        self.current_mode = mode
        self.current_radius = sample_radius
        self.target_fps = self.video_cap.get(cv2.CAP_PROP_FPS) or 30.0
        
        # Cap FPS for RPi performance (optional, remove if you want full speed)
        if self.target_fps > 30: 
            self.target_fps = 30.0

        # 4. Launch Thread
        self._stop_event.clear()
        self._playback_thread = threading.Thread(target=self._video_loop, daemon=True)
        self._playback_thread.start()