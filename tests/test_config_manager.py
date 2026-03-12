import json

from modules.config_manager import Config


def reset_config_singleton(tmp_path, monkeypatch):
    Config._instance = None
    monkeypatch.setattr(Config, "CONFIG_PATH", str(tmp_path / "server_config.json"))


def test_config_load_missing_file_creates_default(tmp_path, monkeypatch):
    reset_config_singleton(tmp_path, monkeypatch)
    config = Config()
    assert config.config == {"current_setup": ""}
    assert (tmp_path / "server_config.json").exists()


def test_config_save_and_reload(tmp_path, monkeypatch):
    reset_config_singleton(tmp_path, monkeypatch)
    config = Config()
    config.config = {"current_setup": "tree", "brightness": 0.5}
    config.save()

    Config._instance = None
    monkeypatch.setattr(Config, "CONFIG_PATH", str(tmp_path / "server_config.json"))
    loaded = Config()
    assert loaded.config["current_setup"] == "tree"
    assert loaded.config["brightness"] == 0.5


def test_config_load_invalid_json_keeps_previous_value(tmp_path, monkeypatch):
    reset_config_singleton(tmp_path, monkeypatch)
    config = Config()
    config.config = {"current_setup": "tree"}
    (tmp_path / "server_config.json").write_text("{bad json", encoding="utf-8")
    monkeypatch.setattr("modules.config_manager.time.sleep", lambda seconds: None)
    config.load(retries=2, delay_s=0)
    assert config.config == {"current_setup": "tree"}


def test_config_save_writes_json_file(tmp_path, monkeypatch):
    reset_config_singleton(tmp_path, monkeypatch)
    config = Config()
    config.config = {"current_setup": "tree"}
    config.save()
    written = json.loads((tmp_path / "server_config.json").read_text(encoding="utf-8"))
    assert written == {"current_setup": "tree"}