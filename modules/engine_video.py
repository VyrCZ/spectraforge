from modules.engine import AudioEngine
from modules.engine_manager import EngineManager
from modules.log_manager import Log
import modules.mathutils as mu
import modules.display_utils as du

from typing import Optional, Any
from PIL import Image
import os
import imageio

class VideoEngine(AudioEngine):
    """
    VideoEngine using ImageIO for lightweight video decoding on Raspberry Pi.
    """

    VIDEO_DIR = "media/videos/"
    VIDEO_AUDIO_DIR = "media/videos/audio/"

    def __init__(self, renderer, setup, ready_callback):
        Log.info("VideoEngine", "Initializing VideoEngine (ImageIO).")
        super().__init__(renderer, ready_callback)
        
        self.reader: Optional[Any] = None
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

    @EngineManager.requires_active
    def on_audio_load(self, video_filename: str) -> None:
        Log.info("VideoEngine", f"Loading video context: {video_filename}")
        
        try:
            video_path = os.path.join(self.VIDEO_DIR, video_filename)
            audio_filename = video_filename + ".mp3"
            
            if not os.path.exists(video_path):
                Log.error("VideoEngine", f"Video file not found: {video_path}")
                return

            # --- ImageIO Setup ---
            if self.reader:
                self.reader.close()
            
            self.reader = imageio.get_reader(video_path, 'ffmpeg')
            meta = self.reader.get_meta_data()
            
            # --- Robust Metadata Extraction ---
            self.video_fps = float(meta.get('fps', 30.0))
            
            # Safe retrieval of frame count
            raw_nframes = meta.get('nframes', 0)
            
            # Handle 'inf' or missing frames
            if raw_nframes and raw_nframes != float('inf'):
                self.total_frames = int(raw_nframes)
            else:
                # Fallback: Calculate from duration if frames are missing/infinite
                duration = meta.get('duration', 0)
                if duration and duration != float('inf'):
                    self.total_frames = int(duration * self.video_fps)
                else:
                    self.total_frames = 0 # Mark as unknown

            self.FPS = max(1, int(round(self.video_fps)))
            
            if self.total_frames > 0:
                self.audio_length = self.total_frames / self.video_fps
            else:
                # If we still don't know the length, treat it as endless
                self.audio_length = float("inf") 

            Log.info("VideoEngine", f"Video loaded. FPS: {self.video_fps}, Frames: {self.total_frames}")

            if self.ready_callback:
                self.ready_callback(audio_filename)
                
        except Exception as e:
            Log.error("VideoEngine", f"Load error: {e}")

    @EngineManager.requires_active
    def on_frame(self, current_time: float) -> None:
        if not self.reader:
            return

        target_frame_index = int(current_time * self.video_fps)

        if target_frame_index >= self.total_frames and self.total_frames > 0:
            target_frame_index = self.total_frames - 1

        try:
            # get_data(index) seeks and retrieves the frame
            # ImageIO returns RGB by default, so we skip color conversion!
            frame_rgb = self.reader.get_data(target_frame_index)
            
            pil_img = Image.fromarray(frame_rgb)

            du.map_image_to_leds(
                pil_img, 
                self.renderer, 
                self.coords, 
                self.bounds, 
                self.current_mode, 
                self.current_radius
            )
            self.renderer.show()
                
        except IndexError:
            # End of video
            pass
        except Exception as e:
            Log.error("VideoEngine", f"Frame error: {e}")

    def on_audio_stop(self) -> None:
        if self.reader:
            self.reader.close()
            self.reader = None
        self.renderer.clear()
        self.renderer.show()

    def on_disable(self) -> None:
        self.on_audio_stop()
        super().on_disable()

    def set_display_config(self, mode="fill", radius=1):
        self.current_mode = mode
        self.current_radius = radius