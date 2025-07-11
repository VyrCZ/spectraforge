from abc import ABC, abstractmethod
from modules.setup import Setup

class Engine(ABC):
    """
    The engine system is designed to manage individual system that manage the LED effects.
    Each engine must implement the `on_enable` and `on_disable` methods to handle changing the engines. If you use the setup system, you should also implement the `on_setup_changed` method to handle changes in the setup.
    The engine can communicate with the app using its own methods, but they all must have a decorator @EngineManager.requres_active, which will ensure that the engine is active before executing the method and disabling another engine, if necessary.
    """

    @abstractmethod
    def on_enable(self):
        """
        Called when the engine is enabled. **(But not on the startup of the engine)**

        Use __init__ to set up the engine
        """
        pass

    @abstractmethod
    def on_disable(self):
        """Called when the engine is being disabled. *(It is called on the shutdown of the app, but the app is usually not ended gracefully, so do not rely on this method to save the state of the engine)*"""
        pass

    def on_setup_changed(self, setup: Setup):
        """
        Called when the setup is changed, regardless if enabled or not **(But not on the init of the engine)**
        """
        pass



class AudioEngine(Engine):
    """
    AudioEngine is an extension of the regular Engine class, with the callbacks for audio events.
    It is used to create effects using audio. Playback and loading of the audio is handled by the server, this class is only responsible for the effects and showing the lights.

    When the user wants to use the audio engine, it will be automatically enabled with the selected audio file.
    
    **When on_audio_load is called, it is strongly recommended to calculate the light states for the whole audio file, due to performance. When your calculation logic is completed, you must call ready_for_playback to let the server know that the engine is finished and ready.**
    """
    @abstractmethod
    def on_enable(self):
        """
        Called when the engine is enabled. **(But not on the startup of the engine)**

        Use __init__ to set up the engine
        """
        pass

    @abstractmethod
    def on_disable(self):
        """
        Called when the engine is being disabled. *(It is called on the shutdown of the app, but the app is usually not ended gracefully, so do not rely on this method to save the state of the engine)*
        """
        pass

    @abstractmethod
    def on_audio_load(self, audio_path: str):
        """
        Called when the audio is loaded. This is called when the audio is loaded from the file or from the stream.
        """
        pass

    @abstractmethod
    def on_audio_play(self):
        """
        Called when the audio is played in the player.
        """
        pass

    @abstractmethod
    def on_audio_pause(self):
        """
        Called when the audio is paused in the player.
        """
        pass

    @abstractmethod
    def on_audio_stop(self):
        """
        Called when the audio is stopped in the player.
        """
        pass

    @abstractmethod
    def on_audio_seek(self, position: float):
        """
        Called when the user seeks to a different part of the audio in the player.

        Position is in seconds.
        """
        pass
