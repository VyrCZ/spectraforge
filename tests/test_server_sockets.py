import pytest

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
