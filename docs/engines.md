# Engines

Each engine is a separate module that can manipulate the lights in a different way. The engine manager dynamically enables/disables engines so only one engine is active at a time.

Building an engine is simple, but adding client API or web UI requires editing `server.py` and the web files.

Each engine must inherit from `Engine` (imported from `modules.engine`) and implement lifecycle hooks. Any function that manipulates the lights must be decorated by the `EngineManager.requires_active` decorator so the manager can make sure the engine is active and others aren't when executing.

## Engine Documentation

Functions
- `on_enable() -> None`  
  Description: Called when this engine becomes active. Start lightweight resources or resume tasks here.

- `on_disable() -> None`  
  Description: Called when this engine is being disabled (another engine enabled or shutdown). Clean up resources and stop tasks. However, do not count on this being called before the app shutdown. 

- `on_setup_changed(setup: modules.setup.Setup) -> None`  
  Description: Called whenever the system setup changes (for example, pixel layout or count changes). Engines should update internal state to match the new configuration. This is invoked for all engines (enabled or not).  
  Args:
    - `setup (Setup)`: Updated setup/configuration object.

## AudioEngine
AudioEngine is inherited from `Engine` and provides functions for audio playback and frame generation based on the audio. It is designed to be used with audio files, and it provides a callback functions for frame generation and playback control actions.

## AudioEngine Documentation

Built-in attributes
- `renderer` - LEDRenderer instance 
- `ready_callback` - callable invoked when preprocessing (e.g., frame generation) is complete and playback can start.  
- `FPS` (int) - target frames-per-second for `on_frame` callbacks.  
- `current_time` (float) - current playback time in seconds.  
- `audio_length` (float) - length of the loaded audio in seconds.  
- `playback_start_time` (float) - monotonic time when playback started.  
- `seek_time_at_start` (float) - playback position at the moment playback started/restarted.

Lifecycle & playback functions
- `__init__(renderer, ready_callback) -> None`  

- `on_enable() -> None`  
  Description: Engine enabled; start or resume lightweight audio-related resources. Heavy work should be done in `__init__` or `on_audio_load`.

- `on_disable() -> None`  
  Description: Engine disabled; should stop playback and clear lights (typically calls `on_audio_stop`).

- `on_audio_load(audio_path: str) -> None`  
  Description: Called when the user is loading an audio file. You should precompute all light states and necessary data here. Call `ready_callback()` when ready.  
  Args:
    - `audio_path (str)`: Filesystem path or identifier of the audio file.

- `on_audio_play() -> None`

- `on_audio_pause() -> None`  

- `on_audio_stop() -> None`  

- `on_audio_seek(position: float) -> None`  
  Args:
    - `position (float)`: Target playback time in seconds.

- `on_frame(current_time: float) -> None`  
  Description: Called repeatedly by the runner while playing, you should update the lights here based on the current playback time.
  Args:
    - `current_time (float)`: Playback time in seconds for this frame.

Implementation notes
- Avoid blocking the main thread; precompute heavy data during `on_audio_load`.
- Still use `EngineManager.requires_active` for on_audio_load and on_frame to ensure the engine is active.