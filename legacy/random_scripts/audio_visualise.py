import os
import math
import sys
import pygame
from pydub import AudioSegment
import matplotlib.pyplot as plt

# --- Config ---
AUDIO_FILE = "quaoar.wav"   # file under ./audio/
FPS = 24                         # frames per second / chunks per second
WINDOW_SIZE = (400, 400)         # window dimensions
GAMMA = 5
VISUALIZE = True                 # True for pygame, False for matplotlib plot
VISUAL_OFFSET_S = 0            # Visual offset in seconds to compensate for lag

def calculate_intensities(path: str, fps: int):
    audio = AudioSegment.from_file(path)
    if audio.channels > 1:
        audio = audio.set_channels(1)
    framerate = audio.frame_rate
    audio_length = len(audio) / 1000.0
    samples = audio.get_array_of_samples()
    chunk_size = max(1, int(framerate / fps))
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
    min_db, max_db = min(raw_db), max(raw_db)
    span = max_db - min_db
    
    intensities = []
    if span == 0:
        intensities = [0] * len(raw_db)
    else:
        for db in raw_db:
            normalized = (db - min_db) / span
            gamma_corrected = normalized ** GAMMA
            intensities.append(int(gamma_corrected * 255))

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

def run_visualizer(intensities, fps, audio_path):
    pygame.init()
    # — New: initialize mixer & play audio —
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    # — End new —

    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    running = True
    while running:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                running = False

        if not pygame.mixer.music.get_busy():
            # audio finished → stop visualizer
            break

        current_time_s = pygame.mixer.music.get_pos() / 1000.0
        compensated_time_s = current_time_s + VISUAL_OFFSET_S
        idx = int(compensated_time_s * fps)

        if idx < len(intensities):
            val = intensities[idx]
        else:
            val = 0
        screen.fill((0, val, 0))
        pygame.display.flip()
        clock.tick(fps)

    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    audio_path = os.path.join("audio", AUDIO_FILE)
    if not os.path.isfile(audio_path):
        print(f"Audio file not found: {audio_path}")
        sys.exit(1)
    try:
        print("Calculating intensities...")
        intensities, audio_length = calculate_intensities(audio_path, FPS)
        print("Done.")

        if VISUALIZE:
            run_visualizer(intensities, FPS, audio_path)
        else:
            plot_intensities(intensities, audio_length)
    except Exception as e:
        print("Error:", e)
