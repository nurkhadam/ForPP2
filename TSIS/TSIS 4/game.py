# ─────────────────────────────────────────────────────────────────────────────
# game.py  — Core game objects: Snake, Food, PoisonFood, PowerUp, Obstacle
#            Plus all drawing helpers: draw_field, draw_hud, sound manager.
# This module is imported by main.py; it never runs a game loop on its own.
# ─────────────────────────────────────────────────────────────────────────────

import pygame
import random
import sys
import os

# Resolve the directory where game.py lives so asset paths work regardless
# of which folder the user runs `python main.py` from.
_HERE = os.path.dirname(os.path.abspath(__file__))

from config import (
    CELL, COLS, ROWS, PANEL_H, WIDTH, HEIGHT,
    BASE_FPS, BASE_MOVE, MIN_MOVE,
    BG_COLOR, GRID_COLOR, WALL_COLOR, OBSTACLE_COLOR, TEXT_COLOR,
    GOLD, RED, SILVER, ORANGE, DARK_RED, PANEL_BG,
    DEFAULT_SNAKE_HEAD, DEFAULT_SNAKE_BODY, DEFAULT_SNAKE_OUTLINE,
    FOOD_POOL, POWERUP_TYPES,
)

# ──────────────────────────────────────────────
# Initialize pygame subsystems
# ──────────────────────────────────────────────
pygame.init()
# channels=2 → stereo output (required by most audio drivers even for mono WAVs)
# buffer=1024 → slightly larger buffer reduces underrun glitches
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

# ──────────────────────────────────────────────
# Shared pygame objects (created once, reused everywhere)
# ──────────────────────────────────────────────
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake — TSIS 4")
clock  = pygame.time.Clock()    # used to cap FPS and measure frame time

# Font hierarchy: large for titles, medium for HUD, small for labels
font_large  = pygame.font.SysFont("Consolas", 40, bold=True)
font_medium = pygame.font.SysFont("Consolas", 24, bold=True)
font_small  = pygame.font.SysFont("Consolas", 16)


# ──────────────────────────────────────────────
# SOUND MANAGER
# ──────────────────────────────────────────────

# Sound file names (keys used in play() calls throughout the game)
_SOUND_FILES = {
    "eat":      "eat.wav",
    "levelup":  "levelup.wav",
    "gameover": "gameover.wav",
    "powerup":  "powerup.wav",
    "poison":   "poison.wav",
    "shield":   "shield.wav",
    "click":    "click.wav",
}

def _find_assets_dir() -> str:
    """Search multiple candidate folders to find the WAV files.

    Checks assets/sounds/ first (user's actual layout), then assets/ as fallback.
    Works regardless of which directory python is launched from.
    """
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    candidates = [
        os.path.join(_HERE,       "assets", "sounds"),  # TSIS4/assets/sounds/  <-- primary
        os.path.join(script_dir,  "assets", "sounds"),  # next to main script
        os.path.join(os.getcwd(), "assets", "sounds"),  # cwd/assets/sounds/
        os.path.join(_HERE,       "assets"),             # TSIS4/assets/  fallback
        os.path.join(script_dir,  "assets"),             # script/assets/ fallback
        os.path.join(os.getcwd(), "assets"),             # cwd/assets/    fallback
    ]
    for d in candidates:
        if os.path.isdir(d) and any(f.endswith(".wav") for f in os.listdir(d)):
            return d
    return candidates[0]   # last resort — will log MISSING for each file


