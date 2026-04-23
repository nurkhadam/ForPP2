
"""
Practice 10 - Snake

This project extends a simple lecture-style snake game and adds:
- Border / wall collision checking
- Food generation that avoids walls and the snake body
- Levels based on score
- Faster speed on each new level
- Score and level counters
- Code comments
"""

import random
import sys

import pygame

pygame.init()

# Window and board settings
CELL_SIZE = 20
COLUMNS = 30
ROWS = 30
HUD_HEIGHT = 60
WIDTH = CELL_SIZE * COLUMNS
HEIGHT = CELL_SIZE * ROWS + HUD_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 180, 0)
DARK_GREEN = (0, 100, 0)
RED = (220, 0, 0)
GRAY = (70, 70, 70)
YELLOW = (255, 220, 0)

# Display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

# Fonts
hud_font = pygame.font.SysFont("Verdana", 22)
game_over_font = pygame.font.SysFont("Verdana", 48)

# Snake settings
snake = [(10, 10), (9, 10), (8, 10)]
direction = (1, 0)
next_direction = (1, 0)

# Progress values
score = 0
level = 1
foods_eaten = 0
base_speed = 8

# Food position
food = None


def get_walls(current_level):
    """
    Build the wall set.
    Border walls always exist.
    Higher levels add simple inner obstacles.
    """
    walls = set()

    # Border walls
    for x in range(COLUMNS):
        walls.add((x, 0))
        walls.add((x, ROWS - 1))

    for y in range(ROWS):
        walls.add((0, y))
        walls.add((COLUMNS - 1, y))

    # Additional walls for higher levels
    if current_level >= 2:
        for y in range(6, 24):
            walls.add((15, y))

    if current_level >= 3:
        for x in range(7, 23):
            walls.add((x, 15))

    if current_level >= 4:
        for y in range(5, 11):
            walls.add((7, y))
            walls.add((22, y))
        for y in range(19, 25):
            walls.add((7, y))
            walls.add((22, y))

    return walls


def generate_food():
    """
    Generate food in a random cell that is not on a wall
    and not on the snake body.
    """
    walls = get_walls(level)
    free_cells = []

    for x in range(1, COLUMNS - 1):
        for y in range(1, ROWS - 1):
            position = (x, y)
            if position not in walls and position not in snake:
                free_cells.append(position)

    return random.choice(free_cells)


def draw_cell(position, color):
    """Draw one board cell."""
    x, y = position
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE + HUD_HEIGHT, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)


def draw_board():
    """Draw HUD, walls, snake, and food."""
    screen.fill(BLACK)

    # HUD area
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, HUD_HEIGHT))
    score_text = hud_font.render(f"Score: {score}", True, WHITE)
    level_text = hud_font.render(f"Level: {level}", True, WHITE)
    speed_text = hud_font.render(f"Speed: {base_speed + level - 1}", True, WHITE)
    screen.blit(score_text, (15, 15))
    screen.blit(level_text, (170, 15))
    screen.blit(speed_text, (300, 15))

    # Draw walls
    for wall in get_walls(level):
        draw_cell(wall, GRAY)

    # Draw food
    draw_cell(food, YELLOW)

    # Draw snake
    for index, part in enumerate(snake):
        color = GREEN if index == 0 else DARK_GREEN
        draw_cell(part, color)


def change_level_if_needed():
    """
    Increase level each time the user eats 4 foods.
    Each new level also increases game speed.
    """
    global level
    level = 1 + score // 4


def handle_direction(event_key):
    """Change direction, but prevent a direct turn into the snake's own body."""
    global next_direction

    if event_key == pygame.K_UP and direction != (0, 1):
        next_direction = (0, -1)
    elif event_key == pygame.K_DOWN and direction != (0, -1):
        next_direction = (0, 1)
    elif event_key == pygame.K_LEFT and direction != (1, 0):
        next_direction = (-1, 0)
    elif event_key == pygame.K_RIGHT and direction != (-1, 0):
        next_direction = (1, 0)


def move_snake():
    """
    Move the snake and return False if the snake hits a wall,
    goes outside the playing area, or touches itself.
    """
    global direction, score, foods_eaten, food

    direction = next_direction
    head_x, head_y = snake[0]
    dx, dy = direction
    new_head = (head_x + dx, head_y + dy)

    # Collision with the outside of the playing area
    if new_head[0] < 0 or new_head[0] >= COLUMNS or new_head[1] < 0 or new_head[1] >= ROWS:
        return False

    # Collision with walls
    if new_head in get_walls(level):
        return False

    # Collision with the snake body
    if new_head in snake:
        return False

    snake.insert(0, new_head)

    # Eat food
    if new_head == food:
        score += 1
        foods_eaten += 1
        change_level_if_needed()
        food = generate_food()
    else:
        snake.pop()

    return True


def show_game_over():
    """Display the game-over screen."""
    screen.fill(BLACK)
    text1 = game_over_font.render("Game Over", True, RED)
    text2 = hud_font.render(f"Final score: {score}", True, WHITE)
    text3 = hud_font.render(f"Level reached: {level}", True, WHITE)

    screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 70))
    screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 + 5))
    screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2 + 35))
    pygame.display.flip()
    pygame.time.wait(2000)


# Generate the first food position
food = generate_food()

# Main game loop
running = True
alive = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            else:
                handle_direction(event.key)

    if alive:
        alive = move_snake()
        draw_board()
        pygame.display.flip()

        # Speed increases with each new level
        clock.tick(base_speed + level - 1)
    else:
        show_game_over()
        running = False

pygame.quit()
sys.exit()
