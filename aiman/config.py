import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".config" / "aiman"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "model": "qwen3:14b",
    "host": "http://172.18.224.1:11434"
}

def load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r") as f:
            user_config = json.load(f)
            # Merge with defaults to ensure all keys exist
            config = DEFAULT_CONFIG.copy()
            if isinstance(user_config, dict):
                config.update(user_config)
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
