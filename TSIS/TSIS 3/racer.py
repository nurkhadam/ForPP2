"""
racer.py  —  TSIS 3
All game objects, constants, and helper draw functions.
"""

import pygame
import random
import sys

# ──────────────────────────────────────────────
# Initialize pygame
# ──────────────────────────────────────────────
pygame.init()

# ──────────────────────────────────────────────
# Screen / timing
# ──────────────────────────────────────────────
SCREEN_WIDTH  = 480
SCREEN_HEIGHT = 680
FPS           = 60

# ──────────────────────────────────────────────
# Colors
# ──────────────────────────────────────────────
WHITE   = (255, 255, 255)
BLACK   = (  0,   0,   0)
GRAY    = (100, 100, 100)
DARK    = ( 30,  30,  30)
RED     = (220,  30,  30)
YELLOW  = (255, 215,   0)
GREEN   = ( 30, 200,  30)
BLUE    = ( 30, 100, 220)
CYAN    = (  0, 220, 220)
ORANGE  = (255, 140,   0)
SILVER  = (192, 192, 192)
GOLD    = (255, 215,   0)
BRONZE  = (205, 127,  50)
PURPLE  = (160,  32, 240)
LIME    = (160, 240,  50)
PINK    = (255,  80, 180)

# Car color palette (for settings)
CAR_COLOR_MAP = {
    "blue":   (30,  100, 220),
    "red":    (220,  30,  30),
    "green":  ( 30, 180,  30),
    "purple": (160,  32, 240),
    "orange": (255, 140,   0),
}

# ──────────────────────────────────────────────
# Road
# ──────────────────────────────────────────────
ROAD_LEFT  = 80
ROAD_RIGHT = 400
LANE_COUNT = 3

def lane_x(lane: int, car_width: int) -> int:
    """Return the left-edge x for a car in the given lane (0-based)."""
    lane_width = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT
    return ROAD_LEFT + lane * lane_width + (lane_width - car_width) // 2

# ──────────────────────────────────────────────
# Gameplay tuning
# ──────────────────────────────────────────────
COINS_PER_SPEED_UP  = 5
DISTANCE_PER_FRAME  = 1          # metres per frame (1 px = 1 m for display)
POWERUP_TIMEOUT     = 8_000      # ms before uncollected power-up disappears
NITRO_DURATION      = 4_000      # ms
NITRO_SPEED_BONUS   = 4          # extra px/frame added to player movement
NITRO_SCROLL_BONUS  = 5          # extra px/frame added to road scroll (all objects)

# Difficulty presets: (enemy_spawn_ms, coin_spawn_ms, obstacle_spawn_ms, base_speed)
DIFFICULTY_PRESETS = {
    "easy":   (2000, 1800, 3500, 3),
    "normal": (1500, 2000, 2500, 4),
    "hard":   (1000, 2200, 1600, 6),
}

# ──────────────────────────────────────────────
# Coin definitions (unchanged from Practice 11)
# ──────────────────────────────────────────────
COIN_TYPES = [
    {"label": "B", "value": 1, "color": BRONZE, "outline": (139, 90,  43), "radius": 10, "weight": 60},
    {"label": "S", "value": 3, "color": SILVER, "outline": (120, 120, 120), "radius": 12, "weight": 30},
    {"label": "G", "value": 5, "color": GOLD,   "outline": (180, 140,  0), "radius": 14, "weight": 10},
]
COIN_POOL = []
for _ct in COIN_TYPES:
    COIN_POOL.extend([_ct] * _ct["weight"])

# ──────────────────────────────────────────────
# Window, clock, fonts
# ──────────────────────────────────────────────
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer  —  TSIS 3")
clock  = pygame.time.Clock()

font_large  = pygame.font.SysFont("Consolas", 38, bold=True)
font_medium = pygame.font.SysFont("Consolas", 24, bold=True)
font_small  = pygame.font.SysFont("Consolas", 15)
font_tiny   = pygame.font.SysFont("Consolas", 12)


