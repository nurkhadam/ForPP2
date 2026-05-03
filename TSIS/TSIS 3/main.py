"""
main.py  —  TSIS 3: Racer Game — Advanced Driving, Leaderboard & Power-Ups
Run:  python main.py
"""

import shutil, os
# Удаляем кэш чтобы всегда использовался свежий код
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")

import pygame
import random
import sys

from racer import (
    PlayerCar, EnemyCar, Coin, PowerUp, Obstacle, NitroStrip,
    draw_road, draw_hud, game_over_screen,
    screen, clock,
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    COINS_PER_SPEED_UP, DIFFICULTY_PRESETS, POWERUP_TIMEOUT,
    NITRO_DURATION, DISTANCE_PER_FRAME, NITRO_SCROLL_BONUS,
    CAR_COLOR_MAP, BLUE,
)
from persistence import load_settings, add_leaderboard_entry
from ui import main_menu, settings_screen, leaderboard_screen, username_screen
from sounds import SoundManager


def play(settings: dict):
    diff   = settings.get("difficulty", "normal")
    e_ms, c_ms, o_ms, base_spd = DIFFICULTY_PRESETS[diff]
    car_color = CAR_COLOR_MAP.get(settings.get("car_color", "blue"), BLUE)
    username  = settings.get("username", "Player") or "Player"

    sfx = SoundManager(enabled=True)
    sfx.start_engine()

    player   = PlayerCar(color=car_color)
    enemies  = []
    coins    = []
    powerups = []
    obstacles= []
    strips   = []

    score        = 0
    coin_count   = 0
    distance     = 0
    road_offset  = 0
    enemy_speed  = base_spd

    ENEMY_EV    = pygame.USEREVENT + 1
    COIN_EV     = pygame.USEREVENT + 2
    OBSTACLE_EV = pygame.USEREVENT + 3
    STRIP_EV    = pygame.USEREVENT + 4
    POWERUP_EV  = pygame.USEREVENT + 5

    pygame.time.set_timer(ENEMY_EV,    e_ms)
    pygame.time.set_timer(COIN_EV,     c_ms)
    pygame.time.set_timer(OBSTACLE_EV, o_ms)
    pygame.time.set_timer(STRIP_EV,    5000)
    pygame.time.set_timer(POWERUP_EV,  7000)

    last_scale_dist = 0

    def scale_difficulty():
        nonlocal enemy_speed, e_ms, o_ms
        enemy_speed = min(enemy_speed + 1, 16)
        e_ms  = max(600,  int(e_ms  * 0.92))
        o_ms  = max(800,  int(o_ms  * 0.92))
        pygame.time.set_timer(ENEMY_EV,    e_ms)
        pygame.time.set_timer(OBSTACLE_EV, o_ms)
        sfx.set_engine_pitch(enemy_speed)

    active_pu = None
    pu_end_ms = 0

    while True:
        clock.tick(FPS)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sfx.stop_all(); pygame.quit(); sys.exit()
            if event.type == ENEMY_EV:
                enemies.append(EnemyCar(enemy_speed, player.rect))
            if event.type == COIN_EV:
                if random.random() < 0.7:
                    coins.append(Coin())
            if event.type == OBSTACLE_EV:
                if random.random() < 0.65:
                    obstacles.append(Obstacle(enemy_speed, player.rect))
            if event.type == STRIP_EV:
                if random.random() < 0.4:
                    strips.append(NitroStrip())
            if event.type == POWERUP_EV:
                if len(powerups) == 0:
                    kind = random.choice(["nitro", "shield", "repair"])
                    powerups.append(PowerUp(kind, now))

        distance += DISTANCE_PER_FRAME
        if distance - last_scale_dist >= 500:
            last_scale_dist = distance
            scale_difficulty()

        keys = pygame.key.get_pressed()
        player.move(keys)
        player.update(now)

        nitro_extra = NITRO_SCROLL_BONUS if player.nitro_active else 0

        for e in enemies[:]:
            e.update(nitro_extra)
            if e.is_off_screen():
                enemies.remove(e); score += 1

        for c in coins[:]:
            c.update(nitro_extra)
            if c.is_off_screen(): coins.remove(c)

        for o in obstacles[:]:
            o.update(nitro_extra)
            if o.is_off_screen(): obstacles.remove(o)

        for s in strips[:]:
            s.update(nitro_extra)
            if s.is_off_screen(): strips.remove(s)

        for p in powerups[:]:
            p.update(nitro_extra)
            if p.is_off_screen() or p.is_expired(now):
                powerups.remove(p)

        # Nitro circle
        for s in strips[:]:
            if not s.triggered and player.rect.colliderect(s.rect):
                s.triggered = True
                player.activate_nitro(now)
                active_pu = "nitro"; pu_end_ms = now + NITRO_DURATION
                strips.remove(s)
                sfx.play("nitro")

        # Power-up collection
        for p in powerups[:]:
            if player.rect.colliderect(p.rect):
                powerups.remove(p)
                if p.kind == "nitro":
                    player.activate_nitro(now)
                    active_pu = "nitro"; pu_end_ms = now + NITRO_DURATION
                    sfx.play("nitro")
                elif p.kind == "shield":
                    player.activate_shield()
                    active_pu = "shield"; pu_end_ms = now + 999_999
                    sfx.play("shield")
                elif p.kind == "repair":
                    player.repair()
                    active_pu = "repair"; pu_end_ms = now + 800
                    sfx.play("powerup")
                score += 10

        if active_pu == "nitro"  and not player.nitro_active:  active_pu = None
        if active_pu == "shield" and not player.shield_active: active_pu = None
        if active_pu == "repair" and now > pu_end_ms:          active_pu = None

        # Coins
        for c in coins[:]:
            if player.rect.colliderect(c.rect):
                coins.remove(c)
                score += c.value; coin_count += c.value
                sfx.play("gold_coin" if c.value == 5 else "coin")
                if coin_count // COINS_PER_SPEED_UP > (coin_count - c.value) // COINS_PER_SPEED_UP:
                    enemy_speed = min(enemy_speed + 1, 16)
                    sfx.set_engine_pitch(enemy_speed)

        # Obstacle collision
        for o in obstacles[:]:
            if player.rect.colliderect(o.rect):
                dmg = o.kind_def.get("damage", 1)
                died = player.take_damage(dmg)
                obstacles.remove(o)
                if died:
                    sfx.play("crash"); sfx.stop_engine()
                    _draw_final_frame(player, enemies, coins, powerups, obstacles, strips,
                                      road_offset, score, coin_count, enemy_speed,
                                      _coins_to_boost(coin_count), distance,
                                      _pu_info(active_pu, pu_end_ms, now))
                    result = game_over_screen(score, coin_count, distance)
                    add_leaderboard_entry(username, score, distance, coin_count)
                    return result
                else:
                    sfx.play("obstacle_hit")

        # Enemy collision — instant death
        for e in enemies[:]:
            if player.rect.colliderect(e.rect):
                if player.shield_active:
                    player.shield_active = False
                    player.invincible_flash = 90
                    enemies.remove(e)
                    sfx.play("shield")
                    break
                sfx.play("crash"); sfx.stop_engine()
                _draw_final_frame(player, enemies, coins, powerups, obstacles, strips,
                                  road_offset, score, coin_count, enemy_speed,
                                  _coins_to_boost(coin_count), distance,
                                  _pu_info(active_pu, pu_end_ms, now))
                result = game_over_screen(score, coin_count, distance)
                add_leaderboard_entry(username, score, distance, coin_count)
                return result

        road_offset = (road_offset + enemy_speed + nitro_extra) % 80

        draw_road(screen, road_offset)
        for s in strips:    s.draw(screen)
        for o in obstacles: o.draw(screen)
        for e in enemies:   e.draw(screen)
        for c in coins:     c.draw(screen)
        for p in powerups:  p.draw(screen, now)
        player.draw(screen)
        draw_hud(screen, score, coin_count, enemy_speed,
                 _coins_to_boost(coin_count), distance,
                 _pu_info(active_pu, pu_end_ms, now),
                 player.hp, player.MAX_HP)
        pygame.display.flip()


