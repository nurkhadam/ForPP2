import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

DEFAULT_SETTINGS = {
    "sound":       False,
    "car_color":   "blue",
    "difficulty":  "normal",   # "easy" | "normal" | "hard"
    "username":    "",
}

# ── Leaderboard ────────────────────────────────────────────────────────────────

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_leaderboard(entries: list):
    """Keep only the top 10 entries sorted by score descending."""
    entries.sort(key=lambda e: e.get("score", 0), reverse=True)
    top = entries[:10]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(top, f, ensure_ascii=False, indent=2)


def add_leaderboard_entry(username: str, score: int, distance: int, coins: int):
    entries = load_leaderboard()
    new_entry = {"name": username, "score": score, "distance": distance, "coins": coins}

    for i, e in enumerate(entries):
        if e.get("name", "").lower() == username.lower():
            if score > e.get("score", 0):
                entries[i] = new_entry
                save_leaderboard(entries)  # сохраняем обновлённый рекорд
            return  # если счёт хуже — просто выходим

    entries.append(new_entry)
    save_leaderboard(entries)


# ── Settings ───────────────────────────────────────────────────────────────────

def load_settings() -> dict:
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Fill missing keys with defaults
        result = DEFAULT_SETTINGS.copy()
        result.update({k: v for k, v in data.items() if k in DEFAULT_SETTINGS})
        return result
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)