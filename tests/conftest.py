import os
import sys
import pytest

# Add the project root to the PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.led_renderer import DummyRenderer
from modules.setup import Setup, SetupType
from server import app, socketio

@pytest.fixture
def mock_setup():
    return Setup("test_setup", SetupType.TWO_DIMENSIONAL, [(0,0,0)]*10)

@pytest.fixture
def dummy_renderer(mock_setup):
    return DummyRenderer(mock_setup)

@pytest.fixture
def test_client():
    app.config.update({"TESTING": True})
    with app.test_client() as client:
        yield client

@pytest.fixture
def socket_client(test_client):
    return socketio.test_client(app, flask_test_client=test_client)
