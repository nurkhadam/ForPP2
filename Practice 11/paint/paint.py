import pygame
import sys
import math

# ──────────────────────────────────────────────
# Initialize pygame
# ──────────────────────────────────────────────
pygame.init()

# ──────────────────────────────────────────────
# Screen layout constants
# ──────────────────────────────────────────────
SCREEN_W  = 900
SCREEN_H  = 640
TOOLBAR_H = 64   # height of the top toolbar in pixels

# ──────────────────────────────────────────────
# UI color constants (RGB)
# ──────────────────────────────────────────────
BG_CANVAS   = (255, 255, 255)   # white drawing surface
BG_TOOLBAR  = ( 40,  40,  50)   # dark toolbar background
HIGHLIGHT   = ( 80, 140, 220)   # active tool button colour
BORDER_CLR  = (100, 100, 110)   # button / palette border colour
TEXT_COLOR  = (220, 220, 220)   # label text colour

# ──────────────────────────────────────────────
# 18-colour palette
# ──────────────────────────────────────────────
PALETTE = [
    (  0,   0,   0), (255, 255, 255), (128, 128, 128), (192, 192, 192),
    (255,   0,   0), (128,   0,   0), (255, 128,   0), (128,  64,   0),
    (255, 255,   0), (128, 128,   0), (  0, 255,   0), (  0, 128,   0),
    (  0, 255, 255), (  0, 128, 128), (  0,   0, 255), (  0,   0, 128),
    (255,   0, 255), (128,   0, 128),
]

# ──────────────────────────────────────────────
# Tool ID constants
# ──────────────────────────────────────────────
TOOL_PEN      = "pen"
TOOL_RECT     = "rect"
TOOL_SQUARE   = "square"        # NEW: always draws a square
TOOL_CIRCLE   = "circle"
TOOL_ERASER   = "eraser"
TOOL_RTRI     = "right_tri"     # NEW: right-angle triangle
TOOL_ETRI     = "equil_tri"     # NEW: equilateral triangle
TOOL_RHOMBUS  = "rhombus"       # NEW: rhombus (diamond)

# ──────────────────────────────────────────────
# Window, clock, font, drawing canvas
# ──────────────────────────────────────────────
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint — Practice 11")
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("Arial", 13, bold=True)

# The canvas is a separate surface so drawing persists between frames
canvas = pygame.Surface((SCREEN_W, SCREEN_H - TOOLBAR_H))
canvas.fill(BG_CANVAS)

# ──────────────────────────────────────────────
# Toolbar UI element rects (fixed positions)
# ──────────────────────────────────────────────
plus_rect  = pygame.Rect(385, 28, 28, 22)    # increase brush size
minus_rect = pygame.Rect(418, 28, 28, 22)    # decrease brush size
clear_rect = pygame.Rect(SCREEN_W - 80, 15, 70, 34)   # clear canvas


# ══════════════════════════════════════════════
# CLASS: ToolButton
# ══════════════════════════════════════════════
class ToolButton:
    """A clickable button in the toolbar that selects a drawing tool."""

    def __init__(self, x, y, w, h, label, tool_id):
        self.rect    = pygame.Rect(x, y, w, h)
        self.label   = label    # text shown on the button
        self.tool_id = tool_id  # string identifier matching a TOOL_* constant

    def draw(self, surface, active_tool):
        """Render the button; highlighted if it is the active tool."""
        color = HIGHLIGHT if self.tool_id == active_tool else BG_TOOLBAR
        pygame.draw.rect(surface, color,      self.rect, border_radius=6)
        pygame.draw.rect(surface, BORDER_CLR, self.rect, 1, border_radius=6)
        lbl = font.render(self.label, True, TEXT_COLOR)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width()  // 2,
                           self.rect.centery - lbl.get_height() // 2))

    def is_clicked(self, pos):
        """Return True if pos is inside this button's rect."""
        return self.rect.collidepoint(pos)


