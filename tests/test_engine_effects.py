import pytest
import os
import time
from modules.engine_effects import EffectsEngine
from modules.engine_manager import EngineManager
from modules.setup import Setup, SetupType
from modules.effect import EffectType
from modules.led_renderer import DummyRenderer
from modules.config_manager import Config

@pytest.fixture
def effects_engine(mock_setup, dummy_renderer):
    # Ensure Config is initialized with a blank slate for testing
    Config().config = {}
    
    manager = EngineManager()
    engine = EffectsEngine(dummy_renderer, mock_setup)
    engine.setup = mock_setup
    engine.coords = mock_setup.coords
    manager.register_engine(engine)
    manager.active_engine = engine
    
    return engine

def test_effects_engine_init(effects_engine, dummy_renderer):
    assert effects_engine.renderer == dummy_renderer
    assert effects_engine.current_effect is None
    assert isinstance(effects_engine.effects, dict)

def test_load_effects(effects_engine):
    effects = effects_engine.load_effects()
    assert isinstance(effects, dict)
    assert len(effects) > 0, "Expected at least one effect to load from the 'effects' directory"

def test_get_state_empty(effects_engine):
    # If no effects are loaded, state should be entirely None
    effects_engine.effects = {}
    state = effects_engine.get_state()
    assert state == {
        "current_effect": None,
        "parameters": None,
        "effect_type": None
    }

def test_set_effect(effects_engine):
    effects_engine.load_effects()
    first_effect_name = list(effects_engine.effects.keys())[0]
    
    result = effects_engine.set_effect(first_effect_name)
    assert result["status"] == "success"
    assert result["current_effect"] == first_effect_name
    
    state = effects_engine.get_state()
    assert state["current_effect"] == first_effect_name
    assert "parameters" in state
    assert "effect_type" in state

def test_set_invalid_effect(effects_engine):
    result = effects_engine.set_effect("this_effect_should_never_exist_12345")
    assert result["status"] == "error"
    assert result["message"] == "Effect not found"

def test_enable_disable(effects_engine):
    effects_engine.on_enable()
    assert effects_engine.running is True
    assert effects_engine.runner_thread is not None
    assert effects_engine.runner_thread.is_alive()

    effects_engine.on_disable()
    assert effects_engine.running is False
    # allow thread to stop
    time.sleep(0.1)
    assert not effects_engine.runner_thread.is_alive()
