from pynput.keyboard import Key, Listener
import pygame
import time

presses = []

audio_path = "lightshow/static/audio/peer_gynt.mp3"
pygame.mixer.init()
pygame.mixer.music.load(audio_path)
pygame.mixer.music.set_volume(0.1)

for x in range(3, 0, -1):
    print(f"Countdown: {x}")
    time.sleep(1)
pygame.mixer.music.play()

def on_press(key):
    print(f"{pygame.mixer.music.get_pos() / 1000:.3f}: {key}")
    presses.append((pygame.mixer.music.get_pos() / 1000, key))
def on_release(key):
    if key == Key.esc:
        for press in presses:
            print(f"{press[0]:.3f}, {press[1]}")
        # Stop listener
        return False

# Collect events until released
with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()