# ══════════════════════════════════════════════
# FUNCTION: draw_toolbar
# ══════════════════════════════════════════════
def draw_toolbar(surface, tool_buttons, cur_tool, cur_color, cur_size, palette_rects):
    """Render the entire toolbar: tool buttons, colour preview, size controls, palette, clear."""
    # Toolbar background
    pygame.draw.rect(surface, BG_TOOLBAR, (0, 0, SCREEN_W, TOOLBAR_H))

    # Draw all tool buttons
    for btn in tool_buttons:
        btn.draw(surface, cur_tool)

    # Current colour preview square
    color_rect = pygame.Rect(330, 10, 44, 44)
    pygame.draw.rect(surface, cur_color,  color_rect, border_radius=4)
    pygame.draw.rect(surface, TEXT_COLOR, color_rect, 2, border_radius=4)

    # Brush size label and +/- buttons
    surface.blit(font.render(f"Size:{cur_size}", True, TEXT_COLOR), (385, 10))
    pygame.draw.rect(surface, BORDER_CLR, plus_rect,  border_radius=4)
    pygame.draw.rect(surface, BORDER_CLR, minus_rect, border_radius=4)
    surface.blit(font.render("+", True, TEXT_COLOR),
                 (plus_rect.centerx  - 4, plus_rect.centery  - 8))
    surface.blit(font.render("-", True, TEXT_COLOR),
                 (minus_rect.centerx - 4, minus_rect.centery - 8))

    # Colour palette swatches
    for idx, rect in enumerate(palette_rects):
        pygame.draw.rect(surface, PALETTE[idx], rect, border_radius=3)
        pygame.draw.rect(surface, BORDER_CLR,   rect, 1, border_radius=3)

    # Clear canvas button
    pygame.draw.rect(surface, (180, 40, 40), clear_rect, border_radius=6)
    surface.blit(font.render("Clear", True, TEXT_COLOR),
                 (clear_rect.centerx - 18, clear_rect.centery - 8))


# ══════════════════════════════════════════════
# FUNCTION: to_canvas
# ══════════════════════════════════════════════
def to_canvas(x, y):
    """Convert screen coordinates to canvas-local coordinates
    (subtracts the toolbar height from y)."""
    return x, y - TOOLBAR_H


# ══════════════════════════════════════════════
# SHAPE DRAWING HELPERS
# All functions draw onto `surface` (either canvas or a preview copy).
# ══════════════════════════════════════════════

def draw_square(surface, color, start, end, size):
    """Draw a square whose side equals the shorter dimension of the drag bounding box.
    The square is anchored at the drag start corner."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    # Use the minimum absolute distance so the shape is always square
    side = min(abs(dx), abs(dy))
    # Preserve the sign of the drag direction
    sx = side if dx >= 0 else -side
    sy = side if dy >= 0 else -side
    rx = min(start[0], start[0] + sx)
    ry = min(start[1], start[1] + sy)
    pygame.draw.rect(surface, color, (rx, ry, side, side), size)


def draw_right_triangle(surface, color, start, end, size):
    """Draw a right-angle triangle.
    The right angle is at start; the other two vertices are (end[0], start[1])
    and start, forming an L-shape.

         start ──── (end[0], start[1])
           |         /
           └── end (not drawn — only 3 vertices matter)
    Actually:
         A = start
         B = (end[0], start[1])   ← horizontal leg end
         C = (start[0], end[1])   ← vertical leg end
    """
    A = start
    B = (end[0], start[1])   # horizontal corner
    C = (start[0], end[1])   # vertical corner
    pygame.draw.polygon(surface, color, [A, B, C], size)


def draw_equilateral_triangle(surface, color, start, end, size):
    """Draw an equilateral triangle.
    The base runs horizontally from start to (end[0], start[1]).
    The apex is centred above (or below) the base at the correct height
    so all three sides are equal.

    Height of equilateral triangle with base b: h = b * sqrt(3) / 2
    """
    base_x1 = start[0]
    base_x2 = end[0]
    base_y  = start[1]
    base    = abs(base_x2 - base_x1)

    if base == 0:
        return

    height = int(base * math.sqrt(3) / 2)

    # Apex direction: above the base if dragging up, below if dragging down
    apex_y = base_y - height if end[1] <= start[1] else base_y + height
    apex_x = (base_x1 + base_x2) // 2

    A = (base_x1, base_y)
    B = (base_x2, base_y)
    C = (apex_x,  apex_y)
    pygame.draw.polygon(surface, color, [A, B, C], size)


def draw_rhombus(surface, color, start, end, size):
    """Draw a rhombus (diamond) fitted inside the drag bounding box.
    The four vertices are the midpoints of the bounding box edges:
      Top    = (cx, start[1])
      Right  = (end[0],  cy)
      Bottom = (cx, end[1])
      Left   = (start[0], cy)
    """
    cx = (start[0] + end[0]) // 2   # horizontal centre
    cy = (start[1] + end[1]) // 2   # vertical centre

    top    = (cx,       start[1])
    right  = (end[0],   cy)
    bottom = (cx,       end[1])
    left   = (start[0], cy)

    pygame.draw.polygon(surface, color, [top, right, bottom, left], size)