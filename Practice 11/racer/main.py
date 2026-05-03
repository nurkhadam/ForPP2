import pygame
import random
import sys

from racer import (
    PlayerCar, EnemyCar, Coin,
    draw_road, draw_hud, game_over_screen,
    screen, clock,
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    COINS_PER_SPEED_UP,
)


def main():
    # ── Game objects ──────────────────────────
    player = PlayerCar()
    enemies: list[EnemyCar] = []
    coins:   list[Coin]     = []

    # ── Counters ──────────────────────────────
    score        = 0    # total points (from avoided enemies + coin values)
    coin_count   = 0    # total coins collected (all types combined)
    coin_points  = 0    # accumulated coin-point value (used for speed trigger)
    road_offset  = 0    # drives the animated lane-marking scroll
    enemy_speed  = 4    # base speed passed to each new EnemyCar

    # ── Spawn timers (milliseconds) ───────────
    ENEMY_EVENT = pygame.USEREVENT + 1
    COIN_EVENT  = pygame.USEREVENT + 2
    pygame.time.set_timer(ENEMY_EVENT, 1500)   # new enemy every 1.5 s
    pygame.time.set_timer(COIN_EVENT,  2000)   # new coin every 2.0 s

    while True:
        clock.tick(FPS)

        # ── Event handling ────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # Spawn a new enemy car at the current base speed
            if event.type == ENEMY_EVENT:
                enemies.append(EnemyCar(enemy_speed))

            # Spawn a coin with 70 % probability to add variety
            if event.type == COIN_EVENT:
                if random.random() < 0.7:
                    coins.append(Coin())

        # ── Player movement ───────────────────
        keys = pygame.key.get_pressed()
        player.move(keys)

        # ── Update enemies ────────────────────
        for e in enemies[:]:
            e.update()
            if e.is_off_screen():
                enemies.remove(e)
                score += 1   # 1 point for each enemy successfully avoided

        # ── Update coins ──────────────────────
        for c in coins[:]:
            c.update()
            if c.is_off_screen():
                coins.remove(c)   # missed coin — just remove it

        # ── Collision: player ↔ enemy ─────────
        for e in enemies:
            if player.rect.colliderect(e.rect):
                # Draw last frame before showing game-over screen
                draw_road(screen, road_offset)
                for obj in enemies: obj.draw(screen)
                for obj in coins:   obj.draw(screen)
                player.draw(screen)
                coins_to_boost = COINS_PER_SPEED_UP - (coin_count % COINS_PER_SPEED_UP)
                draw_hud(screen, score, coin_count, enemy_speed, coins_to_boost)
                pygame.display.flip()

                if game_over_screen(score, coin_count):
                    main()   # restart
                return

        # ── Collision: player ↔ coin ──────────
        for c in coins[:]:
            if player.rect.colliderect(c.rect):
                coins.remove(c)
                score      += c.value   # Bronze=1, Silver=3, Gold=5
                coin_count += c.value   # Coins в HUD тоже считаем по value
                
                # Увеличиваем скорость каждые COINS_PER_SPEED_UP очков монет
                if coin_count // COINS_PER_SPEED_UP > (coin_count - c.value) // COINS_PER_SPEED_UP:
                    enemy_speed = min(enemy_speed + 1, 14)

        # ── Scroll road animation ─────────────
        road_offset = (road_offset + enemy_speed) % 80

        # ── Draw everything ───────────────────
        draw_road(screen, road_offset)
        for e in enemies: e.draw(screen)
        for c in coins:   c.draw(screen)
        player.draw(screen)

        # Coins до следующего буста
        coins_to_boost = COINS_PER_SPEED_UP - (coin_count % COINS_PER_SPEED_UP)
        draw_hud(screen, score, coin_count, enemy_speed, coins_to_boost)

        pygame.display.flip()


if __name__ == "__main__":
    main()