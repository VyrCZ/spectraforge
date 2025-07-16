import pygame, wave
import numpy as np
import numpy.fft as fft

# config variables
AUDIO_FILE = 'audio/quaoar.wav'
BAR_COUNT = 128

# load entire audio and convert to mono array
with wave.open(AUDIO_FILE, 'rb') as wf:
    sample_rate = wf.getframerate()
    channels = wf.getnchannels()
    raw = wf.readframes(wf.getnframes())
audio = np.frombuffer(raw, dtype=np.int16)
if channels == 2:
    audio = audio.reshape(-1, 2).mean(axis=1)

def main():
    pygame.mixer.init(frequency=sample_rate)
    pygame.init()
    pygame.mixer.music.load(AUDIO_FILE)
    pygame.mixer.music.play()

    WIDTH, HEIGHT = 800, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # print log-spaced ranges
    freqs = np.fft.rfftfreq(1024, d=1/sample_rate)
    edges = np.logspace(np.log10(freqs[1]), np.log10(freqs[-1]), BAR_COUNT+1)
    for i in range(BAR_COUNT):
        print(f"Bar {i}: {edges[i]:.1f}-{edges[i+1]:.1f} Hz")

    while pygame.mixer.music.get_busy():
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return

        # current playback index
        pos_ms = pygame.mixer.music.get_pos()
        idx = int(pos_ms * sample_rate / 1000)
        window = audio[idx:idx+1024]
        if window.size < 1024:
            window = np.pad(window, (0, 1024-window.size), 'constant')

        # frequency-domain bands via FFT
        spectrum = np.abs(fft.rfft(window))
        half = spectrum[:len(spectrum)]
        # build log-spaced bins
        freqs = np.fft.rfftfreq(1024, d=1/sample_rate)
        edges = np.logspace(np.log10(freqs[1]), np.log10(freqs[-1]), BAR_COUNT+1)
        idx = np.searchsorted(freqs, edges)
        amps = []
        for i in range(BAR_COUNT):
            s, e = idx[i], idx[i+1]
            amps.append(spectrum[s:e].mean() if e > s else 0.0)

        # draw bars
        screen.fill((0,0,0))
        bar_w = WIDTH / BAR_COUNT
        for i, a in enumerate(amps):
            h = (a / np.max(amps)) * HEIGHT
            rect = pygame.Rect(i*bar_w, HEIGHT-h, bar_w-2, h)
            pygame.draw.rect(screen, (0,255,0), rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()
