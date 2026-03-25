import pytest

import server

def test_socket_connection(socket_client):
    assert socket_client.is_connected() is True

def test_audio_client_connected_no_file(socket_client):
    socket_client.emit('audio_client_connected', {})
    received = socket_client.get_received()
    
    # Needs to match 'audio_error' emitted event when missing file
    assert len(received) > 0
    error_event = next((evt for evt in received if evt['name'] == 'audio_error'), None)
    assert error_event is not None
    assert error_event['args'][0]['status'] == 'error'

def test_lightshow_client_connected_no_file(socket_client):
    socket_client.emit('lightshow_client_connected', {})
    received = socket_client.get_received()
    
    assert len(received) > 0
    error_event = next((evt for evt in received if evt['name'] == 'lightshow_error'), None)
    assert error_event is not None
    assert error_event['args'][0]['status'] == 'error'

def test_video_client_connected_no_file(socket_client):
    socket_client.emit('video_client_connected', {})
    received = socket_client.get_received()
    
    assert len(received) > 0
    error_event = next((evt for evt in received if evt['name'] == 'video_error'), None)
    assert error_event is not None
    assert error_event['args'][0]['status'] == 'error'

def test_audio_controls(socket_client):
    from server import manager, visualiser_engine
    
    # Needs an audio engine to be active
    manager.active_engine = visualiser_engine

    socket_client.emit('audio_play')
    socket_client.emit('audio_pause')
    socket_client.emit('audio_stop')
    socket_client.emit('audio_seek', {"time": 10})
    # These events trigger methods in the active engine but don't emit back directly unless mocked.
    # We mainly test that the socket event doesn't crash the server.
    received = socket_client.get_received()
    # verify no errors came back (this depends on your engine manager mock/setup state)
    error_events = [evt for evt in received if 'error' in evt['name']]
    assert len(error_events) == 0

def test_photo_start(socket_client):
    socket_client.emit('photo_start')
    # Depending on how fast the calibration_engine triggers, take_photo might not be emitted instantly without an ongoing mock.
    # Mainly checking for no crashes.
    received = socket_client.get_received()
    error_events = [evt for evt in received if 'error' in evt['name']]
    assert len(error_events) == 0

def test_led_position_error(socket_client):
    socket_client.emit('led_position', {}) # Missing x, y
    received = socket_client.get_received()
    
    error_event = next((evt for evt in received if evt['name'] == 'led_position_error'), None)
    assert error_event is not None
    assert error_event['args'][0]['status'] == 'error'
    assert 'X and Y coordinates are required' in error_event['args'][0]['message']

def test_photo_data_forwarded(socket_client, monkeypatch):
    captured = {}

    def fake_receive_photo_data(data):
        captured["data"] = data

    monkeypatch.setattr(server.calibration_engine, "receive_photo_data", fake_receive_photo_data)
    socket_client.emit('photo_data', {"image": "abc"})
    assert captured["data"] == {"image": "abc"}

def test_led_position_success(socket_client, monkeypatch):
    captured = {}

    def fake_receive_image_position(x, y, z=None):
        captured["data"] = (x, y, z)

    monkeypatch.setattr(server.calibration_engine, "receive_image_position", fake_receive_image_position)
    socket_client.emit('led_position', {"x": 1, "y": 2})
    assert captured["data"] == (1, 2, None)

def test_client_connected_success_paths(socket_client, monkeypatch):
    captured = {}

    monkeypatch.setattr(server.visualiser_engine, "on_audio_load", lambda audio_file: captured.setdefault("audio", audio_file))
    monkeypatch.setattr(server.lightshow_engine, "on_audio_load", lambda lightshow_file: captured.setdefault("lightshow", lightshow_file))
    monkeypatch.setattr(server.video_engine, "on_audio_load", lambda video_file: captured.setdefault("video", video_file))

    socket_client.emit('audio_client_connected', {"audio_file": "song.mp3"})
    socket_client.emit('lightshow_client_connected', {"lightshow_file": "show.json"})
    socket_client.emit('video_client_connected', {"video_file": "clip.mp4"})

    assert captured == {
        "audio": "song.mp3",
        "lightshow": "show.json",
        "video": "clip.mp4",
    }

def test_audio_engine_ready_emits(monkeypatch):
    payloads = []
    monkeypatch.setattr(server.socketio, "emit", lambda event, payload=None: payloads.append((event, payload)))
    server.audio_engine_ready("song.mp3")
    assert payloads == [("audio_ready", {"audio_file": "song.mp3"})]
