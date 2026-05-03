"""
ui.py  —  TSIS 3
All non-gameplay screens: Main Menu, Settings, Leaderboard, Username entry.
Built entirely with pygame — no external UI libraries.
"""

import pygame
import sys
from racer import (
    screen, clock, font_large, font_medium, font_small, font_tiny,
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WHITE, BLACK, GRAY, RED, YELLOW, GREEN, BLUE, CYAN, ORANGE,
    SILVER, GOLD, BRONZE, LIME, PURPLE, DARK,
    CAR_COLOR_MAP,
)
from persistence import load_leaderboard, load_settings, save_settings


# ── Palette ───────────────────────────────────────────────────────────────────
BG       = ( 8,  8, 18)
ACCENT   = (255, 200,  0)
DIM      = ( 60,  60,  80)
HIGHLIGHT= (255, 255, 255)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fill_bg(surface):
    surface.fill(BG)
    # Subtle road lines
    for x in range(SCREEN_WIDTH // 2 - 60, SCREEN_WIDTH // 2 + 61, 120):
        for y in range(0, SCREEN_HEIGHT, 80):
            pygame.draw.rect(surface, ( 25, 25, 40), (x - 2, y, 4, 40))


def _draw_centered(font, text, color, y, surface=None):
    if surface is None:
        surface = screen
    surf = font.render(text, True, color)
    surface.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))


