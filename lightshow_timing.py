from pynput.keyboard import Key, Listener
import pygame

pygame.mixer.init()
pygame.mixer.music.load("centipede.ogg")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play()

def on_press(key):
    print(f"{pygame.mixer.music.get_pos() / 1000:.3f}: {key}")
    #1v1v1v111v1v1v1v1v1v1v1v56048pva
def on_release(key):
    if key == Key.esc:
        # Stop listener
        return False

# Collect events until released
with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()