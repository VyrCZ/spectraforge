import pytest
import json
import io

import server

def test_index_page(test_client):
    response = test_client.get('/')
    assert response.status_code == 200

def test_effects_page(test_client):
    response = test_client.get('/effects')
    assert response.status_code == 200

def test_get_state(test_client):
    response = test_client.get('/api/get_state')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "current_effect" in data
    assert "parameters" in data
    assert "effect_type" in data

def test_set_effect_invalid(test_client):
    response = test_client.post('/api/set_effect', json={"effect": "nonexistent_effect_123"})
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["status"] == "error"

def test_get_coords(test_client):
    response = test_client.get('/api/get_coords')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "coords" in data

def test_get_pixels(test_client):
    response = test_client.get('/api/canvas/get_pixels')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "pixels" in data
    
def test_set_pixels_empty(test_client):
    response = test_client.post('/api/canvas/set_pixels', json={"pixels": []})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["status"] == "error"
    assert "Pixel data is required" in data["message"]

def test_sandbox_page(test_client):
    response = test_client.get('/sandbox')
    assert response.status_code == 200

def test_settings_page(test_client):
    response = test_client.get('/settings')
    assert response.status_code == 200
    
def test_get_log(test_client):
    response = test_client.get('/api/get_log')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "logs" in data
    
def test_audio_page(test_client):
    response = test_client.get('/audio')
    assert response.status_code == 200

def test_lightshows_page(test_client):
    response = test_client.get('/lightshows')
    assert response.status_code == 200

def test_get_parameters_success(test_client, monkeypatch):
    monkeypatch.setattr(server.effects_engine, "get_parameters", lambda effect_name: {"speed": {"value": 10}})
    response = test_client.get('/api/get_parameters/rainbow')
    assert response.status_code == 200
    assert response.get_json()["speed"]["value"] == 10

def test_get_parameters_not_found(test_client, monkeypatch):
    monkeypatch.setattr(server.effects_engine, "get_parameters", lambda effect_name: {"error": "Effect not found"})
    response = test_client.get('/api/get_parameters/missing')
    assert response.status_code == 404

def test_set_parameter_success(test_client, monkeypatch):
    monkeypatch.setattr(server.effects_engine, "set_parameter", lambda name, value: {"status": "success"})
    response = test_client.post('/api/set_parameter', json={"name": "speed", "value": 42})
    assert response.status_code == 200
    assert response.get_json()["status"] == "success"

def test_set_parameter_error(test_client, monkeypatch):
    monkeypatch.setattr(server.effects_engine, "set_parameter", lambda name, value: {"status": "error", "message": "Invalid parameter"})
    response = test_client.post('/api/set_parameter', json={"name": "speed", "value": 42})
    assert response.status_code == 400

def test_setup_pages(test_client):
    assert test_client.get('/setup').status_code == 200
    assert test_client.get('/setup/new').status_code == 200
    assert test_client.get('/canvas').status_code == 200
    assert test_client.get('/logs').status_code == 200
    assert test_client.get('/upload').status_code == 200

def test_change_setup_missing_name(test_client):
    response = test_client.post('/api/change_setup', json={})
    assert response.status_code == 400

def test_change_setup_success(test_client, monkeypatch):
    called = {}

    def fake_change_setup(name):
        called["name"] = name

    monkeypatch.setattr(server.manager, "change_setup_by_name", fake_change_setup)
    response = test_client.post('/api/change_setup', json={"name": "test_setup"})
    assert response.status_code == 200
    assert called["name"] == "test_setup"

def test_change_setup_failure(test_client, monkeypatch):
    monkeypatch.setattr(server.manager, "change_setup_by_name", lambda name: (_ for _ in ()).throw(RuntimeError("boom")))
    response = test_client.post('/api/change_setup', json={"name": "bad"})
    assert response.status_code == 500