def _coins_to_boost(coin_count):
    return COINS_PER_SPEED_UP - (coin_count % COINS_PER_SPEED_UP)

def _pu_info(active_pu, pu_end_ms, now):
    if active_pu is None: return None
    return (active_pu, max(0, pu_end_ms - now))

def _draw_final_frame(player, enemies, coins, powerups, obstacles, strips,
                      road_offset, score, coin_count, enemy_speed,
                      coins_to_boost, distance, pu_info):
    draw_road(screen, road_offset)
    for s in strips:    s.draw(screen)
    for o in obstacles: o.draw(screen)
    for e in enemies:   e.draw(screen)
    for c in coins:     c.draw(screen)
    for p in powerups:  p.draw(screen, pygame.time.get_ticks())
    player.draw(screen)
    draw_hud(screen, score, coin_count, enemy_speed, coins_to_boost, distance, pu_info,
             player.hp, player.MAX_HP)
    pygame.display.flip()


def run():
    settings = load_settings()
    from persistence import save_settings

    # Always ask for username on every launch
    settings["username"] = username_screen(settings.get("username", ""))
    save_settings(settings)

    while True:
        choice = main_menu()
        if choice == "play":
            result = play(settings)
            if result == "retry":
                continue
        elif choice == "leaderboard":
            leaderboard_screen()
        elif choice == "settings":
            settings = settings_screen()
            if not settings.get("username"):
                settings["username"] = username_screen()
                save_settings(settings)
        elif choice == "quit":
            pygame.quit(); sys.exit()


if __name__ == "__main__":
    run()