# ══════════════════════════════════════════════
# PlayerCar
# ══════════════════════════════════════════════
class PlayerCar:
    WIDTH  = 50
    HEIGHT = 80
    SPEED  = 5
    MAX_HP = 3

    def __init__(self, color=BLUE):
        self.base_color = color
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - self.WIDTH // 2,
            SCREEN_HEIGHT - self.HEIGHT - 20,
            self.WIDTH, self.HEIGHT,
        )
        self.hp = self.MAX_HP
        # Power-up state
        self.shield_active = False
        self.nitro_active  = False
        self.nitro_end_ms  = 0
        self.invincible_flash = 0  # frames of invincibility after hit

    def move(self, keys, nitro_bonus=0):
        spd = self.SPEED + (NITRO_SPEED_BONUS if self.nitro_active else 0)
        if keys[pygame.K_LEFT]  and self.rect.left   > ROAD_LEFT:     self.rect.x -= spd
        if keys[pygame.K_RIGHT] and self.rect.right  < ROAD_RIGHT:    self.rect.x += spd
        if keys[pygame.K_UP]    and self.rect.top    > 0:             self.rect.y -= spd
        if keys[pygame.K_DOWN]  and self.rect.bottom < SCREEN_HEIGHT: self.rect.y += spd

    def update(self, now_ms):
        if self.nitro_active and now_ms >= self.nitro_end_ms:
            self.nitro_active = False
        if self.invincible_flash > 0:
            self.invincible_flash -= 1

    def activate_nitro(self, now_ms):
        self.nitro_active = True
        self.nitro_end_ms = now_ms + NITRO_DURATION

    def activate_shield(self):
        self.shield_active = True

    def repair(self):
        """Fully restore HP."""
        self.hp = self.MAX_HP

    def take_damage(self, amount=1):
        """Deal damage. Returns True if player dies."""
        if self.invincible_flash > 0:
            return False
        if self.shield_active:
            self.shield_active = False
            self.invincible_flash = 90
            return False
        self.hp = max(0, self.hp - amount)
        self.invincible_flash = 90  # ~1.5s invincibility after hit
        return self.hp <= 0

    # kept for compatibility with enemy collision code
    def hit_by_obstacle(self):
        return self.take_damage(1)

    def draw(self, surface):
        color = self.base_color
        if self.nitro_active and (pygame.time.get_ticks() // 100) % 2 == 0:
            color = CYAN
        if self.invincible_flash > 0 and (self.invincible_flash // 5) % 2 == 0:
            color = WHITE

        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (180, 220, 255),
                         (self.rect.x + 8, self.rect.y + 10, 34, 20), border_radius=4)
        pygame.draw.rect(surface, RED,
                         (self.rect.x + 5, self.rect.bottom - 12, 12, 8), border_radius=2)
        pygame.draw.rect(surface, RED,
                         (self.rect.right - 17, self.rect.bottom - 12, 12, 8), border_radius=2)
        if self.shield_active:
            pygame.draw.circle(surface, CYAN,
                                self.rect.center,
                                max(self.rect.width, self.rect.height) // 2 + 8, 3)
        if self.nitro_active:
            flame_rect = pygame.Rect(self.rect.x + 10, self.rect.bottom, 30, 18)
            pygame.draw.ellipse(surface, ORANGE, flame_rect)
            inner = pygame.Rect(self.rect.x + 16, self.rect.bottom + 2, 18, 10)
            pygame.draw.ellipse(surface, YELLOW, inner)


# ══════════════════════════════════════════════
# EnemyCar
# ══════════════════════════════════════════════
class EnemyCar:
    WIDTH  = 50
    HEIGHT = 80
    COLORS = [RED, GREEN, ORANGE, PURPLE, PINK]

    def __init__(self, base_speed, player_rect=None):
        self.color = random.choice(self.COLORS)
        lane = self._safe_lane(player_rect)
        x    = lane_x(lane, self.WIDTH)
        self.rect  = pygame.Rect(x, -self.HEIGHT - random.randint(0, 60), self.WIDTH, self.HEIGHT)
        self.speed = max(2, base_speed + random.randint(-1, 2))

    def _safe_lane(self, player_rect):
        lane = random.randint(0, LANE_COUNT - 1)
        if player_rect:
            pl = (player_rect.centerx - ROAD_LEFT) // ((ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT)
            pl = max(0, min(LANE_COUNT - 1, pl))
            for _ in range(6):
                if lane != pl:
                    break
                lane = random.randint(0, LANE_COUNT - 1)
        return lane

    def update(self, extra=0):
        self.rect.y += self.speed + extra

    def is_off_screen(self):
        return self.rect.top > SCREEN_HEIGHT

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (200, 230, 200),
                         (self.rect.x + 8, self.rect.y + 10, 34, 20), border_radius=4)
        pygame.draw.rect(surface, YELLOW,
                         (self.rect.x + 5, self.rect.bottom - 12, 12, 8), border_radius=2)
        pygame.draw.rect(surface, YELLOW,
                         (self.rect.right - 17, self.rect.bottom - 12, 12, 8), border_radius=2)


# ══════════════════════════════════════════════
# Coin (unchanged logic from Practice 11)
# ══════════════════════════════════════════════
class Coin:
    FALL_SPEED = 4

    def __init__(self):
        self.kind   = random.choice(COIN_POOL)
        self.radius = self.kind["radius"]
        self.value  = self.kind["value"]
        x = random.randint(ROAD_LEFT + self.radius, ROAD_RIGHT - self.radius)
        self.center = [x, -self.radius]
        self.rect   = pygame.Rect(x - self.radius, -self.radius * 2,
                                   self.radius * 2, self.radius * 2)

    def update(self, extra=0):
        self.center[1] += self.FALL_SPEED + extra
        self.rect.center = (int(self.center[0]), int(self.center[1]))

    def is_off_screen(self):
        return self.center[1] > SCREEN_HEIGHT + self.radius

    def draw(self, surface):
        cx, cy = int(self.center[0]), int(self.center[1])
        pygame.draw.circle(surface, self.kind["color"],   (cx, cy), self.radius)
        pygame.draw.circle(surface, self.kind["outline"], (cx, cy), self.radius, 2)
        lbl = font_small.render(self.kind["label"], True, BLACK)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))


