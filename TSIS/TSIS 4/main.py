# ─────────────────────────────────────────────────────────────────────────────
# main.py  — Entry point: game screens (Main Menu, Gameplay, Game Over,
#             Leaderboard, Settings) and the primary game loop.
# Run this file to start the game: python main.py
# ─────────────────────────────────────────────────────────────────────────────

import pygame
import sys

import settings as sett           # settings.py — load/save preferences
from db import Database           # db.py      — PostgreSQL integration
from game import (                # game.py    — all game objects & drawing
    Snake, Food, PoisonFood, PowerUp, Obstacle,
    SoundManager, place_obstacles,
    draw_field, draw_hud,
    screen, clock,
    font_large, font_medium, font_small,
)
from config import (
    WIDTH, HEIGHT, PANEL_H, BASE_FPS, BASE_MOVE, MIN_MOVE,
    FOOD_PER_LEVEL,
    obstacle_count,
    GOLD, RED, SILVER, TEXT_COLOR, PANEL_BG, WALL_COLOR,
    BG_COLOR,
)

# ──────────────────────────────────────────────────────────────────────────────
# Load settings and database once at module level
# ──────────────────────────────────────────────────────────────────────────────
cfg  = sett.load()               # dict with all user preferences
db   = Database(cfg)             # may be None-like if Postgres is unavailable
snd  = SoundManager(cfg.get("sound", True))   # pre-load WAV files

# ──────────────────────────────────────────────────────────────────────────────
# Colour / font shortcuts
# ──────────────────────────────────────────────────────────────────────────────
BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (120, 120, 120)
DKGRAY = ( 40,  40,  50)
CYAN   = (100, 200, 255)

MAX_FOOD        = 2    # maximum normal food items on the field at once
POISON_INTERVAL = 12   # seconds between poison food spawn attempts
POWERUP_INTERVAL = 15  # seconds between power-up spawn attempts

# ──────────────────────────────────────────────────────────────────────────────
# UTILITY DRAWING HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _text(txt: str, font, color=WHITE) -> pygame.Surface:
    """Render text to a surface (helper to avoid repetition)."""
    return font.render(txt, True, color)


def _blit_centered(surf: pygame.Surface, y: int):
    """Blit a surface centered horizontally at the given y coordinate."""
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))


def _draw_button(label: str, rect: pygame.Rect,
                 hover: bool = False, font=None) -> None:
    """Draw a rectangular button with hover highlight."""
    if font is None:
        font = font_medium
    color = (60, 60, 90) if not hover else (90, 90, 140)   # darken when idle
    pygame.draw.rect(screen, color, rect, border_radius=6)
    pygame.draw.rect(screen, WALL_COLOR, rect, 2, border_radius=6)
    lbl = font.render(label, True, WHITE)
    screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                       rect.centery - lbl.get_height() // 2))


def _button_row(labels: list[str], y: int, w=160, h=44, gap=20) -> list[pygame.Rect]:
    """Build a centered row of equally-sized button Rects."""
    total = len(labels) * w + (len(labels) - 1) * gap
    x0    = WIDTH // 2 - total // 2
    rects = []
    for i, _ in enumerate(labels):
        rects.append(pygame.Rect(x0 + i * (w + gap), y, w, h))
    return rects