def test_calibration_new_setup_variants(test_client, monkeypatch):
    response = test_client.post('/api/calibration/new_setup', json={})
    assert response.status_code == 400

    response = test_client.post('/api/calibration/new_setup', json={"name": "x", "type": "4D", "led_count": 10})
    assert response.status_code == 400

    created = {}

    def fake_new_setup(name, setup_type, led_count):
        created["data"] = (name, setup_type.value, led_count)

    monkeypatch.setattr(server.calibration_engine, "new_setup", fake_new_setup)
    response = test_client.post('/api/calibration/new_setup', json={"name": "x", "type": "2D", "led_count": 10})
    assert response.status_code == 200
    assert created["data"] == ("x", "2D", 10)

    monkeypatch.setattr(server.calibration_engine, "new_setup", lambda *args: (_ for _ in ()).throw(RuntimeError("nope")))
    response = test_client.post('/api/calibration/new_setup', json={"name": "x", "type": "2D", "led_count": 10})
    assert response.status_code == 500

def test_calibration_show_pixel_variants(test_client, monkeypatch):
    response = test_client.post('/api/calibration/show_pixel', json={})
    assert response.status_code == 400

    seen = {}

    def fake_show_pixel(index, color):
        seen["data"] = (index, color)

    monkeypatch.setattr(server.calibration_engine, "show_pixel", fake_show_pixel, raising=False)
    response = test_client.post('/api/calibration/show_pixel', json={"index": 1, "color": [255, 0, 0]})
    assert response.status_code == 200
    assert seen["data"] == (1, [255, 0, 0])

    monkeypatch.setattr(server.calibration_engine, "show_pixel", lambda *args: (_ for _ in ()).throw(RuntimeError("bad pixel")), raising=False)
    response = test_client.post('/api/calibration/show_pixel', json={"index": 1, "color": [255, 0, 0]})
    assert response.status_code == 500

