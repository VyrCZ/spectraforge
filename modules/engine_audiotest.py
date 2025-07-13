from modules.engine import AudioEngine
from modules.engine_manager import EngineManager
from modules.log_manager import Log
from pydub import AudioSegment
import os
import math

class AudioTestEngine(AudioEngine):
    """
    Let's see if this works
    """

    def __init__(self, renderer, ready_callback):
        Log.info("EngineAudioTest", "Initializing EngineAudioTest.")
        super().__init__(renderer, ready_callback)
        self.GAMMA = 10
        self.SMOOTH_FACTOR = 0.6

    def on_enable(self):
        Log.info("EngineAudioTest", "EngineAudioTest enabled.")

    def on_disable(self):
        Log.info("EngineAudioTest", "EngineAudioTest disabled.")
        super().on_disable()

    @EngineManager.requires_active
    def on_audio_load(self, audio_file: str):
        Log.info("EngineAudioTest", f"Loading audio file: {audio_file}")
        self.intensities = []
        try:
            audio = AudioSegment.from_mp3(os.path.join("audio", audio_file))

            if audio.channels > 1:
                Log.debug("EngineAudioTest", "Audio is not mono, converting to mono.")
                audio = audio.set_channels(1)

            framerate = audio.frame_rate
            self.audio_length = len(audio) / 1000.0
            Log.info("EngineAudioTest", f"Audio length: {self.audio_length} seconds.")

            samples = audio.get_array_of_samples()
            Log.debug("EngineAudioTest", f"Extracted {len(samples)} samples from audio file.")

            chunk_size = int(framerate / self.FPS)
            if chunk_size == 0:
                Log.error("EngineAudioTest", "FPS is too high for this audio's framerate.")
                return

            raw_db = []
            for i in range(0, len(samples), chunk_size):
                chunk = samples[i:i+chunk_size]
                if not chunk:
                    break
                rms = math.sqrt(sum(s**2 for s in chunk) / len(chunk))
                db = 20 * math.log10(rms + 1e-9)
                raw_db.append(db)
            if not raw_db:
                raise RuntimeError("No intensity values computed.")
            
            # — Changed: apply exponential moving average smoothing —
            smoothed_db = []
            prev = raw_db[0]
            for db in raw_db:
                # new = α·current + (1−α)·previous
                prev = self.SMOOTH_FACTOR * db + (1 - self.SMOOTH_FACTOR) * prev
                smoothed_db.append(prev)
            # — end changes —

            # normalize on smoothed values
            min_db, max_db = min(smoothed_db), max(smoothed_db)
            span = max_db - min_db
            
            self.intensities = []
            if span == 0:
                self.intensities = [0] * len(smoothed_db)
            else:
                for db in smoothed_db:
                    normalized = (db - min_db) / span
                    gamma_corrected = normalized ** self.GAMMA
                    self.intensities.append(int(gamma_corrected * 255))
            Log.info("EngineAudioTest", f"Calculated {len(self.intensities)} intensity values.")

        except Exception as e:
            Log.error("EngineAudioTest", f"Failed to load or process audio file: {e}")
            return
        self.ready_callback()

    def on_frame(self, current_time: float):
        idx = int(current_time * self.FPS)
        b = self.intensities[idx] if idx < len(self.intensities) else 0
        Log.debug("EngineAudioTest", f"{current_time:.2f}s: {b}")
        self.renderer.fill((0, b, 0))
        self.renderer.show()
