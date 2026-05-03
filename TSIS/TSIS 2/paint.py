import pygame
import sys
import math
from collections import deque
from datetime import datetime  # Уақыт бойынша файл атын беру үшін қажет

# --- Инициализация ---
pygame.init()

# --- Константалар ---
SCREEN_W, SCREEN_H = 900, 720
TOOLBAR_H = 120
BG_CANVAS = (255, 255, 255)
BG_TOOLBAR = (40, 40, 50)
HIGHLIGHT = (80, 140, 220)
BORDER_CLR = (100, 100, 110)
TEXT_COLOR = (220, 220, 220)

PALETTE = [
    (0, 0, 0), (255, 255, 255), (128, 128, 128), (192, 192, 192),
    (255, 0, 0), (128, 0, 0), (255, 128, 0), (128, 64, 0),
    (255, 255, 0), (128, 128, 0), (0, 255, 0), (0, 128, 0),
    (0, 255, 255), (0, 128, 128), (0, 0, 255), (0, 0, 128),
    (255, 0, 255), (128, 0, 128),
]

# Құралдар ID-і
TOOL_PEN, TOOL_RECT, TOOL_SQUARE = "pen", "rect", "square"
TOOL_CIRCLE, TOOL_RTRI, TOOL_ETRI = "circle", "right_tri", "equil_tri"
TOOL_RHOMBUS, TOOL_LINE, TOOL_ERASER = "rhombus", "line", "eraser"
TOOL_FILL, TOOL_TEXT = "fill", "text"

# Экран және Шрифт
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Ultimate Paint — TSIS 2")
clock = pygame.time.Clock()
ui_font = pygame.font.SysFont("Arial", 12, bold=True)
canvas_font = pygame.font.SysFont("Arial", 24)

canvas = pygame.Surface((SCREEN_W, SCREEN_H - TOOLBAR_H))
canvas.fill(BG_CANVAS)

