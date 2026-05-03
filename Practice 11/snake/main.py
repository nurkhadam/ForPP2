import pygame
import sys

from snake import (
    Snake, Food,
    draw_field, draw_hud, end_screen,
    screen, clock,
    BASE_FPS, BASE_MOVE, FOOD_PER_LEVEL,
)

# Maximum number of food items allowed on screen at once
MAX_FOOD = 2


def main():
    snake = Snake()

    # Start with one piece of food on the field
    foods: list[Food] = [Food(snake.body)]

    score       = 0
    level       = 1
    food_eaten  = 0    # food eaten on the current level (resets on level-up)
    move_delay  = BASE_MOVE   # frames between snake steps
    frame_count = 0

    # Timer for spawning additional food items (milliseconds)
    EXTRA_FOOD_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(EXTRA_FOOD_EVENT, 5000)   # attempt spawn every 5 s

    while True:
        # dt = time elapsed this frame in seconds (used for food timers)
        dt = clock.tick(BASE_FPS) / 1000.0
        frame_count += 1

        # ── Event handling ────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                # Direction controls: arrow keys or WASD
                if event.key in (pygame.K_UP,    pygame.K_w): snake.set_direction( 0, -1)
                if event.key in (pygame.K_DOWN,  pygame.K_s): snake.set_direction( 0,  1)
                if event.key in (pygame.K_LEFT,  pygame.K_a): snake.set_direction(-1,  0)
                if event.key in (pygame.K_RIGHT, pygame.K_d): snake.set_direction( 1,  0)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

            # Periodically spawn an extra food item (up to MAX_FOOD on screen)
            if event.type == EXTRA_FOOD_EVENT:
                if len(foods) < MAX_FOOD:
                    foods.append(Food(snake.body))

        # ── Update food timers ────────────────
        for f in foods[:]:
            f.update(dt)
            if f.expired:
                foods.remove(f)   # timed food has vanished — remove it
                # Ensure at least one food is always present
                if not foods:
                    foods.append(Food(snake.body))

        # ── Snake step (once every move_delay frames) ──
        if frame_count % move_delay == 0:
            alive = snake.step()

            if not alive:
                # Render final frame, then show game-over screen
                draw_field(screen)
                for f in foods: f.draw(screen)
                snake.draw(screen)
                draw_hud(screen, score, level)
                pygame.display.flip()

                if end_screen(score, level):
                    main()   # restart
                return

            # ── Check if the head is on any food ──
            for f in foods[:]:
                if snake.body[0] == f.pos:
                    snake.grow()
                    foods.remove(f)
                    score += f.value   # фиксированные очки: 1 / 2 / 3 / 5
                    food_eaten += 1

                    # Always keep at least one food on the field
                    if not foods:
                        foods.append(Food(snake.body))

                    # Level up after eating FOOD_PER_LEVEL items
                    if food_eaten >= FOOD_PER_LEVEL:
                        level      += 1
                        food_eaten  = 0
                        move_delay  = max(2, move_delay - 1)   # speed up snake
                    break   # only eat one food per step

        # ── Render ────────────────────────────
        draw_field(screen)
        for f in foods: f.draw(screen)
        snake.draw(screen)
        draw_hud(screen, score, level)
        pygame.display.flip()


if __name__ == "__main__":
    main()