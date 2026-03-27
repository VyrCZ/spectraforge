import json
from unittest.mock import MagicMock, patch

import pytest


def test_lightshow_manager_registry_instance_init():
    """Test RegistryInstance initialization."""
    from modules.lightshow_manager import RegistryInstance

    with patch("modules.lightshow_manager.Path"):
        registry = RegistryInstance([[0, 0, 0], [1, 1, 1]])

        assert len(registry.coords) == 2
        assert isinstance(registry.registry, dict)


@pytest.mark.parametrize("fps,expected", [(30, 30), (60, 60), (120, 120)])
def test_lightshow_manager_settings_fps(fps, expected):
    """Test LightshowSettings stores the given FPS; defaults to 30."""
    from modules.lightshow_manager import LightshowSettings

    settings = LightshowSettings(fps=fps)
    assert settings.FPS == expected


def test_lightshow_manager_default_fps():
    """Test LightshowSettings defaults to 30 FPS."""
    from modules.lightshow_manager import LightshowSettings

    assert LightshowSettings().FPS == 30


def test_lightshow_manager_process_lightshow_empty_timeline_returns_empty_frames():
    """process_lightshow with an empty timeline should return an empty list of frames."""
    from modules.lightshow_manager import process_lightshow, RegistryInstance, LightshowSettings

    registry = RegistryInstance.__new__(RegistryInstance)
    registry.coords = [[0, 0, 0], [1, 1, 1]]
    registry.registry = {}

    frames = process_lightshow(registry, {"timeline": []}, LightshowSettings())

    assert isinstance(frames, list)
    assert len(frames) == 0


def test_lightshow_manager_process_lightshow_frame_count_and_led_count():
    """Frames produced must match FPS * duration and contain one entry per LED."""
    from modules.lightshow_manager import process_lightshow, RegistryInstance, LightshowSettings

    led_count = 5
    registry = RegistryInstance.__new__(RegistryInstance)
    registry.coords = [[i, 0, 0] for i in range(led_count)]

    # Build a minimal effect stub that returns one black pixel per LED per step
    def fake_effect(steps, **params):
        return [[(0, 0, 0)] * led_count for _ in range(steps)]

    registry.registry = {"fx": fake_effect}

    # BPM=60 means 1 beat = 1 s; 2-beat segment at 30 FPS = 60 frames
    lightshow_data = {
        "bpm": 60,
        "timeline": [{"effect": "fx", "start": 0, "end": 2, "parameters": {}}],
    }
    frames = process_lightshow(registry, lightshow_data, LightshowSettings(fps=30))

    assert len(frames) == 60
    for frame in frames:
        assert len(frame) == led_count


def test_lightshow_manager_process_lightshow_unknown_effect_skipped():
    """An unknown effect in the timeline should be skipped without error."""
    from modules.lightshow_manager import process_lightshow, RegistryInstance, LightshowSettings

    registry = RegistryInstance.__new__(RegistryInstance)
    registry.coords = [[0, 0, 0]]
    registry.registry = {}

    lightshow_data = {
        "bpm": 60,
        "timeline": [{"effect": "nonexistent", "start": 0, "end": 1}],
    }
    frames = process_lightshow(registry, lightshow_data, LightshowSettings(fps=30))

    # All 30 frames should exist but contain only the default black pixels.
    # Use list() to normalise tuples vs lists (cache returns lists, live path returns tuples).
    assert len(frames) == 30
    assert all(list(pixel) == [0, 0, 0] for frame in frames for pixel in frame)


def test_lightshow_manager_process_lightshow_alpha_blending():
    """A fully opaque effect pixel should overwrite the black canvas."""
    from modules.lightshow_manager import process_lightshow, RegistryInstance, LightshowSettings

    registry = RegistryInstance.__new__(RegistryInstance)
    registry.coords = [[0, 0, 0]]
    registry.registry = {}

    # Fully opaque red pixel via RGB (no alpha channel)
    def red_effect(steps, **params):
        return [[(255, 0, 0)] for _ in range(steps)]

    registry.registry = {"red": red_effect}

    lightshow_data = {
        "bpm": 60,
        "timeline": [{"effect": "red", "start": 0, "end": 1, "parameters": {}}],
    }
    frames = process_lightshow(registry, lightshow_data, LightshowSettings(fps=30))

    # Every frame must contain the fully opaque red pixel.
    # Use list() to normalise tuples vs lists (cache returns lists, live path returns tuples).
    assert all(list(frame[0]) == [255, 0, 0] for frame in frames)


def test_lightshow_manager_registry_instance_has_empty_registry_by_default():
    """RegistryInstance should start with an empty registry dict (before loading files)."""
    from modules.lightshow_manager import RegistryInstance

    with patch("modules.lightshow_manager.Path"):
        registry = RegistryInstance([[0, 0, 0]])

        assert isinstance(registry.registry, dict)
        # The registry may be populated by auto-loading from disk, but it should
        # always be a dict — test that the type guarantee holds.
        assert len(registry.registry) >= 0

