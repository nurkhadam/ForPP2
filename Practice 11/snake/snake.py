import pygame
import random
import sys

# ──────────────────────────────────────────────
# Initialize pygame
# ──────────────────────────────────────────────
pygame.init()

# ──────────────────────────────────────────────
# Grid and screen constants
# ──────────────────────────────────────────────
CELL      = 20    # pixel size of one grid cell
COLS      = 25    # number of grid columns
ROWS      = 25    # number of grid rows
PANEL_H   = 50    # height of the HUD panel at the top
WIDTH     = COLS * CELL
HEIGHT    = ROWS * CELL + PANEL_H

# ──────────────────────────────────────────────
# Color constants (RGB)
# ──────────────────────────────────────────────
BG_COLOR      = ( 15,  15,  15)
GRID_COLOR    = ( 30,  30,  30)
SNAKE_HEAD    = ( 50, 220,  50)
SNAKE_BODY    = ( 30, 160,  30)
SNAKE_OUTLINE = ( 10,  90,  10)
WALL_COLOR    = ( 80,  80,  80)
TEXT_COLOR    = (255, 255, 255)
GOLD          = (255, 215,   0)
RED           = (220,  30,  30)
SILVER        = (192, 192, 192)
ORANGE        = (255, 140,   0)
PURPLE        = (180,  50, 220)

# ──────────────────────────────────────────────
# Speed constants
# BASE_MOVE = frames between snake steps (lower = faster)
# ──────────────────────────────────────────────
BASE_FPS  = 60
BASE_MOVE = 15

# ──────────────────────────────────────────────
# Level progression: food items per level
# ──────────────────────────────────────────────
FOOD_PER_LEVEL = 4

# ──────────────────────────────────────────────
# Food type definitions
# weight    = relative spawn probability
# value     = score points awarded
# lifetime  = seconds before the food disappears (None = never)
# ──────────────────────────────────────────────
FOOD_TYPES = [
    {
        "label":    "1",
        "value":    1,
        "color":    (220,  50,  50),
        "shine":    (255, 120, 120),
        "weight":   50,
        "lifetime": None,
    },
    {
        "label":    "2",
        "value":    2,
        "color":    ORANGE,
        "shine":    (255, 190, 100),
        "weight":   30,
        "lifetime": 6.0,
    },
    {
        "label":    "3",
        "value":    3,
        "color":    PURPLE,
        "shine":    (220, 130, 255),
        "weight":   15,
        "lifetime": 4.0,
    },
    {
        "label":    "5",
        "value":    5,
        "color":    GOLD,
        "shine":    (255, 240, 100),
        "weight":   5,
        "lifetime": 3.0,
    },
]

# Flat weighted pool for random.choice()
FOOD_POOL = []
for ft in FOOD_TYPES:
    FOOD_POOL.extend([ft] * ft["weight"])

# ──────────────────────────────────────────────
# Window, clock, fonts
# ──────────────────────────────────────────────
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake — Practice 11")
clock  = pygame.time.Clock()

font_large  = pygame.font.SysFont("Consolas", 40, bold=True)
font_medium = pygame.font.SysFont("Consolas", 24, bold=True)
font_small  = pygame.font.SysFont("Consolas", 16)


# ──────────────────────────────────────────────
# HELPER: cell grid position → pixel position
# ──────────────────────────────────────────────
def cell_to_px(col, row):
    """Convert grid (col, row) to top-left pixel (x, y), offset by HUD panel."""
    return col * CELL, row * CELL + PANEL_H


# ══════════════════════════════════════════════
# CLASS: Snake
# ══════════════════════════════════════════════
class Snake:
    """The player-controlled snake.
    Stored as a list of (col, row) tuples; index 0 is the head."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Place the snake at the centre of the grid, length 3, moving right."""
        cx, cy         = COLS // 2, ROWS // 2
        self.body      = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)   # current movement direction
        self.next_dir  = (1, 0)   # buffered next direction (applied each step)
        self.grew      = False    # when True, the tail is NOT removed this step

    def set_direction(self, dx, dy):
        """Queue a direction change; 180-degree reversal is ignored."""
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.next_dir = (dx, dy)

    def step(self):
        """Advance the snake by one cell. Returns False if the snake dies."""
        self.direction = self.next_dir
        hx, hy = self.body[0]
        new_head = (hx + self.direction[0], hy + self.direction[1])

        # Wall collision check
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            return False

        # Self-collision check
        if new_head in self.body:
            return False

        self.body.insert(0, new_head)

        if self.grew:
            self.grew = False   # tail stays → snake is one cell longer
        else:
            self.body.pop()     # tail removed → length unchanged

        return True

    def grow(self):
        """Signal that the tail should NOT be removed on the next step."""
        self.grew = True

    def draw(self, surface):
        """Render each body segment; head is brighter with eyes."""
        for i, (col, row) in enumerate(self.body):
            px, py = cell_to_px(col, row)
            color  = SNAKE_HEAD if i == 0 else SNAKE_BODY
            pygame.draw.rect(surface, color,
                             (px + 1, py + 1, CELL - 2, CELL - 2), border_radius=4)
            pygame.draw.rect(surface, SNAKE_OUTLINE,
                             (px + 1, py + 1, CELL - 2, CELL - 2), 1, border_radius=4)
            if i == 0:
                self._draw_eyes(surface, px, py)

    def _draw_eyes(self, surface, px, py):
        """Draw two small eyes on the head, oriented toward the movement direction."""
        dx, dy = self.direction
        offsets = {
            ( 1,  0): [(12,  5), (12, 13)],
            (-1,  0): [( 5,  5), ( 5, 13)],
            ( 0, -1): [( 5,  5), (13,  5)],
            ( 0,  1): [( 5, 13), (13, 13)],
        }
        for ex, ey in offsets.get((dx, dy), [(5, 5), (13, 5)]):
            pygame.draw.circle(surface, TEXT_COLOR, (px + ex, py + ey), 3)
            pygame.draw.circle(surface, BG_COLOR,   (px + ex, py + ey), 1)