# --- ЖАҢА ФУНКЦИЯ: СУРЕТТІ САҚТАУ ---
def save_canvas(surface):
    """Суретті ағымдағы уақытпен файл ретінде сақтайды"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")  #
    filename = f"canvas_{timestamp}.png"  #
    pygame.image.save(surface, filename)  #
    print(f"[Save] Сурет сақталды: {filename}")  #

# --- БАСҚА ФУНКЦИЯЛАР ---
def flood_fill(surface, start_pos, fill_color):
    target_color = surface.get_at(start_pos)[:3]
    fill_rgb = fill_color[:3]
    if target_color == fill_rgb: return
    w, h = surface.get_size()
    queue = deque([start_pos]); visited = {start_pos}
    surface.lock()
    while queue:
        x, y = queue.popleft()
        surface.set_at((x, y), fill_rgb)
        for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                if surface.get_at((nx, ny))[:3] == target_color:
                    visited.add((nx, ny)); queue.append((nx, ny))
    surface.unlock()

def draw_shape(surface, tool, color, start, end, size):
    if tool == TOOL_LINE: pygame.draw.line(surface, color, start, end, size)
    elif tool == TOOL_RECT:
        x, y = min(start[0], end[0]), min(start[1], end[1])
        w, h = abs(end[0] - start[0]), abs(end[1] - start[1])
        if w > 0 and h > 0: pygame.draw.rect(surface, color, (x, y, w, h), size)
    elif tool == TOOL_SQUARE:
        dx, dy = end[0] - start[0], end[1] - start[1]
        side = min(abs(dx), abs(dy))
        sx = start[0] if dx >= 0 else start[0] - side
        sy = start[1] if dy >= 0 else start[1] - side
        pygame.draw.rect(surface, color, (sx, sy, side, side), size)
    elif tool == TOOL_CIRCLE:
        r = int(math.hypot(end[0] - start[0], end[1] - start[1]))
        if r > 0: pygame.draw.circle(surface, color, start, r, size)
    elif tool == TOOL_RTRI: pygame.draw.polygon(surface, color, [start, (end[0], start[1]), (start[0], end[1])], size)
    elif tool == TOOL_ETRI:
        base = abs(end[0] - start[0])
        if base > 0:
            h_tri = int(base * math.sqrt(3) / 2)
            apex_y = start[1] - h_tri if end[1] <= start[1] else start[1] + h_tri
            apex_x = (start[0] + end[0]) // 2
            pygame.draw.polygon(surface, color, [(start[0], start[1]), (end[0], start[1]), (apex_x, apex_y)], size)
    elif tool == TOOL_RHOMBUS:
        cx, cy = (start[0] + end[0]) // 2, (start[1] + end[1]) // 2
        pts = [(cx, start[1]), (end[0], cy), (cx, end[1]), (start[0], cy)]
        pygame.draw.polygon(surface, color, pts, size)

class ToolButton:
    def __init__(self, x, y, w, h, label, tool_id):
        self.rect = pygame.Rect(x, y, w, h); self.label = label; self.tool_id = tool_id
    def draw(self, surface, active_tool):
        color = HIGHLIGHT if self.tool_id == active_tool else BG_TOOLBAR
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, BORDER_CLR, self.rect, 1, border_radius=6)
        lbl = ui_font.render(self.label, True, TEXT_COLOR)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width() // 2, self.rect.centery - lbl.get_height() // 2))

def to_canvas(pos): return (pos[0], pos[1] - TOOLBAR_H)
def to_screen(pos): return (pos[0], pos[1] + TOOLBAR_H)

# --- НЕГІЗГІ ЦИКЛ ---
def main():
    cur_tool, cur_color, cur_size = TOOL_PEN, (0, 0, 0), 5
    drawing = False; start_pos_canvas = (0, 0); last_pos_canvas = (0, 0)
    input_text = ""; text_pos_canvas = (0, 0); typing = False

    btns = [
        ToolButton(10, 10, 65, 30, "Pen", TOOL_PEN), ToolButton(80, 10, 65, 30, "Rect", TOOL_RECT),
        ToolButton(150, 10, 65, 30, "Square", TOOL_SQUARE), ToolButton(10, 45, 65, 30, "Circle", TOOL_CIRCLE),
        ToolButton(80, 45, 65, 30, "R-Tri", TOOL_RTRI), ToolButton(150, 45, 65, 30, "E-Tri", TOOL_ETRI),
        ToolButton(10, 80, 65, 30, "Rhomb", TOOL_RHOMBUS), ToolButton(80, 80, 65, 30, "Line", TOOL_LINE),
        ToolButton(150, 80, 65, 30, "Eraser", TOOL_ERASER), ToolButton(225, 10, 65, 30, "Fill", TOOL_FILL),
        ToolButton(225, 45, 65, 30, "Text", TOOL_TEXT),
    ]

    palette_rects = [pygame.Rect(450 + (i % 9) * 25, 15 + (i // 9) * 25, 20, 20) for i in range(18)]
    plus_rect, minus_rect, clear_rect = pygame.Rect(310, 45, 25, 25), pygame.Rect(340, 45, 25, 25), pygame.Rect(SCREEN_W-80, 15, 70, 35)

    while True:
        m_pos = pygame.mouse.get_pos(); m_canvas = to_canvas(m_pos)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            # ПЕРНЕТАҚТА ОҚИҒАЛАРЫ
            if event.type == pygame.KEYDOWN:
                # Ctrl + S (немесе Command + S) арқылы сақтау
                if (event.key == pygame.K_s) and (pygame.key.get_mods() & pygame.KMOD_CTRL or pygame.key.get_mods() & pygame.KMOD_META):
                    save_canvas(canvas)  #
                
                if typing:
                    if event.key == pygame.K_RETURN:
                        txt_surf = canvas_font.render(input_text, True, cur_color)
                        canvas.blit(txt_surf, text_pos_canvas)
                        input_text, typing = "", False
                    elif event.key == pygame.K_BACKSPACE: input_text = input_text[:-1]
                    else: input_text += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                if m_pos[1] < TOOLBAR_H:
                    for btn in btns:
                        if btn.rect.collidepoint(m_pos): cur_tool = btn.tool_id
                    for i, r in enumerate(palette_rects):
                        if r.collidepoint(m_pos): cur_color = PALETTE[i]
                    if plus_rect.collidepoint(m_pos): cur_size += 2
                    if minus_rect.collidepoint(m_pos): cur_size = max(1, cur_size - 2)
                    if clear_rect.collidepoint(m_pos): canvas.fill(BG_CANVAS)
                else:
                    if cur_tool == TOOL_FILL: flood_fill(canvas, m_canvas, cur_color)
                    elif cur_tool == TOOL_TEXT: typing = True; text_pos_canvas = m_canvas; input_text = ""
                    else: drawing = True; start_pos_canvas = m_canvas; last_pos_canvas = m_canvas

            if event.type == pygame.MOUSEBUTTONUP:
                if drawing:
                    if cur_tool not in [TOOL_PEN, TOOL_ERASER]:
                        draw_shape(canvas, cur_tool, cur_color, start_pos_canvas, m_canvas, cur_size)
                    drawing = False

            if event.type == pygame.MOUSEMOTION and drawing:
                if cur_tool == TOOL_PEN:
                    pygame.draw.line(canvas, cur_color, last_pos_canvas, m_canvas, cur_size)
                    pygame.draw.circle(canvas, cur_color, m_canvas, cur_size // 2)
                    last_pos_canvas = m_canvas
                elif cur_tool == TOOL_ERASER:
                    pygame.draw.line(canvas, BG_CANVAS, last_pos_canvas, m_canvas, cur_size * 4)
                    last_pos_canvas = m_canvas

        screen.fill(BG_CANVAS); screen.blit(canvas, (0, TOOLBAR_H))
        if drawing and cur_tool not in [TOOL_PEN, TOOL_ERASER]:
            draw_shape(screen, cur_tool, cur_color, to_screen(start_pos_canvas), m_pos, cur_size)
        if typing:
            t_surf = canvas_font.render(input_text + "|", True, cur_color)
            screen.blit(t_surf, to_screen(text_pos_canvas))

        pygame.draw.rect(screen, BG_TOOLBAR, (0, 0, SCREEN_W, TOOLBAR_H))
        for btn in btns: btn.draw(screen, cur_tool)
        for i, r in enumerate(palette_rects):
            pygame.draw.rect(screen, PALETTE[i], r); pygame.draw.rect(screen, BORDER_CLR, r, 1)
        pygame.draw.rect(screen, cur_color, (310, 10, 55, 30), border_radius=4)
        screen.blit(ui_font.render(f"Size: {cur_size}", True, TEXT_COLOR), (375, 15))
        pygame.draw.rect(screen, BORDER_CLR, plus_rect); screen.blit(ui_font.render("+", True, TEXT_COLOR), (318, 50))
        pygame.draw.rect(screen, BORDER_CLR, minus_rect); screen.blit(ui_font.render("-", True, TEXT_COLOR), (349, 50))
        pygame.draw.rect(screen, (180, 40, 40), clear_rect); screen.blit(ui_font.render("Clear", True, TEXT_COLOR), (SCREEN_W-65, 25))
        screen.blit(ui_font.render("Ctrl+S: Save", True, (160, 160, 170)), (SCREEN_W - 120, 85))  # Сақтау анықтамасы

        pygame.display.flip()
        clock.tick(120)

if __name__ == "__main__":
    main()