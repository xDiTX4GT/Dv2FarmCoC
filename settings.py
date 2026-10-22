import json
import os

from utils import is_frozen, resource_path, user_path

SETTINGS_PATH = user_path("settings.json")
# Shipped inside the bundle; used to seed a fresh install.
DEFAULT_SETTINGS_RESOURCE = "settings.json"


def _seed_default_settings():
    """Copy the bundled default settings into the user data dir (once)."""
    if not is_frozen() or os.path.exists(SETTINGS_PATH):
        return
    try:
        with open(resource_path(DEFAULT_SETTINGS_RESOURCE), "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            save_settings(data)
    except (OSError, ValueError):
        pass


def load_settings():
    """Read settings.json. Returns an empty dict if missing or unreadable."""
    _seed_default_settings()
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (OSError, ValueError):
        pass
    return {}


def save_settings(data):
    """Write settings.json. Returns True on success, False on failure."""
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except OSError:
        return False
