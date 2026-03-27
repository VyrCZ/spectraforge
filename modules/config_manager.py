import json
import os
from json import JSONDecodeError
from modules.log_manager import Log

class Config:
    _instance = None
    CONFIG_PATH = "config/server_config.json"
    _DEFAULT_CONFIG = {"current_setup": ""}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._init_once(*args, **kwargs)
        return cls._instance

    def _init_once(self, *args, **kwargs):
        self.config = {}
        self.load()

    def load(self):
        os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)

        if not os.path.exists(self.CONFIG_PATH):
            self.config = dict(self._DEFAULT_CONFIG)
            self.save()
            return

        try:
            with open(self.CONFIG_PATH, "r", encoding="utf-8") as file:
                text = file.read()

            if not text.strip():
                raise JSONDecodeError("Empty config file", text, 0)

            self.config = json.loads(text)
            Log.info("Config", "Configuration loaded successfully.")
        except JSONDecodeError as e:
            Log.warn("Config", f"Config load failed (keeping previous): {e}")

    def save(self):
        Log.info("Config", "Saving configuration...")
        os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)
        with open(self.CONFIG_PATH, "w", encoding="utf-8") as file:
            json.dump(self.config, file, indent=4)