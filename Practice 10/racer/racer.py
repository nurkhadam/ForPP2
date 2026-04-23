
"""
Practice 10 - Racer

This file follows the CodersLegacy racer tutorial structure:
- Player sprite
- Enemy sprite
- Sprite groups
- Speed increase with a user event
- Background, fonts, scoring, and collision handling

Extra tasks added:
- Randomly appearing coins on the road
- Coin counter in the top-right corner
- Code comments
"""

# Imports
import os
import random
import sys
import time

import pygame
from pygame.locals import *


# Initialize pygame
pygame.init()

# Setting up FPS
FPS = 60
FramePerSec = pygame.time.Clock()

# Creating colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (212, 175, 55)

# Other variables for use in the program
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0
COINS_COLLECTED = 0

# Asset paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYER_IMAGE = os.path.join(BASE_DIR, "Player.png")
ENEMY_IMAGE = os.path.join(BASE_DIR, "Enemy.png")
COIN_IMAGE = os.path.join(BASE_DIR, "Coin.png")
BACKGROUND_IMAGE = os.path.join(BASE_DIR, "AnimatedStreet.png")
CRASH_SOUND = os.path.join(BASE_DIR, "crash.wav")

# Setting up fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# Load background
background = pygame.image.load(BACKGROUND_IMAGE)

# Create a display screen
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Racer")


class Enemy(pygame.sprite.Sprite):
    """Enemy car that moves downward and increases the score when it leaves the screen."""

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(ENEMY_IMAGE)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(70, SCREEN_WIDTH - 70), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(70, SCREEN_WIDTH - 70), 0)


class Player(pygame.sprite.Sprite):
    """Player car controlled with the left and right arrow keys."""

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(PLAYER_IMAGE)
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        if self.rect.left > 45:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-5, 0)

        if self.rect.right < SCREEN_WIDTH - 45:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(5, 0)


class Coin(pygame.sprite.Sprite):
    """Coin sprite that appears randomly on the road and moves downward."""

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(COIN_IMAGE)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(65, SCREEN_WIDTH - 65), -20)

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# Setting up sprites
P1 = Player()
E1 = Enemy()

# Creating sprite groups
enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)

# Adding user events
INC_SPEED = pygame.USEREVENT + 1
SPAWN_COIN = pygame.USEREVENT + 2

# Increase speed every second, as shown in the tutorial.
pygame.time.set_timer(INC_SPEED, 1000)

# Try to spawn a coin frequently, but not every event will create one.
pygame.time.set_timer(SPAWN_COIN, 900)


def spawn_coin():
    """Randomly create a coin on the road."""
    # A small random chance keeps coin appearance irregular.
    if random.randint(1, 100) <= 45 and len(coins) < 3:
        coin = Coin()
        coins.add(coin)
        all_sprites.add(coin)


def draw_hud():
    """Draw score on the left and collected coins on the top-right corner."""
    score_text = font_small.render(f"Score: {SCORE}", True, BLACK)
    coin_text = font_small.render(f"Coins: {COINS_COLLECTED}", True, GOLD)

    DISPLAYSURF.blit(score_text, (10, 10))

    coin_rect = coin_text.get_rect()
    coin_rect.topright = (SCREEN_WIDTH - 10, 10)
    DISPLAYSURF.blit(coin_text, coin_rect)


# Game loop
while True:
    # Cycles through all events occurring
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.5

        if event.type == SPAWN_COIN:
            spawn_coin()

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Draw background first
    DISPLAYSURF.blit(background, (0, 0))
    draw_hud()

    # Move and re-draw all sprites
    for entity in list(all_sprites):
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # Coin collection
    collected = pygame.sprite.spritecollide(P1, coins, True)
    if collected:
        COINS_COLLECTED += len(collected)

    # Collision with the enemy
    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.Sound(CRASH_SOUND).play()
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 220))

        final_score = font_small.render(f"Final score: {SCORE}", True, BLACK)
        final_coins = font_small.render(f"Collected coins: {COINS_COLLECTED}", True, BLACK)
        DISPLAYSURF.blit(final_score, (120, 320))
        DISPLAYSURF.blit(final_coins, (95, 350))

        pygame.display.update()

        for entity in all_sprites:
            entity.kill()

        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)