def test_upload_pixel_image_variants(test_client, monkeypatch):
    response = test_client.post('/api/calibration/upload_pixel_image', data={})
    assert response.status_code == 400

    uploaded = {}

    def fake_upload_pixel_image(index, image):
        uploaded["data"] = (index, image.filename)

    monkeypatch.setattr(server.calibration_engine, "upload_pixel_image", fake_upload_pixel_image, raising=False)
    response = test_client.post(
        '/api/calibration/upload_pixel_image',
        data={"index": "2", "image": (io.BytesIO(b"img"), "pixel.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert uploaded["data"] == (2, "pixel.png")

def test_set_pixels_success_and_failure(test_client, monkeypatch):
    pixels = [[0, 0, 0]] * len(server.canvas_engine.renderer)
    called = {}

    def fake_set_pixels(pixel_list):
        called["pixels"] = pixel_list

    monkeypatch.setattr(server.canvas_engine, "set_pixels", fake_set_pixels)
    response = test_client.post('/api/canvas/set_pixels', json={"pixels": pixels})
    assert response.status_code == 200
    assert called["pixels"] == pixels

    monkeypatch.setattr(server.canvas_engine, "set_pixels", lambda pixel_list: (_ for _ in ()).throw(RuntimeError("canvas failed")))
    response = test_client.post('/api/canvas/set_pixels', json={"pixels": pixels})
    assert response.status_code == 500

def test_sandbox_set_file_variants(test_client, monkeypatch):
    response = test_client.post('/api/sandbox/set_file', json={})
    assert response.status_code == 400

    selected = {}

    def fake_set_file(file_name):
        selected["name"] = file_name

    monkeypatch.setattr(server.sandbox_engine, "set_file", fake_set_file)
    response = test_client.post('/api/sandbox/set_file', json={"file_name": "clock.py"})
    assert response.status_code == 200
    assert selected["name"] == "clock.py"

    monkeypatch.setattr(server.sandbox_engine, "set_file", lambda file_name: (_ for _ in ()).throw(RuntimeError("sandbox failed")))
    response = test_client.post('/api/sandbox/set_file', json={"file_name": "clock.py"})
    assert response.status_code == 500

def test_settings_set_setting_variants(test_client, monkeypatch):
    response = test_client.post('/api/settings/set_setting', json={"invalid": 1})
    assert response.status_code == 400

    calls = {}

    def fake_set_brightness(value):
        calls["brightness"] = value

    monkeypatch.setattr(server.renderer, "set_brightness", fake_set_brightness)
    response = test_client.post('/api/settings/set_setting', json={"brightness": 50})
    assert response.status_code == 200
    assert calls["brightness"] == 0.5

    monkeypatch.setattr(server.Config, "save", lambda self: None)
    response = test_client.post('/api/settings/set_setting', json={"performance_mode": "low"})
    assert response.status_code == 200
    assert server.Config().config["performance_mode"] == "low"

    response = test_client.post('/api/settings/set_setting', json={"enhance_colors": False})
    assert response.status_code == 200
    assert server.Config().config["enhance_colors"] is False

def test_media_listing_routes(test_client, monkeypatch):
    def fake_listdir(path):
        if path.endswith('audio'):
            return ["song.mp3", "voice.wav", "ignore.txt"]
        if path.endswith('images'):
            return ["pic.png", "photo.jpg", "skip.txt"]
        if path.endswith('videos'):
            return ["clip.mp4", "movie.mkv", "skip.txt"]
        return []

    monkeypatch.setattr(server.os, "listdir", fake_listdir)
    assert test_client.get('/api/audio/get_audio_files').get_json()["files"] == ["song.mp3", "voice.wav"]
    assert test_client.get('/api/get_image_files').get_json()["files"] == ["pic.png", "photo.jpg"]
    assert test_client.get('/api/get_video_files').get_json()["files"] == ["clip.mp4", "movie.mkv"]

def test_media_listing_errors(test_client, monkeypatch):
    monkeypatch.setattr(server.os, "listdir", lambda path: (_ for _ in ()).throw(OSError("missing")))
    assert test_client.get('/api/audio/get_audio_files').status_code == 500
    assert test_client.get('/api/get_image_files').status_code == 500
    assert test_client.get('/api/get_video_files').status_code == 500

def test_display_image_variants(test_client, monkeypatch):
    response = test_client.post('/api/display_image', json={})
    assert response.status_code == 400

    called = {}

    def fake_display_image(path):
        called["path"] = path

    monkeypatch.setattr(server.image_engine, "display_image", fake_display_image)
    response = test_client.post('/api/display_image', json={"image_file": "demo.png"})
    assert response.status_code == 200
    assert called["path"].endswith("media\\images\\demo.png") or called["path"].endswith("media/images/demo.png")

    monkeypatch.setattr(server.image_engine, "display_image", lambda path: (_ for _ in ()).throw(RuntimeError("bad image")))
    response = test_client.post('/api/display_image', json={"image_file": "demo.png"})
    assert response.status_code == 500

def test_file_delivery_routes(test_client, monkeypatch):
    monkeypatch.setattr(server, "send_from_directory", lambda directory, filename, **kwargs: server.app.response_class(f"{directory}|{filename}", mimetype="text/plain"))
    assert test_client.get('/favicon.ico').status_code == 200
    assert test_client.get('/locales/en.json').status_code == 200
    assert test_client.get('/audio/song.mp3').status_code == 200
    assert test_client.get('/video/movie.mp4').status_code == 200
    assert test_client.get('/video_audio/movie.mp4.mp3').status_code == 200

def test_upload_api_variants(test_client, monkeypatch):
    response = test_client.post('/api/upload', data={}, content_type="multipart/form-data")
    assert response.status_code == 400

    monkeypatch.setattr(server.upload, "handle_file_upload", lambda files: True)
    response = test_client.post(
        '/api/upload',
        data={"files": (io.BytesIO(b"hello"), "test.txt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.get_json()["success"] is True
