# ─────────────────────────────────────────────────────────────────────────────
# settings.py  — Load / save user preferences to settings.json
# Preferences: snake_color (RGB), grid_overlay (bool), sound (bool), db config
# ─────────────────────────────────────────────────────────────────────────────

import json        # built-in module for reading/writing JSON files
import os
from config import (
    SETTINGS_FILE,
    DEFAULT_SNAKE_HEAD, DEFAULT_SNAKE_BODY, DEFAULT_SNAKE_OUTLINE,
    DB_DEFAULTS,
)

# ── Default settings written to disk when no settings.json exists yet ─────────
_DEFAULT_SETTINGS = {
    "snake_head_color":    list(DEFAULT_SNAKE_HEAD),     # [R, G, B]
    "snake_body_color":    list(DEFAULT_SNAKE_BODY),
    "snake_outline_color": list(DEFAULT_SNAKE_OUTLINE),
    "grid_overlay":        True,     # show faint grid lines in the arena
    "sound":               True,     # play sound effects
    "db": {                          # database connection overrides
        "host":     DB_DEFAULTS["host"],
        "port":     DB_DEFAULTS["port"],
        "dbname":   DB_DEFAULTS["dbname"],
        "user":     DB_DEFAULTS["user"],
        "password": DB_DEFAULTS["password"],
    },
}


def load() -> dict:
    """Read settings.json and return a settings dict.

    If the file doesn't exist or is corrupted, write and return defaults.
    Missing individual keys are filled in from defaults (forward-compatible).
    """
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)   # parse JSON → Python dict
            # Merge: start with defaults, then overwrite with saved values
            # This way new keys added to defaults appear automatically.
            merged = {**_DEFAULT_SETTINGS, **data}
            # Also merge nested "db" sub-dict
            merged["db"] = {**_DEFAULT_SETTINGS["db"], **data.get("db", {})}
            return merged
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Settings] Failed to read {SETTINGS_FILE}: {e} — using defaults")

    # No file found or parse failed → create fresh defaults and save them
    save(_DEFAULT_SETTINGS)
    return dict(_DEFAULT_SETTINGS)


def save(settings: dict) -> None:
    """Write the settings dict to settings.json with pretty formatting."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as fh:
            json.dump(settings, fh, indent=4)   # indent=4 → human-readable JSON
    except IOError as e:
        print(f"[Settings] Failed to write {SETTINGS_FILE}: {e}")


def snake_colors(settings: dict) -> tuple:
    """Extract the three snake color tuples from settings.

    Returns (head_color, body_color, outline_color) as RGB tuples.
    """
    head    = tuple(settings.get("snake_head_color",    DEFAULT_SNAKE_HEAD))
    body    = tuple(settings.get("snake_body_color",    DEFAULT_SNAKE_BODY))
    outline = tuple(settings.get("snake_outline_color", DEFAULT_SNAKE_OUTLINE))
    return head, body, outline