# ══════════════════════════════════════════════
# PowerUp
# ══════════════════════════════════════════════
POWERUP_DEFS = {
    "nitro":  {"label": "N", "color": ORANGE, "outline": (200, 90,  0),  "radius": 14},
    "shield": {"label": "S", "color": CYAN,   "outline": (  0, 160, 160),"radius": 14},
    "repair": {"label": "R", "color": LIME,   "outline": ( 80, 180,  0), "radius": 14},
}

class PowerUp:
    FALL_SPEED = 3

    def __init__(self, kind: str, spawn_ms: int):
        self.kind      = kind
        self.spawn_ms  = spawn_ms
        d = POWERUP_DEFS[kind]
        self.radius  = d["radius"]
        self.color   = d["color"]
        self.outline = d["outline"]
        self.label   = d["label"]
        x = random.randint(ROAD_LEFT + self.radius, ROAD_RIGHT - self.radius)
        self.center = [x, -self.radius]
        self.rect   = pygame.Rect(x - self.radius, -self.radius * 2,
                                   self.radius * 2, self.radius * 2)

    def update(self, extra=0):
        self.center[1] += self.FALL_SPEED + extra
        self.rect.center = (int(self.center[0]), int(self.center[1]))

    def is_off_screen(self):
        return self.center[1] > SCREEN_HEIGHT + self.radius

    def is_expired(self, now_ms):
        return now_ms - self.spawn_ms > POWERUP_TIMEOUT

    def draw(self, surface, now_ms):
        cx, cy = int(self.center[0]), int(self.center[1])
        # Pulse opacity warning when about to expire
        age = now_ms - self.spawn_ms
        if age > POWERUP_TIMEOUT - 2000 and (now_ms // 200) % 2 == 0:
            return  # blink
        # Glow ring
        pygame.draw.circle(surface, self.outline, (cx, cy), self.radius + 4, 2)
        pygame.draw.circle(surface, self.color,   (cx, cy), self.radius)
        pygame.draw.circle(surface, self.outline, (cx, cy), self.radius, 2)
        lbl = font_medium.render(self.label, True, BLACK)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))


# ══════════════════════════════════════════════
# Obstacle  (hole, oil, barrier)
# ══════════════════════════════════════════════
OBSTACLE_TYPES = [
    {"kind": "hole",    "color": (30,  20,  10),  "w": 44, "h": 32, "damage": 1, "deadly": False},
    {"kind": "oil",     "color": (20,  20,  60),  "w": 50, "h": 22, "damage": 1, "deadly": False},
    {"kind": "barrier", "color": (255, 200,  0),  "w": 60, "h": 18, "damage": 2, "deadly": False},
]

