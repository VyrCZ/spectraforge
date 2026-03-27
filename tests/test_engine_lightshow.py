import pytest
import os
import json
from unittest.mock import patch, MagicMock, mock_open

from modules.engine_lightshow import LightshowEngine
from modules.engine_manager import EngineManager

@pytest.fixture
def lightshow_engine(dummy_renderer, mock_setup):
    manager = EngineManager()
    engine = LightshowEngine(dummy_renderer, mock_setup, lambda x: None)
    manager.register_audio_engine(engine)
    manager.active_engine = engine
    return engine

@patch('os.path.exists', return_value=True)
@patch('os.listdir')
@patch('builtins.open')
def test_get_lightshow_file_data(mock_open, mock_listdir, mock_exists, lightshow_engine):
    mock_listdir.side_effect = [
        ["song1.mp3", "song2.wav"], # audio folder contents
        ["valid_show.json", "missing_audio.json", "invalid.json"] # lightshow folder contents
    ]

    valid_json = '{"audio_file": "song1.mp3", "timeline": [{"effect": "rainbow"}]}'
    missing_json = '{"audio_file": "missing.mp3", "timeline": []}'

    # Mocking open for multiple files — use os.path.join for cross-platform paths
    def mocked_open(filename, *args, **kwargs):
        norm_path = os.path.normpath(filename)
        if norm_path == os.path.normpath(os.path.join('lightshows', 'valid_show.json')):
            content = valid_json
        elif norm_path == os.path.normpath(os.path.join('lightshows', 'missing_audio.json')):
            content = missing_json
        else:
            content = '{}'
        m = MagicMock()
        m.__enter__ = lambda x: MagicMock(read=lambda: content, **{"__iter__": lambda s: iter([content])})
        m.read = lambda: content
        return m
        
    mock_open.side_effect = mocked_open
    
    # Needs registry to be mocked 
    lightshow_engine.registry = MagicMock()
    lightshow_engine.registry.registry = {"rainbow": MagicMock()}

    data = lightshow_engine.get_lightshow_file_data()
    
    assert "valid_show" in data
    assert data["valid_show"]["audio_file"] == "song1.mp3"
    assert "audio_file_missing" not in data["valid_show"]["effect_issues"]
    
    assert "missing_audio" in data
    assert data["missing_audio"]["effect_issues"].get("audio_file_missing") is True

@patch('modules.engine_lightshow.process_lightshow')
def test_compile_lightshow(mock_process, lightshow_engine):
    mock_process.return_value = [((255, 0, 0),) * 10] * 30 # 30 frames
    
    mock_json = '{"audio_file": "test.mp3", "timeline": []}'
    with patch('builtins.open', mock_open(read_data=mock_json)):
        audio_file = lightshow_engine.compile_lightshow("dummy_path.json")
        
    assert audio_file == "test.mp3"
    assert lightshow_engine.audio_length == 1.0 # 30 frames / 30 FPS
    assert len(lightshow_engine.frames) == 30

def test_engine_callbacks(lightshow_engine):
    assert lightshow_engine.lightshow_data is None
    lightshow_engine.on_enable()
    # on_enable logs but should not alter pre-loaded state
    assert lightshow_engine.lightshow_data is None
    assert lightshow_engine.audio_length == 0.0

    lightshow_engine.on_disable()
    # on_disable logs but should not alter state when no audio is loaded
    assert lightshow_engine.audio_length == 0.0

@patch('modules.engine_lightshow.LightshowEngine.compile_lightshow')
def test_on_audio_load(mock_compile, lightshow_engine):
    mock_compile.return_value = "prepared_audio.mp3"
    lightshow_engine.frames = [((0, 0, 0),)] * 30
    lightshow_engine.FPS = 30
    lightshow_engine.audio_length = 1.0
    
    var_called = False
    def ready_callback(path):
        nonlocal var_called
        var_called = True
        assert path == "prepared_audio.mp3"
        
    lightshow_engine.ready_callback = ready_callback
    lightshow_engine.on_audio_load("unprepared_audio.mp3")
    assert var_called is True