def _button(label, x, y, w, h, hovered, font=font_medium):
    color  = ACCENT   if hovered else DIM
    border = HIGHLIGHT if hovered else GRAY
    pygame.draw.rect(screen, color,  (x, y, w, h), border_radius=8)
    pygame.draw.rect(screen, border, (x, y, w, h), 2, border_radius=8)
    lbl = font.render(label, True, BLACK if hovered else WHITE)
    screen.blit(lbl, (x + w // 2 - lbl.get_width() // 2,
                       y + h // 2 - lbl.get_height() // 2))
    return pygame.Rect(x, y, w, h)


# ══════════════════════════════════════════════
# USERNAME ENTRY
# ══════════════════════════════════════════════

def username_screen(default_name: str = "") -> str:
    """Returns the entered username string."""
    name = list(default_name)
    cursor_visible = True
    cursor_timer   = 0

    while True:
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        if now - cursor_timer > 500:
            cursor_visible = not cursor_visible
            cursor_timer   = now

        _fill_bg(screen)
        _draw_centered(font_large,  "ENTER YOUR NAME", ACCENT, 140)
        _draw_centered(font_small,  "Press ENTER to continue", GRAY, 210)

        # Input box
        box_w, box_h = 320, 50
        bx = SCREEN_WIDTH // 2 - box_w // 2
        by = 270
        pygame.draw.rect(screen, DIM, (bx, by, box_w, box_h), border_radius=8)
        pygame.draw.rect(screen, ACCENT, (bx, by, box_w, box_h), 2, border_radius=8)

        display = "".join(name) + ("|" if cursor_visible else " ")
        txt = font_medium.render(display, True, WHITE)
        screen.blit(txt, (bx + 12, by + box_h // 2 - txt.get_height() // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    return "".join(name).strip()
                elif event.key == pygame.K_BACKSPACE:
                    if name:
                        name.pop()
                elif event.key == pygame.K_ESCAPE:
                    return default_name or "Player"
                elif len(name) < 16 and event.unicode.isprintable():
                    name.append(event.unicode)


# ══════════════════════════════════════════════
# MAIN MENU
# ══════════════════════════════════════════════

def main_menu() -> str:
    """Returns: 'play' | 'leaderboard' | 'settings' | 'quit'"""
    items   = [("PLAY",        "play"),
               ("LEADERBOARD", "leaderboard"),
               ("SETTINGS",    "settings"),
               ("QUIT",        "quit")]
    selected = 0
    btn_w, btn_h = 260, 50
    bx = SCREEN_WIDTH // 2 - btn_w // 2

    while True:
        clock.tick(FPS)
        mouse = pygame.mouse.get_pos()

        _fill_bg(screen)

        # Title
        _draw_centered(font_large, "RACER", ACCENT, 70)
        _draw_centered(font_small, "TSIS 3  —  Advanced Edition", SILVER, 120)

        # Buttons
        btns = []
        for i, (label, _) in enumerate(items):
            y       = 190 + i * 65
            hovered = pygame.Rect(bx, y, btn_w, btn_h).collidepoint(mouse)
            btns.append(_button(label, bx, y, btn_w, btn_h, hovered or selected == i))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(items)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return items[selected][1]
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(btns):
                    if rect.collidepoint(event.pos):
                        return items[i][1]


# ══════════════════════════════════════════════
# SETTINGS SCREEN
# ══════════════════════════════════════════════

def settings_screen() -> dict:
    """Edits settings in-place; returns updated settings dict."""
    cfg = load_settings()

    color_options = list(CAR_COLOR_MAP.keys())
    diff_options  = ["easy", "normal", "hard"]

    def next_option(lst, current):
        idx = lst.index(current) if current in lst else 0
        return lst[(idx + 1) % len(lst)]

    BTN_W, BTN_H = 220, 44
    BX = SCREEN_WIDTH // 2 - BTN_W // 2

    while True:
        clock.tick(FPS)
        mouse = pygame.mouse.get_pos()

        _fill_bg(screen)
        _draw_centered(font_large,  "SETTINGS", ACCENT, 50)

        rows = [
            ("Sound",      "sound",      str(cfg["sound"])),
            ("Car Color",  "car_color",  cfg["car_color"]),
            ("Difficulty", "difficulty", cfg["difficulty"]),
        ]

        rects = {}
        for i, (label, key, value) in enumerate(rows):
            y = 150 + i * 80
            # Row label
            lbl_s = font_small.render(label, True, SILVER)
            screen.blit(lbl_s, (BX, y - 20))
            # Value button
            hovered = pygame.Rect(BX, y, BTN_W, BTN_H).collidepoint(mouse)
            rects[key] = _button(value.upper(), BX, y, BTN_W, BTN_H, hovered)

            # Car color preview swatch
            if key == "car_color":
                c = CAR_COLOR_MAP.get(cfg["car_color"], BLUE)
                pygame.draw.rect(screen, c, (BX + BTN_W + 16, y + 4, 36, 36), border_radius=6)

        # Back button
        back_y   = 450
        back_h   = pygame.Rect(BX, back_y, BTN_W, BTN_H).collidepoint(mouse)
        back_btn = _button("BACK", BX, back_y, BTN_W, BTN_H, back_h)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_settings(cfg)
                return cfg
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.collidepoint(event.pos):
                    save_settings(cfg)
                    return cfg
                for key, rect in rects.items():
                    if rect.collidepoint(event.pos):
                        if key == "sound":
                            cfg["sound"] = not cfg["sound"]
                        elif key == "car_color":
                            cfg["car_color"] = next_option(color_options, cfg["car_color"])
                        elif key == "difficulty":
                            cfg["difficulty"] = next_option(diff_options, cfg["difficulty"])


# ══════════════════════════════════════════════
# LEADERBOARD SCREEN
# ══════════════════════════════════════════════

def leaderboard_screen():
    entries = load_leaderboard()
    BTN_W, BTN_H = 180, 44
    bx = SCREEN_WIDTH // 2 - BTN_W // 2

    while True:
        clock.tick(FPS)
        mouse = pygame.mouse.get_pos()

        _fill_bg(screen)
        _draw_centered(font_large, "TOP 10", ACCENT, 30)

        # Header
        _draw_h_row(65, "#", "NAME", "SCORE", "DIST", "COINS", SILVER)

        # Entries
        rank_colors = [GOLD, SILVER, BRONZE]
        for i, e in enumerate(entries[:10]):
            y   = 95 + i * 47
            col = rank_colors[i] if i < 3 else WHITE
            _draw_h_row(y, str(i + 1),
                        e.get("name", "?")[:10],
                        str(e.get("score", 0)),
                        str(e.get("distance", 0)) + "m",
                        str(e.get("coins", 0)),
                        col)

        if not entries:
            _draw_centered(font_medium, "No entries yet!", GRAY, 250)

        # Back
        hov = pygame.Rect(bx, 565, BTN_W, BTN_H).collidepoint(mouse)
        back = _button("BACK", bx, 565, BTN_W, BTN_H, hov)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_m):
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    return


def _draw_h_row(y, rank, name, score, dist, coins, color):
    cols = [50, 100, 230, 330, 415]
    vals = [rank, name, score, dist, coins]
    for x, v in zip(cols, vals):
        s = font_small.render(str(v), True, color)
        screen.blit(s, (x, y))