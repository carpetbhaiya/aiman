import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".config" / "aiman"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "model": "qwen3:14b",
    "host": "http://localhost:11434"
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

HISTORY_FILE = CONFIG_DIR / "history.json"

def get_history() -> list[dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

def append_history(description: str, command: str) -> None:
    history = get_history()
    history.append({"description": description, "command": command})
    # Keep only last 50
    if len(history) > 50:
        history = history[-50:]
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)
