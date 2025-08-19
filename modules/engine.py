from abc import ABC, abstractmethod
from modules.setup import Setup
import threading
import time

class Engine(ABC):
    """
    Base class for all engines that control LED effects.

    Description:
        Engines implement effect logic and lifecycle hooks. The engine manager
        enables/disables engines and ensures only one engine is active at a time.
        If the engine uses the setup system, implement on_setup_changed to react
        to setup updates. Callbacks that manipulate lights should be guarded by
        the EngineManager.requires_active decorator so the manager can ensure the
        engine is active when invoked.

    Methods:
        on_enable(): Called when the engine is enabled.
        on_disable(): Called when the engine is disabled.
        on_setup_changed(setup): Called when the setup changes.
    """

    @abstractmethod
    def on_enable(self):
        """
        Called when the engine is enabled.

        Description:
            Perform any startup work that should occur when this engine becomes
            active. Heavy initialization that must run once should be done in
            __init__.

        Args:
            None

        Returns:
            None
        """
        pass

    @abstractmethod
    def on_disable(self):
        """
        Called when the engine is being disabled.

        Description:
            Clean up any resources allocated by the engine and stop ongoing
            tasks. This will be called when another engine is enabled or when
            the application requests a shutdown. Do not rely on this method for
            guaranteed persistent storage as the app may not always shut down
            gracefully.

        Args:
            None

        Returns:
            None
        """
        pass

    def on_setup_changed(self, setup: Setup):
        """
        Called when the setup configuration changes.

        Description:
            Receive the updated Setup instance and adjust internal state to
            match the new configuration. This is called for all engines whether
            or not they are currently enabled (not called during engine __init__).

        Args:
            setup (Setup): The new setup configuration.

        Returns:
            None
        """
        pass



class AudioEngine(Engine):
    """
    Engine extension for audio-driven effects.

    Description:
        Provides lifecycle and playback hooks for engines that drive lights
        based on audio playback. The server handles loading and playback; this
        class provides callbacks for load/play/pause/stop/seek and a regular
        on_frame callback during playback. When on_audio_load is called, it is
        recommended to precompute frames for the entire audio track and then
        call the provided ready_callback to signal readiness for playback.

    Attributes:
        renderer: Renderer object used to set and show pixel colors.
        ready_callback (callable): Callback to call when the engine is ready for playback (e.g., after preprocessing).
        FPS (int): Target frames per second for on_frame callbacks.
        current_time (float): Current playback position in seconds.
        audio_length (float): Length of the currently loaded audio in seconds.
        playback_start_time (float): Monotonic time when playback started.
        seek_time_at_start (float): Playback position at the moment playback started.
    """
    def __init__(self, renderer, ready_callback):
        """
        Initialize the AudioEngine.

        Args:
            renderer: Renderer instance with fill/show methods to update lights.
            ready_callback (callable): Function to call when the engine finished
                preparing for playback (e.g., after precomputing frames).

        Returns:
            None
        """
        self.renderer = renderer
        self.ready_callback = ready_callback
        self.FPS = 60
        self._stop_flag = False
        self._runner_thread: threading.Thread | None = None
        self.current_time = 0.0
        self.audio_length = 0.0
        self.playback_start_time = 0.0
        self.seek_time_at_start = 0.0
        self._time = time

    @abstractmethod
    def on_enable(self):
        """
        Called when the audio engine is enabled.

        Description:
            Start or resume any engine-specific resources required for audio
            effects. Lightweight enable logic belongs here; heavy work should be
            done in __init__ or on_audio_load.

        Args:
            None

        Returns:
            None
        """
        pass

    def on_disable(self):
        """
        Called when the audio engine is being disabled.

        Description:
            Stop playback and clear lights. This will call on_audio_stop to
            ensure playback loop and rendering are terminated and the renderer
            is cleared.

        Args:
            None

        Returns:
            None
        """
        self.on_audio_stop()

    @abstractmethod
    def on_audio_load(self, audio_path: str):
        """
        Called when an audio file is loaded for playback.

        Description:
            Prepare the engine for the provided audio file. It is strongly
            recommended to precompute any state or frames for the entire audio
            file here for performance reasons. When preprocessing is complete,
            call the ready_callback to notify the server that playback can
            start.

        Args:
            audio_path (str): Filesystem path or identifier for the audio file.

        Returns:
            None
        """
        pass

    def on_audio_play(self):
        """
        Called when audio playback starts.

        Description:
            Starts the internal runner thread that calls on_frame at the target
            FPS. If a previous runner thread is running, it will be joined
            before starting a new one.

        Args:
            None

        Returns:
            None
        """
        self._stop_flag = False
        if self._runner_thread and self._runner_thread.is_alive():
            self._runner_thread.join()
        
        self.playback_start_time = self._time.monotonic()
        self.seek_time_at_start = self.current_time

        self._runner_thread = threading.Thread(target=self._runner, daemon=True)
        self._runner_thread.start()

    def on_audio_pause(self):
        """
        Called when audio playback is paused.

        Description:
            Signals the runner thread to stop and waits for it to finish so the
            current_time remains at the paused position.

        Args:
            None

        Returns:
            None
        """
        self._stop_flag = True
        if self._runner_thread and self._runner_thread.is_alive():
            self._runner_thread.join()

    def on_audio_stop(self):
        """
        Called when audio playback stops.

        Description:
            Stops the playback runner, clears the renderer (sets pixels to
            black), and resets current_time to the start of the track.

        Args:
            None

        Returns:
            None
        """
        self._stop_flag = True
        if self._runner_thread and self._runner_thread.is_alive():
            if threading.current_thread() != self._runner_thread:
                self._runner_thread.join()
        self.renderer.fill((0, 0, 0))
        self.renderer.show()
        self.current_time = 0.0

    def on_audio_seek(self, position: float):
        """
        Called when playback is seeked to a different position.

        Description:
            Update internal playback position. If playback is active the
            playback_start_time and seek_time_at_start are adjusted so the
            runner continues from the new position.

        Args:
            position (float): Target playback position in seconds.

        Returns:
            None
        """
        self.current_time = position
        if self._runner_thread and self._runner_thread.is_alive():
            self.playback_start_time = self._time.monotonic()
            self.seek_time_at_start = self.current_time

    @abstractmethod
    def on_frame(self, current_time: float):
        """
        Frame callback invoked repeatedly during audio playback.

        Description:
            Implement this method to update the renderer for the given playback
            time. This is called at approximately FPS times per second while
            playback is active.

        Args:
            current_time (float): Playback time in seconds for this frame.

        Returns:
            None
        """
        pass

    def _runner(self):
        """
        Internal runner loop that advances playback time and invokes on_frame.

        Description:
            Runs in a background daemon thread while playback is active. The
            loop updates current_time from monotonic timing and calls on_frame
            until either the stop flag is set or the audio_length is reached.
            If playback reaches the end naturally, on_audio_stop is called.

        Args:
            None

        Returns:
            None
        """
        while not self._stop_flag:
            elapsed = self._time.monotonic() - self.playback_start_time
            self.current_time = self.seek_time_at_start + elapsed

            if self.current_time >= self.audio_length:
                break

            self.on_frame(self.current_time)
            
            self._time.sleep(1 / self.FPS)

        if not self._stop_flag:
            self.on_audio_stop()
