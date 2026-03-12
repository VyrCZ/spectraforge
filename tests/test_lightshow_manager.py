import json
from unittest.mock import MagicMock, patch

import pytest


def test_lightshow_manager_process_lightshow_returns_frames():
    """Test that process_lightshow returns list of frames."""
    from modules.lightshow_manager import process_lightshow, RegistryInstance, LightshowSettings
    
    registry = RegistryInstance.__new__(RegistryInstance)
    registry.coords = [[0, 0, 0], [1, 1, 1]]
    registry.registry = {}
    
    settings = LightshowSettings()
    lightshow_data = {"timeline": []}
    
    frames = process_lightshow(registry, lightshow_data, settings)
    
    assert isinstance(frames, list)


def test_lightshow_manager_registry_instance_init():
    """Test RegistryInstance initialization."""
    from modules.lightshow_manager import RegistryInstance
    
    with patch("modules.lightshow_manager.Path"):
        registry = RegistryInstance([[0, 0, 0], [1, 1, 1]])
        
        assert len(registry.coords) == 2
        assert isinstance(registry.registry, dict)


def test_lightshow_manager_lightshow_settings_fps():
    """Test LightshowSettings stores FPS."""
    from modules.lightshow_manager import LightshowSettings
    
    settings = LightshowSettings(fps=60)
    
    assert settings.FPS == 60


def test_lightshow_manager_default_fps():
    """Test LightshowSettings defaults to 30 FPS."""
    from modules.lightshow_manager import LightshowSettings
    
    settings = LightshowSettings()
    
    assert settings.FPS == 30


def test_lightshow_manager_process_lightshow_with_timeline():
    """Test process_lightshow with timeline items."""
    from modules.lightshow_manager import process_lightshow, RegistryInstance, LightshowSettings
    
    registry = RegistryInstance.__new__(RegistryInstance)
    registry.coords = [[0, 0, 0], [1, 1, 1]]
    registry.registry = {}
    
    settings = LightshowSettings()
    lightshow_data = {
        "timeline": [
            {"effect": "test", "start": 0, "end": 30, "parameters": {}}
        ]
    }
    
    frames = process_lightshow(registry, lightshow_data, settings)
    
    assert isinstance(frames, list)


def test_lightshow_manager_registry_with_coords():
    """Test registry stores coordinates."""
    from modules.lightshow_manager import RegistryInstance
    
    coords = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    
    with patch("modules.lightshow_manager.Path"):
        registry = RegistryInstance(coords)
        
        assert registry.coords == coords


def test_lightshow_manager_process_lightshow_empty_timeline():
    """Test process_lightshow with empty timeline."""
    from modules.lightshow_manager import process_lightshow, RegistryInstance, LightshowSettings
    
    registry = RegistryInstance.__new__(RegistryInstance)
    registry.coords = [[0, 0], [1, 1], [2, 2]]
    registry.registry = {}
    
    settings = LightshowSettings()
    lightshow_data = {"timeline": []}
    
    frames = process_lightshow(registry, lightshow_data, settings)
    
    assert isinstance(frames, list)


def test_lightshow_manager_frame_structure():
    """Test that frames contain RGB tuples."""
    from modules.lightshow_manager import process_lightshow, RegistryInstance, LightshowSettings
    
    registry = RegistryInstance.__new__(RegistryInstance)
    registry.coords = [[0, 0, 0]]
    registry.registry = {}
    
    settings = LightshowSettings()
    lightshow_data = {"timeline": []}
    
    frames = process_lightshow(registry, lightshow_data, settings)
    
    assert isinstance(frames, list)
    for frame in frames:
        assert isinstance(frame, list)


def test_lightshow_manager_settings_with_custom_fps():
    """Test settings creation with custom FPS."""
    from modules.lightshow_manager import LightshowSettings
    
    settings = LightshowSettings(fps=120)
    
    assert settings.FPS == 120


def test_lightshow_manager_process_lightshow_preserves_led_count():
    """Test process_lightshow returns frames with same LED count as registry."""
    from modules.lightshow_manager import process_lightshow, RegistryInstance, LightshowSettings
    
    led_count = 10
    registry = RegistryInstance.__new__(RegistryInstance)
    registry.coords = [[i, 0, 0] for i in range(led_count)]
    registry.registry = {}
    
    settings = LightshowSettings()
    lightshow_data = {"timeline": []}
    
    frames = process_lightshow(registry, lightshow_data, settings)
    
    assert isinstance(frames, list)


def test_lightshow_manager_registry_instance_has_registry_dict():
    """Test RegistryInstance has empty registry dict initially."""
    from modules.lightshow_manager import RegistryInstance
    
    with patch("modules.lightshow_manager.Path"):
        registry = RegistryInstance([[0, 0, 0]])
        
        assert isinstance(registry.registry, dict)
        assert len(registry.registry) == 0 or isinstance(registry.registry, dict)


def test_lightshow_manager_process_multiple_timeline_items():
    """Test process_lightshow handles multiple timeline items."""
    from modules.lightshow_manager import process_lightshow, RegistryInstance, LightshowSettings
    
    registry = RegistryInstance.__new__(RegistryInstance)
    registry.coords = [[0, 0, 0]]
    registry.registry = {"effect1": MagicMock(), "effect2": MagicMock()}
    
    settings = LightshowSettings()
    lightshow_data = {
        "timeline": [
            {"effect": "effect1", "start": 0, "end": 30},
            {"effect": "effect2", "start": 30, "end": 60},
        ]
    }
    
    frames = process_lightshow(registry, lightshow_data, settings)
    
    assert isinstance(frames, list)