class SoundManager:
    """Loads all WAV files from the assets/ folder and plays them on demand.

    Robust against:
    - mixer not initialised yet (re-inits automatically)
    - wrong working directory (searches multiple candidate paths)
    - missing files (logs warning, returns None, never crashes)
    - sound disabled via settings (enabled flag checked on every play())
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled   # toggled from Settings screen
        self._sounds: dict = {}
        self._init_mixer()       # make sure mixer is ready before loading
        self._load_all()

    # ── Setup ─────────────────────────────────────────────────────────────────

    def _init_mixer(self):
        """Ensure pygame.mixer is initialised with compatible settings.
        If it was already initialised with wrong params, re-init it.
        """
        if not pygame.mixer.get_init():
            # Mixer was never started — initialise now
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
                print(f"[Sound] mixer initialised: {pygame.mixer.get_init()}")
            except pygame.error as e:
                print(f"[Sound] mixer init failed: {e}")
                return

        freq, size, ch = pygame.mixer.get_init()
        if ch != 2 or freq != 44100:
            # Wrong params — quit and re-init with correct settings
            print(f"[Sound] Re-initialising mixer (was {freq}Hz ch={ch})")
            pygame.mixer.quit()
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
                print(f"[Sound] mixer re-init OK: {pygame.mixer.get_init()}")
            except pygame.error as e:
                print(f"[Sound] mixer re-init failed: {e}")

        # Allocate enough channels so overlapping sounds don't get cut off
        pygame.mixer.set_num_channels(16)

    def _load_all(self):
        """Pre-load every WAV file into memory for zero-latency playback."""
        if not pygame.mixer.get_init():
            print("[Sound] Cannot load sounds — mixer not available.")
            return

        assets_dir = _find_assets_dir()
        print(f"[Sound] Loading from: {assets_dir}")

        for key, filename in _SOUND_FILES.items():
            path = os.path.join(assets_dir, filename)
            if os.path.exists(path):
                try:
                    self._sounds[key] = pygame.mixer.Sound(path)
                    print(f"[Sound] OK  {key} <- {path}")
                except pygame.error as e:
                    print(f"[Sound] FAIL {key}: {e}")
                    self._sounds[key] = None
            else:
                print(f"[Sound] MISSING {key}: {path}")
                self._sounds[key] = None

    # ── Public API ────────────────────────────────────────────────────────────

    def play(self, key: str):
        """Play sound by name. Safe to call even if the sound failed to load."""
        if not self.enabled:
            return                              # sound disabled in settings
        snd = self._sounds.get(key)
        if snd is not None:
            snd.play()                          # non-blocking playback


# ──────────────────────────────────────────────
# HELPER: grid cell → pixel top-left corner
# ──────────────────────────────────────────────
def cell_to_px(col: int, row: int) -> tuple[int, int]:
    """Return the top-left pixel (x, y) of grid cell (col, row).
    Rows are offset downward by PANEL_H to leave room for the HUD.
    """
    return col * CELL, row * CELL + PANEL_H


# ══════════════════════════════════════════════
# CLASS: Snake
# ══════════════════════════════════════════════
class Snake:
    """Player-controlled snake stored as an ordered list of (col, row) cells.
    Index 0 is always the head. Movement is tile-based (one cell per step).
    """

    def __init__(self, head_color=None, body_color=None, outline_color=None):
        # Allow custom colors injected from settings
        self.head_color    = head_color    or DEFAULT_SNAKE_HEAD
        self.body_color    = body_color    or DEFAULT_SNAKE_BODY
        self.outline_color = outline_color or DEFAULT_SNAKE_OUTLINE
        self.reset()

    def reset(self):
        """Teleport snake back to center, length 3, facing right."""
        cx, cy         = COLS // 2, ROWS // 2
        self.body      = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)    # current movement vector (dx, dy)
        self.next_dir  = (1, 0)    # buffered input processed on next step
        self.grew      = False     # True means tail stays this step (after eating)

    def set_direction(self, dx: int, dy: int):
        """Buffer a direction change. Rejects 180° reversals to prevent self-bite."""
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.next_dir = (dx, dy)

    def step(self, obstacles: set) -> bool:
        """Advance head by one cell. Returns False if the snake should die.

        obstacles — set of (col, row) tuples that are impassable wall blocks.
        The caller passes this set so Snake doesn't need to own obstacle data.
        """
        self.direction = self.next_dir         # apply buffered input
        hx, hy = self.body[0]
        new_head = (hx + self.direction[0], hy + self.direction[1])

        # ── Collision: border walls ───────────────────────────────────────────
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            return False   # hit the border → dead

        # ── Collision: obstacle blocks ────────────────────────────────────────
        if new_head in obstacles:
            return False   # hit an internal wall → dead

        # ── Collision: own body ───────────────────────────────────────────────
        if new_head in self.body:
            return False   # bit itself → dead

        self.body.insert(0, new_head)   # prepend new head

        if self.grew:
            self.grew = False           # skip tail removal → snake gets longer
        else:
            self.body.pop()             # remove tail → length unchanged

        return True    # survived this step

    def grow(self):
        """Schedule the snake to grow by one segment on the next step."""
        self.grew = True

    def shrink(self, amount: int = 2) -> bool:
        """Remove `amount` segments from the tail. Returns False if snake dies.
        Snake dies when its length would drop to 0 or below.
        """
        for _ in range(amount):
            if len(self.body) <= 1:
                return False   # can't shrink further — game over
            self.body.pop()    # remove last (tail) segment
        return True

    def draw(self, surface: pygame.Surface):
        """Draw every segment; head gets a different color and eyes."""
        for i, (col, row) in enumerate(self.body):
            px, py = cell_to_px(col, row)
            color  = self.head_color if i == 0 else self.body_color
            # Filled rounded rectangle for the segment body
            pygame.draw.rect(surface, color,
                             (px + 1, py + 1, CELL - 2, CELL - 2), border_radius=4)
            # 1-pixel outline for definition
            pygame.draw.rect(surface, self.outline_color,
                             (px + 1, py + 1, CELL - 2, CELL - 2), 1, border_radius=4)
            if i == 0:
                self._draw_eyes(surface, px, py)

    def _draw_eyes(self, surface: pygame.Surface, px: int, py: int):
        """Place two small eye dots on the head facing the movement direction."""
        dx, dy = self.direction
        # Offset positions depend on which way the snake is moving
        offsets = {
            ( 1,  0): [(12,  5), (12, 13)],   # moving right → eyes on right side
            (-1,  0): [( 5,  5), ( 5, 13)],   # moving left
            ( 0, -1): [( 5,  5), (13,  5)],   # moving up
            ( 0,  1): [( 5, 13), (13, 13)],   # moving down
        }
        for ex, ey in offsets.get((dx, dy), [(5, 5), (13, 5)]):
            pygame.draw.circle(surface, TEXT_COLOR, (px + ex, py + ey), 3)  # white iris
            pygame.draw.circle(surface, BG_COLOR,   (px + ex, py + ey), 1)  # dark pupil


# ══════════════════════════════════════════════
# CLASS: Food
# ══════════════════════════════════════════════
class Food:
    """Normal food item — weighted random type, optional lifetime countdown."""

    def __init__(self, occupied: set):
        """occupied — set of (col, row) cells that must not contain food."""
        kind = random.choice(FOOD_POOL)   # pick from weighted pool
        self.value    = kind["value"]
        self.color    = kind["color"]
        self.shine    = kind["shine"]
        self.label    = kind["label"]
        self.lifetime = kind["lifetime"]  # None = immortal
        self.age      = 0.0               # seconds alive
        self.expired  = False             # True once age >= lifetime
        self.pos      = self._random_pos(occupied)

    @staticmethod
    def _random_pos(occupied: set) -> tuple[int, int]:
        """Pick a random free cell avoiding the snake body, obstacles, etc."""
        free = [(c, r) for c in range(COLS) for r in range(ROWS)
                if (c, r) not in occupied]
        return random.choice(free) if free else (0, 0)

    def update(self, dt: float):
        """Advance age by dt seconds. Set expired when lifetime is exceeded."""
        if self.lifetime is not None:
            self.age += dt
            if self.age >= self.lifetime:
                self.expired = True

    def draw(self, surface: pygame.Surface):
        """Draw colored circle + value label + optional countdown bar."""
        col, row = self.pos
        px, py   = cell_to_px(col, row)
        cx, cy   = px + CELL // 2, py + CELL // 2
        r        = CELL // 2 - 2

        pygame.draw.circle(surface, self.color, (cx, cy), r)        # main body
        pygame.draw.circle(surface, self.shine, (cx - 3, cy - 3), 4) # highlight dot
        lbl = font_small.render(self.label, True, TEXT_COLOR)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))

        # Shrinking timer bar drawn at the bottom of the cell
        if self.lifetime is not None:
            ratio = max(0.0, 1.0 - self.age / self.lifetime)
            bar_w = int(CELL * ratio)
            # Bar color shifts green → yellow → red as time runs out
            bar_color = (
                ( 50, 220,  50) if ratio > 0.5  else
                (220, 200,  30) if ratio > 0.25 else
                (220,  50,  50)
            )
            pygame.draw.rect(surface, bar_color, (px, py + CELL - 3, bar_w, 3))


# ══════════════════════════════════════════════
# CLASS: PoisonFood
# ══════════════════════════════════════════════
class PoisonFood:
    """Poison food: dark-red skull. Eating it shortens the snake by 2 segments.
    If the snake becomes too short (len ≤ 1) the game ends.
    Has a 10-second lifetime so it doesn't clog the field permanently.
    """

    LIFETIME = 10.0    # seconds before poison disappears on its own

    def __init__(self, occupied: set):
        self.pos     = Food._random_pos(occupied)   # reuse static helper
        self.age     = 0.0
        self.expired = False

    def update(self, dt: float):
        self.age += dt
        if self.age >= self.LIFETIME:
            self.expired = True

    def draw(self, surface: pygame.Surface):
        col, row = self.pos
        px, py   = cell_to_px(col, row)
        cx, cy   = px + CELL // 2, py + CELL // 2
        r        = CELL // 2 - 2

        pygame.draw.circle(surface, DARK_RED, (cx, cy), r)               # dark red fill
        pygame.draw.circle(surface, (180, 0, 0), (cx - 2, cy - 2), 3)    # lighter spot
        lbl = font_small.render("☠", True, (255, 80, 80))                # skull label
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))

        # Countdown bar (same mechanic as normal timed food)
        ratio = max(0.0, 1.0 - self.age / self.LIFETIME)
        bar_w = int(CELL * ratio)
        pygame.draw.rect(surface, (180, 30, 30), (px, py + CELL - 3, bar_w, 3))


# ══════════════════════════════════════════════
# CLASS: PowerUp
# ══════════════════════════════════════════════
class PowerUp:
    """Temporary collectible power-up: speed boost, slow motion, or shield.

    Each power-up:
    - sits on the field for up to `field_lifetime` ms (disappears if untouched)
    - applies an effect when the snake's head overlaps it
    - the effect lasts for `effect_duration` ms (shield: until triggered once)
    """

    def __init__(self, occupied: set):
        kind = random.choice(POWERUP_TYPES)    # pick a random power-up type
        self.kind           = kind["kind"]
        self.label          = kind["label"]
        self.color          = kind["color"]
        self.shine          = kind["shine"]
        self.effect_duration = kind["effect_duration"]   # ms
        self.field_lifetime  = kind["field_lifetime"]    # ms
        self.spawn_time      = pygame.time.get_ticks()   # record spawn timestamp
        self.expired         = False
        self.pos             = Food._random_pos(occupied)

    def update(self):
        """Check if the power-up has been on the field too long."""
        if pygame.time.get_ticks() - self.spawn_time >= self.field_lifetime:
            self.expired = True   # vanish without being collected

    def draw(self, surface: pygame.Surface):
        col, row = self.pos
        px, py   = cell_to_px(col, row)
        cx, cy   = px + CELL // 2, py + CELL // 2
        r        = CELL // 2 - 1

        # Slightly larger circle with a pulsing outline to attract attention
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        pygame.draw.circle(surface, self.shine, (cx - 2, cy - 2), 4)
        # Dashed outer ring to visually separate from normal food
        pygame.draw.circle(surface, TEXT_COLOR, (cx, cy), r, 1)

        lbl = font_small.render(self.label, True, TEXT_COLOR)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))

        # Countdown bar using milliseconds
        elapsed = pygame.time.get_ticks() - self.spawn_time
        ratio   = max(0.0, 1.0 - elapsed / self.field_lifetime)
        bar_w   = int(CELL * ratio)
        pygame.draw.rect(surface, self.color, (px, py + CELL - 3, bar_w, 3))


# ══════════════════════════════════════════════
# CLASS: Obstacle
# ══════════════════════════════════════════════
class Obstacle:
    """Static wall block inside the arena.

    Blocks are placed randomly but the placement algorithm guarantees
    the snake's current head position is never blocked.
    """

    def __init__(self, pos: tuple[int, int]):
        self.pos = pos     # (col, row) — immutable once placed

    def draw(self, surface: pygame.Surface):
        col, row = self.pos
        px, py   = cell_to_px(col, row)
        # Solid brownish square with a darker outline
        pygame.draw.rect(surface, OBSTACLE_COLOR, (px, py, CELL, CELL))
        pygame.draw.rect(surface, (50, 30, 10), (px, py, CELL, CELL), 2)
        # Small cross detail to visually distinguish from the border
        mid = CELL // 2
        pygame.draw.line(surface, (110, 80, 40), (px + 3, py + mid), (px + CELL - 4, py + mid), 1)
        pygame.draw.line(surface, (110, 80, 40), (px + mid, py + 3), (px + mid, py + CELL - 4), 1)


def place_obstacles(count: int, occupied: set) -> list[Obstacle]:
    """Generate `count` non-overlapping obstacle blocks avoiding `occupied` cells.

    occupied should include the snake body and a safety margin around the head.
    Returns a list of Obstacle objects.
    """
    obstacles = []
    occupied  = set(occupied)   # copy so we can add to it without side-effects
    attempts  = 0

    while len(obstacles) < count and attempts < 1000:
        attempts += 1
        col = random.randint(0, COLS - 1)
        row = random.randint(0, ROWS - 1)
        if (col, row) not in occupied:
            obstacles.append(Obstacle((col, row)))
            occupied.add((col, row))   # mark this cell so no two obstacles overlap

    return obstacles


# ══════════════════════════════════════════════
# DRAWING HELPERS
# ══════════════════════════════════════════════

def draw_field(surface: pygame.Surface, show_grid: bool, obstacles: list):
    """Draw background, optional grid lines, border, and obstacle blocks."""
    # Dark background for the play area only (HUD handled separately)
    pygame.draw.rect(surface, BG_COLOR, (0, PANEL_H, WIDTH, HEIGHT - PANEL_H))

    if show_grid:
        for col in range(COLS):
            for row in range(ROWS):
                px, py = cell_to_px(col, row)
                pygame.draw.rect(surface, GRID_COLOR, (px, py, CELL, CELL), 1)

    # Draw all obstacle blocks
    for obs in obstacles:
        obs.draw(surface)

    # Thick border wall around the play area
    pygame.draw.rect(surface, WALL_COLOR, (0, PANEL_H, WIDTH, HEIGHT - PANEL_H), 3)


def draw_hud(surface: pygame.Surface, score: int, level: int,
             personal_best: int, active_effect: str | None,
             effect_end_ms: int):
    """Render the top HUD panel.

    Displays: Score (left), active power-up effect with countdown (centre),
    Level (right), personal best below score.
    """
    # Panel background
    pygame.draw.rect(surface, PANEL_BG, (0, 0, WIDTH, PANEL_H))
    pygame.draw.line(surface, WALL_COLOR, (0, PANEL_H), (WIDTH, PANEL_H), 2)

    # Score (left side)
    score_lbl = font_medium.render(f"Score: {score}", True, GOLD)
    surface.blit(score_lbl, (10, 4))

    # Personal best below score
    pb_lbl = font_small.render(f"Best: {personal_best}", True, SILVER)
    surface.blit(pb_lbl, (10, 30))

    # Level (right side)
    level_lbl = font_medium.render(f"Level: {level}", True, (100, 200, 255))
    surface.blit(level_lbl, (WIDTH - level_lbl.get_width() - 10, 4))

    # Active power-up effect countdown (centre)
    if active_effect:
        now       = pygame.time.get_ticks()
        remaining = max(0, (effect_end_ms - now) // 1000)
        labels = {
            "speed_boost": f"⚡ Speed +{remaining}s",
            "slow_motion": f"🐢 Slow {remaining}s",
            "shield":      "🛡 Shield",
        }
        text  = labels.get(active_effect, active_effect)
        color = (255, 255, 100) if active_effect == "speed_boost" else \
                (100, 200, 255) if active_effect == "slow_motion" else \
                (180, 255, 180)
        eff_lbl = font_small.render(text, True, color)
        surface.blit(eff_lbl,
                     (WIDTH // 2 - eff_lbl.get_width() // 2, PANEL_H // 2 - eff_lbl.get_height() // 2))