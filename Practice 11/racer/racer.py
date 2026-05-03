import pygame
import random
import sys

# ──────────────────────────────────────────────
# Initialize pygame
# ──────────────────────────────────────────────
pygame.init()

# ──────────────────────────────────────────────
# Screen and timing constants
# ──────────────────────────────────────────────
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
FPS           = 60

# ──────────────────────────────────────────────
# Color constants (RGB)
# ──────────────────────────────────────────────
WHITE   = (255, 255, 255)
BLACK   = (  0,   0,   0)
GRAY    = (100, 100, 100)
RED     = (220,  30,  30)
YELLOW  = (255, 215,   0)
GREEN   = ( 30, 200,  30)
BLUE    = ( 30, 100, 220)
ORANGE  = (255, 140,   0)
SILVER  = (192, 192, 192)
GOLD    = (255, 215,   0)
BRONZE  = (205, 127,  50)
PURPLE  = (160,  32, 240)

# ──────────────────────────────────────────────
# Road boundaries (pixels)
# ──────────────────────────────────────────────
ROAD_LEFT  = 60
ROAD_RIGHT = 340

# ──────────────────────────────────────────────
# Every N coins collected → enemy speed increases by 1
# ──────────────────────────────────────────────
COINS_PER_SPEED_UP = 5

# ──────────────────────────────────────────────
# Coin type definitions
# weight = relative spawn probability (higher = more common)
# value  = points awarded when collected
# ──────────────────────────────────────────────
COIN_TYPES = [
    {"label": "B", "value": 1,  "color": BRONZE, "outline": (139, 90,  43), "radius": 10, "weight": 60},
    {"label": "S", "value": 3,  "color": SILVER, "outline": (120, 120, 120), "radius": 12, "weight": 30},
    {"label": "G", "value": 5,  "color": GOLD,   "outline": (180, 140,  0), "radius": 14, "weight": 10},
]

# Flat weighted pool: 60 bronze + 30 silver + 10 gold entries
# random.choice(COIN_POOL) gives correct distribution automatically
COIN_POOL = []
for ct in COIN_TYPES:
    COIN_POOL.extend([ct] * ct["weight"])

# ──────────────────────────────────────────────
# Window, clock, fonts
# ──────────────────────────────────────────────
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer — Practice 11")
clock  = pygame.time.Clock()

font_large  = pygame.font.SysFont("Arial", 36, bold=True)
font_medium = pygame.font.SysFont("Arial", 24, bold=True)
font_small  = pygame.font.SysFont("Arial", 16)


# ══════════════════════════════════════════════
# CLASS: PlayerCar
# ══════════════════════════════════════════════
class PlayerCar:
    """Car controlled by the player.
    Supports 4-directional movement clamped to road / screen bounds."""

    WIDTH  = 50
    HEIGHT = 80
    SPEED  = 5

    def __init__(self):
        # Start at the bottom-centre of the road
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - self.WIDTH // 2,
            SCREEN_HEIGHT - self.HEIGHT - 20,
            self.WIDTH, self.HEIGHT
        )

    def move(self, keys):
        """Translate the car based on arrow-key input."""
        if keys[pygame.K_LEFT]  and self.rect.left   > ROAD_LEFT:     self.rect.x -= self.SPEED
        if keys[pygame.K_RIGHT] and self.rect.right  < ROAD_RIGHT:    self.rect.x += self.SPEED
        if keys[pygame.K_UP]    and self.rect.top    > 0:             self.rect.y -= self.SPEED
        if keys[pygame.K_DOWN]  and self.rect.bottom < SCREEN_HEIGHT: self.rect.y += self.SPEED

    def draw(self, surface):
        """Render the blue player car with windshield and taillights."""
        pygame.draw.rect(surface, BLUE, self.rect, border_radius=8)
        pygame.draw.rect(surface, (180, 220, 255),
                         (self.rect.x + 8, self.rect.y + 10, 34, 20), border_radius=4)
        pygame.draw.rect(surface, RED,
                         (self.rect.x + 5, self.rect.bottom - 12, 12, 8), border_radius=2)
        pygame.draw.rect(surface, RED,
                         (self.rect.right - 17, self.rect.bottom - 12, 12, 8), border_radius=2)


# ══════════════════════════════════════════════
# CLASS: EnemyCar
# ══════════════════════════════════════════════
class EnemyCar:
    """Oncoming car that falls from the top.
    Each enemy receives a random speed offset so they all move differently."""

    WIDTH  = 50
    HEIGHT = 80
    COLORS = [RED, GREEN, ORANGE, PURPLE]

    def __init__(self, base_speed):
        self.color = random.choice(self.COLORS)

        # Assign to a random lane out of 3
        lane_width = (ROAD_RIGHT - ROAD_LEFT) // 3
        lane       = random.randint(0, 2)
        x          = ROAD_LEFT + lane * lane_width + (lane_width - self.WIDTH) // 2

        self.rect = pygame.Rect(x, -self.HEIGHT, self.WIDTH, self.HEIGHT)

        # Individual speed = base speed + random offset in [-1, +2]
        # Clamped to minimum 2 so no car can stall
        self.speed = max(2, base_speed + random.randint(-1, 2))

    def update(self):
        """Move the enemy downward by its individual speed."""
        self.rect.y += self.speed

    def is_off_screen(self):
        """True when the car has fully passed the bottom of the screen."""
        return self.rect.top > SCREEN_HEIGHT

    def draw(self, surface):
        """Render the enemy car with windshield and headlights."""
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (200, 230, 200),
                         (self.rect.x + 8, self.rect.y + 10, 34, 20), border_radius=4)
        pygame.draw.rect(surface, YELLOW,
                         (self.rect.x + 5, self.rect.bottom - 12, 12, 8), border_radius=2)
        pygame.draw.rect(surface, YELLOW,
                         (self.rect.right - 17, self.rect.bottom - 12, 12, 8), border_radius=2)