class Obstacle:
    FALL_SPEED = 5

    def __init__(self, base_speed, player_rect=None):
        self.kind_def = random.choice(OBSTACLE_TYPES)
        w, h = self.kind_def["w"], self.kind_def["h"]
        lane = random.randint(0, LANE_COUNT - 1)
        if player_rect:
            pl = (player_rect.centerx - ROAD_LEFT) // ((ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT)
            for _ in range(5):
                if lane != pl:
                    break
                lane = random.randint(0, LANE_COUNT - 1)
        lw   = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT
        x    = ROAD_LEFT + lane * lw + (lw - w) // 2
        self.rect  = pygame.Rect(x, -h - random.randint(0, 80), w, h)
        self.speed = max(2, base_speed + random.randint(0, 2))

    def update(self, extra=0):
        self.rect.y += self.speed + extra

    def is_off_screen(self):
        return self.rect.top > SCREEN_HEIGHT

    def draw(self, surface):
        k    = self.kind_def["kind"]
        color = self.kind_def["color"]
        if k == "hole":
            # Dark pit with jagged outline
            pygame.draw.ellipse(surface, color, self.rect)
            pygame.draw.ellipse(surface, (80, 60, 30), self.rect, 3)
            lbl = font_tiny.render("HOLE", True, (160, 120, 60))
            surface.blit(lbl, (self.rect.centerx - lbl.get_width() // 2,
                                self.rect.centery - lbl.get_height() // 2))
        elif k == "oil":
            # Dark-blue slick with shimmer
            pygame.draw.ellipse(surface, color, self.rect)
            shine = pygame.Rect(self.rect.x + 6, self.rect.y + 4, self.rect.w // 3, self.rect.h // 3)
            pygame.draw.ellipse(surface, (60, 60, 140), shine)
            pygame.draw.ellipse(surface, (0, 0, 100), self.rect, 2)
            lbl = font_tiny.render("OIL", True, (100, 100, 220))
            surface.blit(lbl, (self.rect.centerx - lbl.get_width() // 2,
                                self.rect.centery - lbl.get_height() // 2))
        else:  # barrier
            pygame.draw.rect(surface, color, self.rect, border_radius=4)
            pygame.draw.rect(surface, RED, self.rect, 2, border_radius=4)
            lbl = font_tiny.render("STOP", True, RED)
            surface.blit(lbl, (self.rect.centerx - lbl.get_width() // 2,
                                self.rect.centery - lbl.get_height() // 2))


# ══════════════════════════════════════════════
# NitroStrip  (road event — speed boost strip)
# ══════════════════════════════════════════════
class NitroStrip:
    """A falling nitro circle (coin-style) that auto-boosts the player on contact."""
    RADIUS = 18
    SCROLL = 4  # pixels per frame

    def __init__(self):
        lane = random.randint(0, LANE_COUNT - 1)
        lw   = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT
        cx   = ROAD_LEFT + lane * lw + lw // 2
        self.center    = [cx, -self.RADIUS]
        self.rect      = pygame.Rect(cx - self.RADIUS, -self.RADIUS * 2,
                                      self.RADIUS * 2, self.RADIUS * 2)
        self.triggered = False

    def update(self, extra=0):
        self.center[1] += self.SCROLL + extra
        self.rect.center = (int(self.center[0]), int(self.center[1]))

    def is_off_screen(self):
        return self.center[1] > SCREEN_HEIGHT + self.RADIUS

    def draw(self, surface):
        cx, cy = int(self.center[0]), int(self.center[1])
        t = pygame.time.get_ticks()
        # Alternating orange/yellow glow
        outer_c = (255, 200, 0) if (t // 120) % 2 == 0 else (255, 120, 0)
        inner_c = (255, 240, 80)
        # Outer glow ring
        pygame.draw.circle(surface, outer_c, (cx, cy), self.RADIUS + 4, 3)
        # Main circle
        pygame.draw.circle(surface, outer_c, (cx, cy), self.RADIUS)
        # Inner highlight
        pygame.draw.circle(surface, inner_c, (cx, cy), self.RADIUS - 5)
        # "N" label
        lbl = font_medium.render("N", True, BLACK)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))


# ══════════════════════════════════════════════
# draw_road
# ══════════════════════════════════════════════
def draw_road(surface, offset):
    surface.fill((34, 120, 34))
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, SCREEN_HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_LEFT,      0, 6, SCREEN_HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_RIGHT - 6, 0, 6, SCREEN_HEIGHT))
    lane_width = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT
    for i in range(1, LANE_COUNT):
        lx = ROAD_LEFT + lane_width * i
        for y in range(-80 + offset % 80, SCREEN_HEIGHT, 80):
            pygame.draw.rect(surface, WHITE, (lx - 2, y, 4, 40))


# ══════════════════════════════════════════════
# draw_hud
# ══════════════════════════════════════════════
def draw_hud(surface, score, coin_count, enemy_speed, coins_to_boost,
             distance, powerup_info=None, hp=3, max_hp=3):
    # Semi-transparent HUD bar at top
    bar = pygame.Surface((SCREEN_WIDTH, 56), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 160))
    surface.blit(bar, (0, 0))

    surface.blit(font_medium.render(f"Score: {score}", True, WHITE), (8, 6))
    coin_lbl = font_medium.render(f"C:{coin_count}", True, YELLOW)
    surface.blit(coin_lbl, (SCREEN_WIDTH - coin_lbl.get_width() - 8, 6))
    surface.blit(font_small.render(f"Boost in: {coins_to_boost}c", True, SILVER), (8, 34))
    dist_lbl = font_small.render(f"{distance} m", True, LIME)
    surface.blit(dist_lbl, (SCREEN_WIDTH // 2 - dist_lbl.get_width() // 2, 34))
    spd = font_small.render(f"Spd:{enemy_speed}", True, SILVER)
    surface.blit(spd, (SCREEN_WIDTH - spd.get_width() - 8, 34))

    # Active power-up banner
    if powerup_info:
        name, ms_left = powerup_info
        secs = max(0, ms_left // 1000)
        colors = {"nitro": ORANGE, "shield": CYAN, "repair": LIME}
        c = colors.get(name, WHITE)
        pu_lbl = font_small.render(f"[{name.upper()} {secs}s]", True, c)
        surface.blit(pu_lbl, (SCREEN_WIDTH // 2 - pu_lbl.get_width() // 2, 6))

    # HP bar at bottom-left
    hp_bar_x, hp_bar_y = 8, SCREEN_HEIGHT - 36
    bar_w, bar_h = 120, 14
    pygame.draw.rect(surface, (60, 10, 10), (hp_bar_x, hp_bar_y, bar_w, bar_h), border_radius=4)
    fill = int(bar_w * max(0, hp) / max_hp)
    hp_color = GREEN if hp >= max_hp else (YELLOW if hp == 2 else RED)
    if fill > 0:
        pygame.draw.rect(surface, hp_color, (hp_bar_x, hp_bar_y, fill, bar_h), border_radius=4)
    pygame.draw.rect(surface, WHITE, (hp_bar_x, hp_bar_y, bar_w, bar_h), 1, border_radius=4)
    hp_lbl = font_tiny.render(f"HP {hp}/{max_hp}", True, WHITE)
    surface.blit(hp_lbl, (hp_bar_x + bar_w + 6, hp_bar_y))

    # Legend bottom-right
    leg = font_tiny.render("B=1  S=3  G=5 pts", True, SILVER)
    surface.blit(leg, (SCREEN_WIDTH - leg.get_width() - 8, SCREEN_HEIGHT - 18))


# ══════════════════════════════════════════════
# game_over_screen  (returns True=restart, False=main_menu)
# ══════════════════════════════════════════════
def game_over_screen(score, coin_count, distance):
    while True:
        screen.fill((10, 10, 20))
        _draw_centered(font_large,  "GAME OVER",             RED,    180)
        _draw_centered(font_medium, f"Score    : {score}",   WHITE,  255)
        _draw_centered(font_medium, f"Distance : {distance} m", LIME, 290)
        _draw_centered(font_medium, f"Coins    : {coin_count}", YELLOW, 325)
        _draw_centered(font_small,  "R — Retry    M — Main Menu    ESC — Quit", GRAY, 400)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:      return "retry"
                if event.key == pygame.K_m:      return "menu"
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()


def _draw_centered(font, text, color, y):
    surf = font.render(text, True, color)
    screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))