# ═════════════════════════════════════════════════════════════════════════════
# SCREEN: USERNAME INPUT
# Returns the entered string (min 1 char).
# ═════════════════════════════════════════════════════════════════════════════
def screen_username() -> str:
    """Prompt the player to type a username before the main menu.
    Backspace to delete, Enter to confirm (requires at least one character).
    """
    username = ""
    box      = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 20, 240, 40)

    while True:
        screen.fill(DKGRAY)

        # Title
        _blit_centered(_text("Enter your name", font_large, GOLD), HEIGHT // 2 - 100)

        # Input box
        pygame.draw.rect(screen, (50, 50, 70), box, border_radius=5)
        pygame.draw.rect(screen, WALL_COLOR,   box, 2, border_radius=5)
        # Show typed text inside the box with a blinking cursor effect
        display = username + ("|" if pygame.time.get_ticks() % 800 < 400 else " ")
        inp_lbl = font_medium.render(display, True, WHITE)
        screen.blit(inp_lbl, (box.x + 8, box.y + 8))

        hint = font_small.render("Press ENTER to confirm", True, GRAY)
        _blit_centered(hint, HEIGHT // 2 + 40)

        pygame.display.flip()
        clock.tick(BASE_FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()    # confirm — return the name
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]   # delete last character
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif len(username) < 20:       # cap at 20 characters
                    username += event.unicode  # append typed character


# ═════════════════════════════════════════════════════════════════════════════
# SCREEN: MAIN MENU
# Returns the chosen action string: "play", "leaderboard", "settings", "quit"
# ═════════════════════════════════════════════════════════════════════════════
def screen_main_menu(username: str) -> str:
    """Main menu with four buttons. Mouse hover highlights the active button."""
    buttons = ["Play", "Leaderboard", "Settings", "Quit"]
    # Stack buttons vertically, centered
    rects   = [pygame.Rect(WIDTH // 2 - 100, 200 + i * 60, 200, 44)
               for i in range(len(buttons))]
    actions = ["play", "leaderboard", "settings", "quit"]

    while True:
        screen.fill(DKGRAY)
        _blit_centered(_text("SNAKE", font_large, GOLD), 80)
        sub = font_small.render(f"Player: {username}", True, SILVER)
        _blit_centered(sub, 140)

        mx, my = pygame.mouse.get_pos()
        for rect, label in zip(rects, buttons):
            _draw_button(label, rect, hover=rect.collidepoint(mx, my))

        pygame.display.flip()
        clock.tick(BASE_FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, action in zip(rects, actions):
                    if rect.collidepoint(event.pos):
                        snd.play("click")
                        return action     # caller decides what to do next
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()


# ═════════════════════════════════════════════════════════════════════════════
# SCREEN: LEADERBOARD
# Fetches top 10 from DB and displays a formatted table.
# ═════════════════════════════════════════════════════════════════════════════
def screen_leaderboard():
    """Display top-10 scores fetched from the database."""
    rows   = db.get_leaderboard(10)   # list of dicts from PostgreSQL
    back_r = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 60, 120, 38)

    while True:
        screen.fill(DKGRAY)
        _blit_centered(_text("🏆 Leaderboard", font_large, GOLD), 20)

        if not rows:
            msg = font_medium.render("No records yet — play a game!", True, SILVER)
            _blit_centered(msg, HEIGHT // 2 - 20)
        else:
            # Table header row
            header = f"{'#':>3}  {'Name':<14} {'Score':>6}  {'Lvl':>4}  {'Date'}"
            screen.blit(font_small.render(header, True, CYAN), (20, 80))
            pygame.draw.line(screen, WALL_COLOR, (20, 98), (WIDTH - 20, 98), 1)

            for i, row in enumerate(rows):
                # Format the timestamp to DD.MM.YYYY
                played = row["played_at"]
                date_s = played.strftime("%d.%m.%y") if played else "—"
                line = (f"{row['rank']:>3}  "
                        f"{row['username']:<14} "
                        f"{row['score']:>6}  "
                        f"{row['level_reached']:>4}  "
                        f"{date_s}")
                color = GOLD if i == 0 else (SILVER if i < 3 else TEXT_COLOR)
                screen.blit(font_small.render(line, True, color), (20, 106 + i * 22))

        mx, my = pygame.mouse.get_pos()
        _draw_button("Back", back_r, hover=back_r.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(BASE_FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_r.collidepoint(event.pos):
                    snd.play("click")
                    return
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                return


# ═════════════════════════════════════════════════════════════════════════════
# SCREEN: SETTINGS
# Toggle grid, sound; pick snake head color. Auto-saved on Back.
# ═════════════════════════════════════════════════════════════════════════════
def screen_settings():
    """Settings screen — shows toggles and color presets. Saves on exit."""
    global cfg, snd   # we modify the global config and sound manager

    # Color presets for the snake head (stored as RGB tuples)
    color_presets = [
        ("Green",  (50, 220, 50),  (30, 160, 30),  (10, 90, 10)),
        ("Blue",   (50, 150, 255), (30, 100, 200), (10, 50, 120)),
        ("Yellow", (255, 220, 30), (200, 160, 20), (120, 90, 10)),
        ("Pink",   (255, 100, 180),(200, 60, 140), (120, 30, 80)),
        ("Cyan",   (50, 220, 220), (30, 160, 160), (10, 90, 90)),
    ]

    back_r = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 60, 120, 38)

    while True:
        screen.fill(DKGRAY)
        _blit_centered(_text("⚙  Settings", font_large, GOLD), 20)

        # ── Grid toggle button ──────────────────────────────────────────────
        grid_on  = cfg.get("grid_overlay", True)
        grid_r   = pygame.Rect(WIDTH // 2 - 80, 110, 160, 38)
        grid_lbl = f"Grid: {'ON ✓' if grid_on else 'OFF'}"
        mx, my   = pygame.mouse.get_pos()
        _draw_button(grid_lbl, grid_r, hover=grid_r.collidepoint(mx, my))

        # ── Sound toggle button ─────────────────────────────────────────────
        snd_on  = cfg.get("sound", True)
        snd_r   = pygame.Rect(WIDTH // 2 - 80, 160, 160, 38)
        snd_lbl = f"Sound: {'ON ✓' if snd_on else 'OFF'}"
        _draw_button(snd_lbl, snd_r, hover=snd_r.collidepoint(mx, my))

        # ── Snake color presets ─────────────────────────────────────────────
        screen.blit(font_small.render("Snake color:", True, SILVER), (20, 215))
        color_rects = []
        for i, (name, h_col, b_col, o_col) in enumerate(color_presets):
            cx = 30 + i * 90
            cy = 240
            r  = pygame.Rect(cx, cy, 70, 30)
            color_rects.append((r, h_col, b_col, o_col))
            # Highlight the currently selected color preset
            current_head = tuple(cfg.get("snake_head_color", [50, 220, 50]))
            border = GOLD if current_head == h_col else WALL_COLOR
            pygame.draw.rect(screen, h_col, r, border_radius=4)
            pygame.draw.rect(screen, border, r, 2, border_radius=4)
            lbl = font_small.render(name, True, BLACK if sum(h_col) > 400 else WHITE)
            screen.blit(lbl, (r.centerx - lbl.get_width() // 2, r.centery - lbl.get_height() // 2))

        # ── Back button ─────────────────────────────────────────────────────
        _draw_button("Save & Back", back_r, hover=back_r.collidepoint(mx, my))

        pygame.display.flip()
        clock.tick(BASE_FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if grid_r.collidepoint(pos):
                    cfg["grid_overlay"] = not cfg["grid_overlay"]    # flip toggle
                    snd.play("click")
                elif snd_r.collidepoint(pos):
                    cfg["sound"] = not cfg["sound"]
                    snd.enabled  = cfg["sound"]   # apply immediately to sound manager
                    snd.play("click")
                elif back_r.collidepoint(pos):
                    sett.save(cfg)                # persist settings to disk
                    snd.play("click")
                    return
                else:
                    for r, h_col, b_col, o_col in color_rects:
                        if r.collidepoint(pos):
                            cfg["snake_head_color"]    = list(h_col)
                            cfg["snake_body_color"]    = list(b_col)
                            cfg["snake_outline_color"] = list(o_col)
                            snd.play("click")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sett.save(cfg)
                return


# ═════════════════════════════════════════════════════════════════════════════
# SCREEN: GAME OVER
# Shows final stats; returns "retry" or "menu"
# ═════════════════════════════════════════════════════════════════════════════
def screen_game_over(score: int, level: int, personal_best: int) -> str:
    """Semi-transparent overlay with final stats and action buttons."""
    # Dim the current frame with a 60%-opaque black overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))       # RGBA: black with ~63% opacity
    screen.blit(overlay, (0, 0))

    # Vertical stack of info lines
    lines = [
        (font_large,  "GAME OVER",           RED),
        (font_medium, f"Score: {score}",     GOLD),
        (font_medium, f"Level: {level}",     CYAN),
        (font_small,  f"Best:  {personal_best}", SILVER),
    ]
    total_h = sum(f.size("A")[1] + 10 for f, _, _ in lines)
    y = HEIGHT // 2 - 80
    for fnt, text, color in lines:
        lbl = fnt.render(text, True, color)
        screen.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, y))
        y += fnt.size("A")[1] + 10

    # Action buttons
    retry_r = pygame.Rect(WIDTH // 2 - 170, y + 20, 150, 42)
    menu_r  = pygame.Rect(WIDTH // 2 +  20, y + 20, 150, 42)
    pygame.draw.rect(screen, (50, 100, 50), retry_r, border_radius=6)
    pygame.draw.rect(screen, (100, 50, 50), menu_r,  border_radius=6)
    screen.blit(font_medium.render("Retry",     True, WHITE),
                (retry_r.centerx - 35, retry_r.centery - 12))
    screen.blit(font_medium.render("Main Menu", True, WHITE),
                (menu_r.centerx  - 60, menu_r.centery  - 12))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_r.collidepoint(event.pos):
                    snd.play("click")
                    return "retry"
                if menu_r.collidepoint(event.pos):
                    snd.play("click")
                    return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:      return "retry"
                if event.key == pygame.K_ESCAPE: return "menu"
        clock.tick(30)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN GAMEPLAY LOOP
# Returns when the player dies. Handles all gameplay state internally.
# ═════════════════════════════════════════════════════════════════════════════
def run_game(username: str, player_id: int | None) -> tuple[int, int]:
    """Run one complete game session.

    Returns (final_score, final_level) so the caller can save the result.
    """
    # ── Resolve colors from settings ─────────────────────────────────────────
    head_col, body_col, outline_col = sett.snake_colors(cfg)
    snake = Snake(head_col, body_col, outline_col)

    # ── Initial game state ────────────────────────────────────────────────────
    score       = 0
    level       = 1
    food_eaten  = 0           # counter that resets each level
    move_delay  = BASE_MOVE   # frames between snake steps
    frame_count = 0

    # Personal best fetched once before the game starts
    personal_best = db.get_personal_best(player_id)

    # ── Food / power-up collections ───────────────────────────────────────────
    occupied = set(snake.body)    # helper set to avoid placing items on snake
    foods:    list[Food]      = [Food(occupied)]   # start with one food item
    poison:   list[PoisonFood] = []
    powerups: list[PowerUp]   = []
    obstacles: list[Obstacle] = []    # filled on level-up when level >= 3

    # ── Active power-up effect tracking ──────────────────────────────────────
    active_effect  = None      # "speed_boost" | "slow_motion" | "shield" | None
    effect_end_ms  = 0         # ticks timestamp when current effect expires
    shield_active  = False     # shield is one-use, not time-limited

    # ── Timers using pygame events ────────────────────────────────────────────
    EXTRA_FOOD_EVENT   = pygame.USEREVENT + 1    # try to spawn extra food
    POISON_SPAWN_EVENT = pygame.USEREVENT + 2    # try to spawn poison food
    POWERUP_SPAWN_EVENT = pygame.USEREVENT + 3   # try to spawn a power-up

    pygame.time.set_timer(EXTRA_FOOD_EVENT,    5000)              # every 5 s
    pygame.time.set_timer(POISON_SPAWN_EVENT,  POISON_INTERVAL * 1000)
    pygame.time.set_timer(POWERUP_SPAWN_EVENT, POWERUP_INTERVAL * 1000)

    show_grid = cfg.get("grid_overlay", True)   # read from settings

    # ── GAME LOOP ─────────────────────────────────────────────────────────────
    while True:
        dt = clock.tick(BASE_FPS) / 1000.0   # delta time in seconds
        frame_count += 1

        # ── Event handling ────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP,    pygame.K_w): snake.set_direction( 0, -1)
                if event.key in (pygame.K_DOWN,  pygame.K_s): snake.set_direction( 0,  1)
                if event.key in (pygame.K_LEFT,  pygame.K_a): snake.set_direction(-1,  0)
                if event.key in (pygame.K_RIGHT, pygame.K_d): snake.set_direction( 1,  0)
                if event.key == pygame.K_ESCAPE:
                    # Cancel timers to avoid stale events in the menu
                    pygame.time.set_timer(EXTRA_FOOD_EVENT,    0)
                    pygame.time.set_timer(POISON_SPAWN_EVENT,  0)
                    pygame.time.set_timer(POWERUP_SPAWN_EVENT, 0)
                    return score, level

            # Extra food spawn timer
            if event.type == EXTRA_FOOD_EVENT:
                if len(foods) < MAX_FOOD:
                    occ = set(snake.body) | {obs.pos for obs in obstacles}
                    foods.append(Food(occ))

            # Poison food spawn (one at a time)
            if event.type == POISON_SPAWN_EVENT:
                if not poison:                # only one poison item at a time
                    occ = set(snake.body) | {obs.pos for obs in obstacles}
                    poison.append(PoisonFood(occ))

            # Power-up spawn (one at a time)
            if event.type == POWERUP_SPAWN_EVENT:
                if not powerups:
                    occ = set(snake.body) | {obs.pos for obs in obstacles}
                    powerups.append(PowerUp(occ))

        # ── Power-up effect timeout check ─────────────────────────────────────
        now = pygame.time.get_ticks()
        if active_effect and active_effect != "shield":
            if now >= effect_end_ms:
                active_effect = None   # effect expired — reset to normal speed
                move_delay    = max(MIN_MOVE, BASE_MOVE - (level - 1))  # restore level speed

        # ── Update food timers ────────────────────────────────────────────────
        for f in foods[:]:
            f.update(dt)
            if f.expired:
                foods.remove(f)
        # Always keep at least one food item present
        if not foods:
            occ = set(snake.body) | {obs.pos for obs in obstacles}
            foods.append(Food(occ))

        # Update poison timers
        for p in poison[:]:
            p.update(dt)
            if p.expired:
                poison.remove(p)

        # Update power-up field timers
        for pu in powerups[:]:
            pu.update()
            if pu.expired:
                powerups.remove(pu)

        # ── Snake step (once every move_delay frames) ─────────────────────────
        if frame_count % move_delay == 0:
            obs_set = {obs.pos for obs in obstacles}   # set for O(1) lookup
            alive   = snake.step(obs_set)

            if not alive:
                # Check shield before dying
                if shield_active:
                    shield_active = False    # shield absorbs the hit
                    active_effect = None
                    # Reset head to safe position: undo the lethal move
                    if len(snake.body) > 1:
                        snake.body.pop(0)    # remove the lethal new head
                    snd.play("shield")
                else:
                    # ── Render the last frame before game over overlay ────────
                    draw_field(screen, show_grid, obstacles)
                    for f  in foods:    f.draw(screen)
                    for p  in poison:   p.draw(screen)
                    for pu in powerups: pu.draw(screen)
                    snake.draw(screen)
                    draw_hud(screen, score, level, personal_best,
                             active_effect, effect_end_ms)
                    pygame.display.flip()
                    snd.play("gameover")

                    # Cancel timers so they don't fire in the game-over overlay
                    pygame.time.set_timer(EXTRA_FOOD_EVENT,    0)
                    pygame.time.set_timer(POISON_SPAWN_EVENT,  0)
                    pygame.time.set_timer(POWERUP_SPAWN_EVENT, 0)
                    return score, level   # exit the game loop

            # ── Check head vs. normal food ────────────────────────────────────
            for f in foods[:]:
                if snake.body[0] == f.pos:
                    snake.grow()
                    foods.remove(f)
                    score      += f.value
                    food_eaten += 1
                    snd.play("eat")
                    if not foods:
                        occ = set(snake.body) | {obs.pos for obs in obstacles}
                        foods.append(Food(occ))
                    # ── Level-up check ────────────────────────────────────────
                    if food_eaten >= FOOD_PER_LEVEL:
                        level      += 1
                        food_eaten  = 0
                        move_delay  = max(MIN_MOVE, move_delay - 1)  # speed up
                        snd.play("levelup")
                        # Regenerate obstacles for the new level
                        n_obs = obstacle_count(level)
                        if n_obs > 0:
                            # Safety margin: exclude snake body + 2-cell radius around head
                            hx, hy = snake.body[0]
                            safe = set(snake.body)
                            for dx in range(-2, 3):
                                for dy in range(-2, 3):
                                    safe.add((hx + dx, hy + dy))
                            obstacles = place_obstacles(n_obs, safe)
                    break   # only one food eaten per step

            # ── Check head vs. poison food ────────────────────────────────────
            for p in poison[:]:
                if snake.body[0] == p.pos:
                    poison.remove(p)
                    snd.play("poison")
                    survived = snake.shrink(2)   # remove 2 tail segments
                    if not survived:
                        # Snake too short — treat as death
                        pygame.time.set_timer(EXTRA_FOOD_EVENT,    0)
                        pygame.time.set_timer(POISON_SPAWN_EVENT,  0)
                        pygame.time.set_timer(POWERUP_SPAWN_EVENT, 0)
                        snd.play("gameover")
                        return score, level
                    break

            # ── Check head vs. power-ups ──────────────────────────────────────
            for pu in powerups[:]:
                if snake.body[0] == pu.pos:
                    powerups.remove(pu)
                    snd.play("powerup")
                    active_effect = pu.kind

                    if pu.kind == "speed_boost":
                        # Halve the move delay (faster snake) but respect minimum
                        move_delay   = max(MIN_MOVE, move_delay // 2)
                        effect_end_ms = now + pu.effect_duration

                    elif pu.kind == "slow_motion":
                        # Double the move delay (slower snake)
                        move_delay   = min(BASE_MOVE * 2, move_delay * 2)
                        effect_end_ms = now + pu.effect_duration

                    elif pu.kind == "shield":
                        shield_active = True     # one-use shield
                        effect_end_ms = now + 99999000   # "infinite" for display

                    break

        # ── Render frame ──────────────────────────────────────────────────────
        draw_field(screen, show_grid, obstacles)
        for f  in foods:    f.draw(screen)
        for p  in poison:   p.draw(screen)
        for pu in powerups: pu.draw(screen)
        snake.draw(screen)
        draw_hud(screen, score, level, personal_best, active_effect, effect_end_ms)
        pygame.display.flip()


# ═════════════════════════════════════════════════════════════════════════════
# APPLICATION ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════
def main():
    """Top-level controller: manage screen transitions and DB calls."""
    # Step 1: ask for a username (always shown at startup)
    username  = screen_username()
    player_id = db.get_or_create_player(username)   # create DB record if new

    while True:
        # Step 2: show main menu and get the player's choice
        action = screen_main_menu(username)

        if action == "play":
            # Step 3: run a game session
            final_score, final_level = run_game(username, player_id)

            # Step 4: save result to database
            db.save_session(player_id, final_score, final_level)

            # Update personal best in memory (DB might have it, but skip extra query)
            personal_best = db.get_personal_best(player_id)

            # Step 5: show game-over screen
            outcome = screen_game_over(final_score, final_level, personal_best)
            if outcome == "retry":
                continue          # skip menu and play again immediately
            # else fall through to main menu

        elif action == "leaderboard":
            screen_leaderboard()

        elif action == "settings":
            screen_settings()

        elif action == "quit":
            db.close()            # cleanly close DB connection
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()