# ══════════════════════════════════════════════
# CLASS: Food
# ══════════════════════════════════════════════
class Food:
    """A single piece of food on the grid.

    Features:
    - Weighted random type selection (common/uncommon/rare/legendary)
    - Optional lifetime: food disappears after `lifetime` seconds
    - Timer bar drawn beneath the food when lifetime is finite
    """

    def __init__(self, snake_body):
        # Pick a food type from the weighted pool
        self.kind     = random.choice(FOOD_POOL)
        self.value    = self.kind["value"]
        self.color    = self.kind["color"]
        self.shine    = self.kind["shine"]
        self.label    = self.kind["label"]
        self.lifetime = self.kind["lifetime"]   # None or float seconds

        # Timer tracking (in seconds)
        self.age      = 0.0       # how long this food has been alive
        self.expired  = False     # set to True when age >= lifetime

        # Place on a random free cell
        self.pos = self._random_pos(snake_body)

    @staticmethod
    def _random_pos(snake_body):
        """Return a random grid cell not occupied by the snake."""
        free = [(c, r) for c in range(COLS) for r in range(ROWS)
                if (c, r) not in snake_body]
        return random.choice(free) if free else (0, 0)

    def update(self, dt):
        """Advance the age timer; mark expired when lifetime is exceeded.
        dt = elapsed seconds since last frame."""
        if self.lifetime is not None:
            self.age += dt
            if self.age >= self.lifetime:
                self.expired = True

    def draw(self, surface):
        """Render the food circle, label, and (if timed) a shrinking countdown bar."""
        col, row = self.pos
        px, py   = cell_to_px(col, row)
        cx, cy   = px + CELL // 2, py + CELL // 2
        r        = CELL // 2 - 2

        # Main circle
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        # Shine highlight
        pygame.draw.circle(surface, self.shine, (cx - 3, cy - 3), 4)
        # Value label (centred)
        lbl = font_small.render(self.label, True, TEXT_COLOR)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))

        # Countdown timer bar drawn below the cell
        if self.lifetime is not None:
            ratio     = max(0.0, 1.0 - self.age / self.lifetime)
            bar_w     = int(CELL * ratio)
            bar_color = (
                ( 50, 220,  50) if ratio > 0.5 else   # green when plenty of time
                (220, 200,  30) if ratio > 0.25 else  # yellow when running low
                (220,  50,  50)                        # red when almost gone
            )
            pygame.draw.rect(surface, bar_color, (px, py + CELL - 3, bar_w, 3))


# ══════════════════════════════════════════════
# FUNCTION: draw_field
# ══════════════════════════════════════════════
def draw_field(surface):
    """Draw the dark grid background and the border walls."""
    pygame.draw.rect(surface, BG_COLOR, (0, PANEL_H, WIDTH, HEIGHT - PANEL_H))
    for col in range(COLS):
        for row in range(ROWS):
            px, py = cell_to_px(col, row)
            pygame.draw.rect(surface, GRID_COLOR, (px, py, CELL, CELL), 1)
    pygame.draw.rect(surface, WALL_COLOR, (0, PANEL_H, WIDTH, HEIGHT - PANEL_H), 3)


# ══════════════════════════════════════════════
# FUNCTION: draw_hud
# ══════════════════════════════════════════════
def draw_hud(surface, score, level):
    """Render the top HUD panel showing the current score and level."""
    pygame.draw.rect(surface, (20, 20, 40), (0, 0, WIDTH, PANEL_H))
    pygame.draw.line(surface, WALL_COLOR, (0, PANEL_H), (WIDTH, PANEL_H), 2)

    score_lbl = font_medium.render(f"Score: {score}", True, GOLD)
    level_lbl = font_medium.render(f"Level: {level}", True, (100, 200, 255))
    surface.blit(score_lbl, (10, PANEL_H // 2 - score_lbl.get_height() // 2))
    surface.blit(level_lbl, (WIDTH - level_lbl.get_width() - 10,
                              PANEL_H // 2 - level_lbl.get_height() // 2))


# ══════════════════════════════════════════════
# FUNCTION: end_screen
# ══════════════════════════════════════════════
def end_screen(score, level):
    """Overlay a semi-transparent game-over screen; return True to restart."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    lines = [
        (font_large,  "GAME OVER",              RED),
        (font_medium, f"Score: {score}",        GOLD),
        (font_medium, f"Level: {level}",        (100, 200, 255)),
        (font_small,  "R — restart  ESC — quit", TEXT_COLOR),
    ]
    total_h = sum(f.get_height() + 10 for f, _, _ in lines)
    y = HEIGHT // 2 - total_h // 2
    for fnt, text, color in lines:
        lbl = fnt.render(text, True, color)
        screen.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, y))
        y += lbl.get_height() + 10

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:            pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:          return True
                if event.key == pygame.K_ESCAPE:     pygame.quit(); sys.exit()
        clock.tick(30)