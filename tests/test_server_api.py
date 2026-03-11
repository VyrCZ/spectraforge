import pytest
import json

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
