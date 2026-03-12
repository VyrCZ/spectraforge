import pytest

from modules.engine import AudioEngine, Engine
from modules.engine_manager import EngineManager
from modules.setup import Setup, SetupType


class StubEngine(Engine):
    def __init__(self):
        self.enabled = 0
        self.disabled = 0
        self.setup_changes = []

    def on_enable(self):
        self.enabled += 1

    def on_disable(self):
        self.disabled += 1

    def on_setup_changed(self, setup):
        self.setup_changes.append(setup)

    @EngineManager.requires_active
    def ping(self):
        return "pong"


class StubAudioEngine(AudioEngine):
    def __init__(self):
        self.frames = []
        self.loaded = None
        super().__init__(renderer=type("Renderer", (), {"fill": lambda self, color: None, "show": lambda self: None})(), ready_callback=lambda *args: None)

    def on_enable(self):
        return None

    def on_audio_load(self, audio_path: str):
        self.loaded = audio_path

    def on_frame(self, current_time: float):
        self.frames.append(current_time)


@pytest.fixture
def fresh_manager(monkeypatch):
    EngineManager._instance = None
    EngineManager._initialized = False
    from modules.config_manager import Config
    Config().config = {}
    manager = EngineManager()
    manager.engines = []
    manager.active_engine = None
    manager.active_setup = None
    return manager


def test_register_engine_enables_first_engine(fresh_manager):
    engine = StubEngine()
    fresh_manager.register_engine(engine)
    assert fresh_manager.active_engine is engine
    assert engine.enabled == 1
    assert engine.manager is fresh_manager


def test_requires_active_raises_for_unregistered_engine():
    engine = StubEngine()
    with pytest.raises(EngineManager.EngineNotRegisteredError):
        engine.ping()


def test_requires_active_switches_active_engine(fresh_manager):
    first = StubEngine()
    second = StubEngine()
    fresh_manager.register_engine(first)
    fresh_manager.register_engine(second)
    assert second.ping() == "pong"
    assert fresh_manager.active_engine is second
    assert first.disabled == 1
    assert second.enabled == 1


def test_register_audio_engine_requires_audio_subclass(fresh_manager):
    with pytest.raises(TypeError):
        fresh_manager.register_audio_engine(StubEngine())


def test_change_setup_notifies_engines_and_adds_z_for_2d(fresh_manager):
    engine = StubEngine()
    fresh_manager.register_engine(engine)
    setup = Setup("demo", SetupType.TWO_DIMENSIONAL, [[1, 2], [3, 4]])
    fresh_manager.change_setup(setup)
    assert setup.coords == [[1, 2, 0], [3, 4, 0]]
    assert engine.setup_changes[-1] is setup


def test_audio_callbacks_success_and_errors(fresh_manager):
    engine = StubAudioEngine()
    fresh_manager.register_audio_engine(engine)
    fresh_manager.active_engine = engine
    fresh_manager.audio_callbacks("load", "song.mp3")
    assert engine.loaded == "song.mp3"

    fresh_manager.active_engine = StubEngine()
    with pytest.raises(EngineManager.NonAudioEngineActiveError):
        fresh_manager.audio_callbacks("play")

    fresh_manager.active_engine = engine
    with pytest.raises(AttributeError):
        fresh_manager.audio_callbacks("missing")