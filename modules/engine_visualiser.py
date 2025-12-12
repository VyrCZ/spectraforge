from modules.engine import AudioEngine
from modules.engine_manager import EngineManager
from modules.log_manager import Log
from pydub import AudioSegment
import os
import math
import json
import numpy as np
from scipy.fft import rfft, rfftfreq
import colorsys
import modules.caching as cache

class VisualiserEngine(AudioEngine):
    """
    Let's see if this works
    """

    def __init__(self, renderer, active_setup, ready_callback):
        Log.info("EngineVisualiser", "Initializing EngineVisualiser.")
        super().__init__(renderer, ready_callback)
        self.bar_count = 16  # Number of bars in the visualiser
        self.GAMMA = 8
        self.SMOOTH_FACTOR = 0.8
        self.led_bar_indices = []
        self.led_y_norm = []
        self.bar_heights = []
        self.bar_colors = []
        self.on_setup_changed(active_setup)

    def on_enable(self):
        Log.info("EngineVisualiser", "EngineVisualiser enabled.")

    def on_disable(self):
        Log.info("EngineVisualiser", "EngineVisualiser disabled.")
        super().on_disable()
    
    def on_setup_changed(self, setup):
        self.coords = setup.coords
        self.minx = min(coord[0] for coord in self.coords)
        self.maxx = max(coord[0] for coord in self.coords)
        self.miny = min(coord[1] for coord in self.coords)
        self.maxy = max(coord[1] for coord in self.coords)
        self.bar_width = (self.maxx - self.minx) / self.bar_count
        self.led_bar_indices = [int((coord[0] - self.minx) / self.bar_width) for coord in self.coords]
        self.led_y_norm = [(coord[1] - self.miny) / (self.maxy - self.miny) if self.maxy > self.miny else 0 for coord in self.coords]
        
        self.bar_colors = []
        for i in range(self.bar_count):
            hue = i / self.bar_count
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            self.bar_colors.append((int(r * 255), int(g * 255), int(b * 255)))


    @EngineManager.requires_active
    def on_audio_load(self, audio_file: str):
        Log.info("EngineVisualiser", f"Loading audio file: {audio_file}")
        self.bar_heights = []
        
        audio_path = os.path.join("audio", audio_file)
        try:
            mtime = os.path.getmtime(audio_path)
            size = os.path.getsize(audio_path)
            cache_key = f"{audio_path}:{mtime}:{size}"
        except OSError:
            Log.error("EngineVisualiser", f"Could not access audio file at {audio_path}")
            return

        cached_data = cache.get_cache_by_data("visualiser", cache_key)
        if cached_data:
            Log.info("EngineVisualiser", "Using cached audio data.")
            data = json.loads(cached_data)
            self.bar_heights = data['heights']
            self.audio_length = data['length']
            Log.info("EngineVisualiser", f"Audio length: {self.audio_length} seconds.")
            self.ready_callback()
            return
        
        try:
            audio = AudioSegment.from_file(audio_path)

            if audio.channels > 1:
                Log.debug("EngineVisualiser", "Audio is not mono, converting to mono.")
                audio = audio.set_channels(1)

            framerate = audio.frame_rate
            self.audio_length = len(audio) / 1000.0
            Log.info("EngineVisualiser", f"Audio length: {self.audio_length} seconds.")

            samples = np.array(audio.get_array_of_samples())
            Log.debug("EngineVisualiser", f"Extracted {len(samples)} samples from audio file.")

            chunk_size = int(framerate / self.FPS)
            if chunk_size == 0:
                Log.error("EngineVisualiser", "FPS is too high for this audio's framerate.")
                return

            num_frames = int(len(samples) / chunk_size)
            
            # STFT
            all_fft_magnitudes = []
            for i in range(num_frames):
                chunk = samples[i*chunk_size : (i+1)*chunk_size]
                fft_result = rfft(chunk)
                fft_magnitudes = np.abs(fft_result)
                all_fft_magnitudes.append(fft_magnitudes)
            
            all_fft_magnitudes = np.array(all_fft_magnitudes)
            freqs = rfftfreq(chunk_size, 1/framerate)

            # Logarithmic frequency bands
            max_freq = freqs[-1]
            # Ensure min frequency is not zero for log scale
            min_freq = max(20, freqs[1]) if len(freqs) > 1 else 20
            log_freq_bands = np.logspace(np.log10(min_freq), np.log10(max_freq), self.bar_count + 1)
            
            band_intensities = np.zeros((num_frames, self.bar_count))

            # For each frequency from the FFT, find which bar it belongs to.
            # np.digitize is perfect for this "histogram" style binning.
            band_indices = np.digitize(freqs, log_freq_bands) - 1

            # Now, for each bar, sum the magnitudes of all frequencies that fall into it.
            for i in range(self.bar_count):
                # Find all FFT frequency indices that belong to the current bar 'i'
                freq_indices_for_bar = np.where(band_indices == i)[0]
                
                if len(freq_indices_for_bar) > 0:
                    # Sum the magnitudes for each frame to get total energy in the band.
                    # Using np.sum() instead of np.mean() gives a more balanced visualization.
                    band_intensities[:, i] = np.sum(all_fft_magnitudes[:, freq_indices_for_bar], axis=1)

            # Convert to dB scale
            with np.errstate(divide='ignore'):
                db_intensities = 20 * np.log10(band_intensities + 1e-9) # Add epsilon to avoid log(0)

            # Smoothing and Normalization
            smoothed_intensities = np.zeros_like(db_intensities)
            prev_frame = db_intensities[0]
            for i in range(num_frames):
                current_frame = db_intensities[i]
                smoothed_frame = self.SMOOTH_FACTOR * current_frame + (1 - self.SMOOTH_FACTOR) * prev_frame
                smoothed_intensities[i] = smoothed_frame
                prev_frame = smoothed_frame

            min_val = np.min(smoothed_intensities)
            max_val = np.max(smoothed_intensities)
            span = max_val - min_val

            if span > 0:
                normalized = (smoothed_intensities - min_val) / span
                gamma_corrected = normalized ** self.GAMMA
                self.bar_heights = gamma_corrected
            else:
                self.bar_heights = np.zeros_like(smoothed_intensities)

            # cache the result
            cache_content = {
                'length': self.audio_length,
                'heights': self.bar_heights.tolist()
            }
            cache.set_cache_by_data("visualiser", cache_key, json.dumps(cache_content))

            Log.info("EngineVisualiser", f"Calculated {len(self.bar_heights)} heights.")

        except Exception as e:
            Log.error("EngineVisualiser", f"Failed to load or process audio file: {e}")
            return
        self.ready_callback()

    @EngineManager.requires_active
    def on_frame(self, current_time: float):
        if not self.led_bar_indices:
            return

        idx = int(current_time * self.FPS)
        if idx >= len(self.bar_heights):
            self.renderer.fill((0, 0, 0))
            self.renderer.show()
            return

        current_heights = self.bar_heights[idx]
        
        for i in range(len(self.renderer)):
            bar_index = self.led_bar_indices[i]
            if bar_index >= self.bar_count: continue

            bar_height = current_heights[bar_index]
            
            if self.led_y_norm[i] <= bar_height:
                self.renderer[i] = self.bar_colors[bar_index]
            else:
                self.renderer[i] = (0, 0, 0)
        self.renderer.show()