# ══════════════════════════════════════════════
# CLASS: Coin
# ══════════════════════════════════════════════
class Coin:
    """Falling collectible with weighted random type.

    Types:
      Bronze (B) — value 1, common   (60 % chance)
      Silver (S) — value 3, uncommon (30 % chance)
      Gold   (G) — value 5, rare     (10 % chance)

    Heavier/rarer coins have a larger radius so they are visually distinct.
    """

    FALL_SPEED = 4  # pixels per frame, same for all types

    def __init__(self):
        # Pick a coin type from the weighted pool
        self.kind   = random.choice(COIN_POOL)
        self.radius = self.kind["radius"]
        self.value  = self.kind["value"]  # points given to player on pickup

        # Random X within road, keeping the circle fully inside
        x = random.randint(ROAD_LEFT + self.radius, ROAD_RIGHT - self.radius)
        self.center = [x, -self.radius]  # start above screen

        # Axis-aligned bounding box for collision detection
        self.rect = pygame.Rect(
            x - self.radius, -self.radius * 2,
            self.radius * 2, self.radius * 2
        )

    def update(self):
        """Drop the coin and keep the collision rect in sync."""
        self.center[1] += self.FALL_SPEED
        self.rect.center = (int(self.center[0]), int(self.center[1]))

    def is_off_screen(self):
        """True when the coin has passed the bottom of the screen."""
        return self.center[1] > SCREEN_HEIGHT + self.radius

    def draw(self, surface):
        """Render the coin with its type colour, outline, and letter label."""
        cx, cy = int(self.center[0]), int(self.center[1])
        pygame.draw.circle(surface, self.kind["color"],   (cx, cy), self.radius)
        pygame.draw.circle(surface, self.kind["outline"], (cx, cy), self.radius, 2)
        lbl = font_small.render(self.kind["label"], True, BLACK)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))


# ══════════════════════════════════════════════
# FUNCTION: draw_road
# ══════════════════════════════════════════════
def draw_road(surface, offset):
    """Render the scrolling road: grass, asphalt, kerbs, dashed lane markings.
    offset is incremented each frame to animate the dashes downward."""
    surface.fill((34, 120, 34))  # green grass
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, SCREEN_HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_LEFT,      0, 6, SCREEN_HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_RIGHT - 6, 0, 6, SCREEN_HEIGHT))

    lane_width = (ROAD_RIGHT - ROAD_LEFT) // 3
    for i in range(1, 3):
        lx = ROAD_LEFT + lane_width * i
        for y in range(-80 + offset % 80, SCREEN_HEIGHT, 80):
            pygame.draw.rect(surface, WHITE, (lx - 2, y, 4, 40))


# ══════════════════════════════════════════════
# FUNCTION: draw_hud
# ══════════════════════════════════════════════
def draw_hud(surface, score, coin_count, enemy_speed, coins_to_boost):
    """Overlay score, coin count, speed indicator, and boost progress."""
    # Score — top left
    surface.blit(font_medium.render(f"Score: {score}", True, WHITE), (10, 10))
    # Coin total — top right
    coin_lbl = font_medium.render(f"Coins: {coin_count}", True, YELLOW)
    surface.blit(coin_lbl, (SCREEN_WIDTH - coin_lbl.get_width() - 10, 10))
    # Coins until next enemy speed boost — below score
    surface.blit(font_small.render(f"Next boost in: {coins_to_boost} coins", True, SILVER), (10, 40))
    # Coin legend — bottom left
    surface.blit(font_small.render("B=1  S=3  G=5 pts", True, SILVER), (10, SCREEN_HEIGHT - 24))
    # Enemy speed — bottom right
    spd = font_small.render(f"Enemy spd: {enemy_speed}", True, SILVER)
    surface.blit(spd, (SCREEN_WIDTH - spd.get_width() - 10, SCREEN_HEIGHT - 24))


# ══════════════════════════════════════════════
# FUNCTION: game_over_screen
# ══════════════════════════════════════════════
def game_over_screen(score, coin_count):
    """Display the game-over screen; return True to restart, exit on ESC."""
    while True:
        screen.fill(BLACK)
        screen.blit(font_large.render("GAME OVER",               True, RED),
                    (SCREEN_WIDTH // 2 - font_large.size("GAME OVER")[0] // 2, 170))
        screen.blit(font_medium.render(f"Score : {score}",       True, WHITE),
                    (SCREEN_WIDTH // 2 - font_medium.size(f"Score : {score}")[0] // 2, 250))
        screen.blit(font_medium.render(f"Coins : {coin_count}",  True, YELLOW),
                    (SCREEN_WIDTH // 2 - font_medium.size(f"Coins : {coin_count}")[0] // 2, 290))
        screen.blit(font_small.render("R — restart   ESC — quit", True, GRAY),
                    (SCREEN_WIDTH // 2 - font_small.size("R — restart   ESC — quit")[0] // 2, 370))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:                          pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:      return True
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()