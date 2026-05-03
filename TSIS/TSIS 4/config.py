# ─────────────────────────────────────────────────────────────────────────────
# config.py  — Central configuration: grid sizes, colors, speed, food types
# All game-wide constants live here so every module can import from one place.
# ─────────────────────────────────────────────────────────────────────────────

# ── Grid / Window geometry ────────────────────────────────────────────────────
CELL    = 20          # pixel width/height of one grid cell
COLS    = 25          # number of columns in the play field
ROWS    = 25          # number of rows in the play field
PANEL_H = 50          # pixel height of the top HUD bar
WIDTH   = COLS * CELL                   # window width  = 500 px
HEIGHT  = ROWS * CELL + PANEL_H         # window height = 550 px

# ── Frames-per-second and movement timing ────────────────────────────────────
BASE_FPS  = 60    # target refresh rate  (pygame clock.tick target)
BASE_MOVE = 15    # frames between snake steps at the start  (lower = faster)
MIN_MOVE  = 3     # hard minimum: snake can never go faster than this

# ── Level progression ─────────────────────────────────────────────────────────
FOOD_PER_LEVEL    = 4    # how many food items must be eaten to advance one level
OBSTACLES_START_LEVEL = 3   # obstacles begin appearing from this level
MAX_OBSTACLES     = 12   # absolute cap on obstacle blocks in the arena

# ── Obstacle count formula: base + 2 per level above threshold ───────────────
def obstacle_count(level: int) -> int:
    """Return number of obstacle blocks for the given level (0 before level 3)."""
    if level < OBSTACLES_START_LEVEL:
        return 0
    return min(MAX_OBSTACLES, (level - OBSTACLES_START_LEVEL + 1) * 2 + 2)

# ── Color palette (RGB tuples) ────────────────────────────────────────────────
BG_COLOR       = ( 15,  15,  15)   # very dark background
GRID_COLOR     = ( 30,  30,  30)   # subtle grid lines
WALL_COLOR     = ( 80,  80,  80)   # border walls
OBSTACLE_COLOR = ( 90,  60,  30)   # brownish obstacle blocks
TEXT_COLOR     = (255, 255, 255)   # white text
GOLD           = (255, 215,   0)   # score / legendary food
RED            = (220,  30,  30)   # game-over text
SILVER         = (192, 192, 192)   # secondary info
ORANGE         = (255, 140,   0)   # uncommon food
PURPLE         = (180,  50, 220)   # rare food
DARK_RED       = (140,  10,  10)   # poison food
PANEL_BG       = ( 20,  20,  40)   # HUD panel background

# Default snake colors — can be overridden by settings.json
DEFAULT_SNAKE_HEAD = ( 50, 220,  50)
DEFAULT_SNAKE_BODY = ( 30, 160,  30)
DEFAULT_SNAKE_OUTLINE = ( 10,  90,  10)

# ── Food type table ───────────────────────────────────────────────────────────
# Each entry is a dict with:
#   label    — character shown inside the food circle
#   value    — score points awarded on eat
#   color    — fill color of the circle
#   shine    — highlight dot color
#   weight   — relative spawn probability (higher = more common)
#   lifetime — seconds until it vanishes; None means it never disappears
FOOD_TYPES = [
    {
        "label":    "1",
        "value":    1,
        "color":    (220,  50,  50),      # common red food — never disappears
        "shine":    (255, 120, 120),
        "weight":   50,
        "lifetime": None,
    },
    {
        "label":    "2",
        "value":    2,
        "color":    ORANGE,               # uncommon orange — 6 s lifetime
        "shine":    (255, 190, 100),
        "weight":   30,
        "lifetime": 6.0,
    },
    {
        "label":    "3",
        "value":    3,
        "color":    PURPLE,               # rare purple — 4 s lifetime
        "shine":    (220, 130, 255),
        "weight":   15,
        "lifetime": 4.0,
    },
    {
        "label":    "5",
        "value":    5,
        "color":    GOLD,                 # legendary gold — 3 s lifetime
        "shine":    (255, 240, 100),
        "weight":   5,
        "lifetime": 3.0,
    },
]

# Build a flat weighted list once at import time so random.choice() is O(1)
FOOD_POOL = []
for _ft in FOOD_TYPES:
    FOOD_POOL.extend([_ft] * _ft["weight"])   # repeat each type by its weight

# ── Power-up definitions ──────────────────────────────────────────────────────
# effect_duration  — how long the effect lasts after collection (ms)
# field_lifetime   — how long it sits on the field before disappearing (ms)
POWERUP_TYPES = [
    {
        "kind":             "speed_boost",
        "label":            "⚡",           # lightning bolt shown on item
        "color":            (255, 220,  30),
        "shine":            (255, 255, 150),
        "effect_duration":  5000,            # 5 seconds of speed boost
        "field_lifetime":   8000,            # vanishes from field after 8 s
    },
    {
        "kind":             "slow_motion",
        "label":            "🐢",
        "color":            (100, 200, 255),
        "shine":            (180, 230, 255),
        "effect_duration":  5000,
        "field_lifetime":   8000,
    },
    {
        "kind":             "shield",
        "label":            "🛡",
        "color":            (180, 255, 180),
        "shine":            (220, 255, 220),
        "effect_duration":  0,               # lasts until triggered (one use)
        "field_lifetime":   8000,
    },
]

# ── Database connection parameters ───────────────────────────────────────────
# These defaults match a typical local PostgreSQL dev install.
# The user can override them in settings.json under key "db".
DB_DEFAULTS = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "snake_game",
    "user":     "postgres",
    "password": "0000",
}

# ── Settings file path ────────────────────────────────────────────────────────
import os
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")   # written/read next to the executable