import json
from modules.log_manager import Log
import os

class Config:
    _instance = None
    CONFIG_PATH = "config/server_config.json"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._init_once(*args, **kwargs)
        return cls._instance

    def _init_once(self, *args, **kwargs):
        self.config = {}
        self.load()

    def load(self):
        if not os.path.exists(Config.CONFIG_PATH):
            base_data = '{"current_setup": ""}'
            with open(self.CONFIG_PATH, "+w") as file:
                file.write(base_data)
        with open(self.CONFIG_PATH, 'r') as file:
            self.config = json.load(file)
            Log.info("Config", "Configuration loaded successfully.")
        

    def save(self):
        with open(self.CONFIG_PATH, 'w') as file:
            json.dump(self.config, file, indent=4)