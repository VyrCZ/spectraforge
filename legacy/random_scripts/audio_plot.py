import os
import math
import matplotlib.pyplot as plt
from pydub import AudioSegment

# --- Config ---
AUDIO_FILE = "thursday.wav"  # Place your file in the ./audio directory
FPS = 60  # Adjust depending on how fine-grained the graph should be
GAMMA = 10
AUDIO_PATH = os.path.join("audio", AUDIO_FILE)

def calculate_intensities(audio_file_path: str, fps: int):
    print(f"Loading audio file: {audio_file_path}")
    intensities = []

    audio = AudioSegment.from_mp3(audio_file_path)

    if audio.channels > 1:
        print("Audio is not mono, converting to mono.")
        audio = audio.set_channels(1)

    framerate = audio.frame_rate
    audio_length = len(audio) / 1000.0
    print(f"Audio length: {audio_length:.2f} seconds.")

    samples = audio.get_array_of_samples()
    print(f"Extracted {len(samples)} samples from audio.")

    chunk_size = int(framerate / fps)
    if chunk_size == 0:
        raise ValueError("FPS is too high for this audio's framerate.")

    raw_intensities = []
    for i in range(0, len(samples), chunk_size):
        chunk = samples[i:i + chunk_size]
        if not chunk:
            continue
        rms = math.sqrt(sum(s**2 for s in chunk) / len(chunk))
        db = 20 * math.log10(rms + 1e-9)  # +1e-9 avoids log(0)
        raw_intensities.append(db)

    if not raw_intensities:
        raise ValueError("Could not calculate any intensity values.")
    
    min_db = min(raw_intensities)
    max_db = max(raw_intensities)

    if max_db == min_db:
        intensities = [128] * len(raw_intensities) # Or 0, or 255, depending on desired behavior for silence
    else:
        # Normalize to 0-1 range, apply gamma, then scale to 0-255
        intensities = []
        for db in raw_intensities:
            normalized = (db - min_db) / (max_db - min_db)
            gamma_corrected = normalized ** GAMMA
            intensities.append(gamma_corrected * 255)

    return intensities, audio_length

def plot_intensities(intensities, audio_length):
    timestamps = [i * (audio_length / len(intensities)) for i in range(len(intensities))]
    plt.figure(figsize=(12, 4))
    plt.plot(timestamps, intensities, color='purple')
    plt.title("Audio Brightness Intensity Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Intensity (0-255)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    try:
        intensities, length = calculate_intensities(AUDIO_PATH, FPS)
        plot_intensities(intensities, length)
    except Exception as e:
        print(f"Error: {e}")
