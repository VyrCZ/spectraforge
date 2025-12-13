from modules.engine import AudioEngine
from modules.engine_manager import EngineManager
from modules.log_manager import Log
import modules.mathutils as mu
import modules.display_utils as du

from typing import Optional
from PIL import Image
import cv2
import os

class VideoEngine(AudioEngine):
    """
    VideoEngine inherits from AudioEngine.
    It plays video frames synchronized to the audio clock provided by the base class.
    """

    VIDEO_DIR = "media/videos/"
    VIDEO_AUDIO_DIR = "media/videos/audio/"

    def __init__(self, renderer, setup, ready_callback):
        Log.info("EngineVideo", "Initializing EngineVideo.")
        super().__init__(renderer, ready_callback)
        
        Log.info("VideoEngine", "VideoEngine initialized.")
        self.video_cap: Optional[cv2.VideoCapture] = None
        
        # Display settings
        self.current_mode = "fill"
        self.current_radius = 1
        self.video_fps = 30.0
        self.total_frames = 0
        
        self.on_setup_changed(setup)

    def on_enable(self):
        Log.info("VideoEngine", "Enabled.")

    def on_setup_changed(self, setup):
        self.setup = setup
        self.coords = setup.coords
        self.bounds = mu.Bounds(setup.coords)

    # --- AudioEngine Lifecycle Overrides ---

    @EngineManager.requires_active
    def on_audio_load(self, video_filename: str) -> None:
        """
        1. Infers video path from audio path.
        2. Loads OpenCV capture.
        3. Signals ready.
        """
        Log.info("VideoEngine", f"Loading video context: {video_filename}")
        
        # 1. Resolve Video Path
        # Structure: media/videos/video.mp4 AND media/videos/audio/video.mp4.mp3
        try:
            video_path = os.path.join(self.VIDEO_DIR, video_filename)  # .../media/videos
            
            audio_filename = video_filename + ".mp3" # video.mp4.mp3
            # Remove the last .mp3 extension to get video filename
            audio_path = os.path.join(self.VIDEO_AUDIO_DIR, audio_filename)
        
        except Exception as e:
            Log.error("VideoEngine", f"Path parsing error: {e}")
            return

        if not os.path.exists(video_path):
            Log.error("VideoEngine", f"Video file not found at calculated path: {video_path}")
            return

        # 2. Initialize Video Capture
        if self.video_cap:
            self.video_cap.release()
            
        self.video_cap = cv2.VideoCapture(video_path)
        
        if not self.video_cap.isOpened():
            Log.error("VideoEngine", f"Failed to open video: {video_path}")
            return

        # Read video properties
        self.video_fps = float(self.video_cap.get(cv2.CAP_PROP_FPS) or 30.0)
        if self.video_fps <= 0:
            self.video_fps = 30.0

        self.total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

        # drive the AudioEngine runner at video fps
        self.FPS = max(1, int(round(self.video_fps)))

        # IMPORTANT: this is why on_frame wasn't firing
        if self.total_frames > 0:
            self.audio_length = self.total_frames / self.video_fps
        else:
            self.audio_length = float("inf")
            Log.warn("VideoEngine", "Frame count unknown; will run until stopped.")

        self.current_time = 0.0

        Log.info("VideoEngine", f"Video loaded. FPS: {self.video_fps}, Frames: {self.total_frames}")

        # 3. Signal AudioEngine that we are ready to play
        if self.ready_callback:
            self.ready_callback(audio_filename)

    @EngineManager.requires_active
    def on_frame(self, current_time: float) -> None:
        """
        Called by AudioEngine loop. Syncs video to current_time.
        """
        if not self.video_cap or not self.video_cap.isOpened():
            Log.error("VideoEngine", "Video capture not initialized.")
            return
        
        #Log.info("VideoEngine", f"Rendering frame at time: {current_time:.2f}s")

        # Calculate target frame based on audio time
        target_frame_index = int(current_time * self.video_fps)

        # Safety clamp
        if target_frame_index >= self.total_frames:
            target_frame_index = self.total_frames - 1

        # Optimization: Only seek if we drifted significantly.
        # Otherwise just read() next frame which is faster.
        # However, for AudioEngine sync, explicit set is safer for seeking/looping support.
        # We try to set position strictly to ensure audio/video sync.
        
        try:
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame_index)
            ret, frame = self.video_cap.read()

            if ret:
                # Convert BGR (OpenCV) to RGB (PIL)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)

                # Use the shared utility to map to LEDs
                du.map_image_to_leds(
                    pil_img, 
                    self.renderer, 
                    self.coords, 
                    self.bounds, 
                    self.current_mode, 
                    self.current_radius
                )
                self.renderer.show()
            else:
                # Handle end of video stream if audio is longer than video
                pass
                
        except Exception as e:
            Log.error("VideoEngine", f"Frame error: {e}")

    def on_audio_stop(self) -> None:
        """Called when playback stops completely."""
        if self.video_cap:
            self.video_cap.release()
            self.video_cap = None
        self.renderer.clear()
        self.renderer.show()

    def on_disable(self) -> None:
        """Engine disabled."""
        self.on_audio_stop()
        super().on_disable()

    # --- Configuration API ---

    def set_display_config(self, mode="fill", radius=1):
        """Allows configuring display style before or during playback."""
        self.current_mode = mode
        self.current_radius = radius