from modules.engine import AudioEngine
from modules.engine_manager import EngineManager
from modules.log_manager import Log
from pydub import AudioSegment
import time
import threading
import os
import math

class AudioTestEngine(AudioEngine):
    """
    Let's see if this works
    """

    def __init__(self, renderer, ready_callback):
        Log.info("EngineAudioTest", "Initializing EngineAudioTest.")
        self.ready_callback = ready_callback
        self.renderer = renderer
        self.FPS = 60
        self._stop_flag = False
        self._runner_thread = None
        self.current_time = 0
        self.GAMMA = 10
        self.SMOOTH_FACTOR = 0.6
        self.frame_length = 1 / self.FPS

    def on_enable(self):
        Log.info("EngineAudioTest", "EngineAudioTest enabled.")

    def on_disable(self):
        Log.info("EngineAudioTest", "EngineAudioTest disabled.")
        self.on_audio_stop()

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

    @EngineManager.requires_active
    def on_audio_play(self):
        self._stop_flag = False
        if self._runner_thread and self._runner_thread.is_alive():
            self._runner_thread.join()
        
        self.playback_start_time = time.monotonic()
        self.seek_time_at_start = self.current_time

        self._runner_thread = threading.Thread(target=self._runner, daemon=True)
        self._runner_thread.start()

    @EngineManager.requires_active
    def on_audio_pause(self):
        Log.info("EngineAudioTest", "Audio playback paused.")
        self._stop_flag = True
        if self._runner_thread and self._runner_thread.is_alive():
            self._runner_thread.join()

    @EngineManager.requires_active
    def on_audio_stop(self):
        Log.info("EngineAudioTest", "Audio playback stopped.")
        self._stop_flag = True
        if self._runner_thread and self._runner_thread.is_alive():
            self._runner_thread.join()
        self.renderer.fill((0, 0, 0))
        self.renderer.show()

    @EngineManager.requires_active
    def on_audio_seek(self, position: float):
        self.current_time = position
        # If playing, update start times to resync the loop
        if self._runner_thread and self._runner_thread.is_alive():
            self.playback_start_time = time.monotonic()
            self.seek_time_at_start = self.current_time
        Log.info("EngineAudioTest", f"Audio jumped to position: {self.current_time}s.")

    def _runner(self):
        while not self._stop_flag:
            # Calculate current time based on wall clock to prevent drift
            elapsed = time.monotonic() - self.playback_start_time
            self.current_time = self.seek_time_at_start + elapsed

            if self.current_time >= self.audio_length:
                break

            idx = int(self.current_time * self.FPS)
            b = self.intensities[idx] if idx < len(self.intensities) else 0
            Log.debug("EngineAudioTest", f"{self.current_time:.2f}s: {b}")
            self.renderer.fill((0, b, 0))
            self.renderer.show()
            time.sleep(1 / self.FPS)

        # auto-cleanup on natural end
        if not self._stop_flag:
            self.on_audio_stop()
