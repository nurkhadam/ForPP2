
"""
Practice 10 - Paint

This file starts from the input/event style shown in Nerd Paradise part 6
and extends it into a simple paint program with:
- Rectangle drawing
- Circle drawing
- Eraser
- Color selection

Controls:
- B = brush
- R = rectangle
- C = circle
- E = eraser
- Click a color box to change color
- Hold left mouse button and drag on the canvas
- ESC closes the program
"""

import pygame

pygame.init()

# Window settings
WIDTH = 900
HEIGHT = 650
TOOLBAR_HEIGHT = 80
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Verdana", 18)
small_font = pygame.font.SysFont("Verdana", 14)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (90, 90, 90)
LIGHT_GRAY = (210, 210, 210)
RED = (220, 30, 30)
GREEN = (30, 180, 30)
BLUE = (30, 30, 220)
YELLOW = (255, 220, 0)
PURPLE = (150, 60, 200)

# Tools
TOOL_BRUSH = "brush"
TOOL_RECT = "rectangle"
TOOL_CIRCLE = "circle"
TOOL_ERASER = "eraser"

current_tool = TOOL_BRUSH
current_color = BLUE
brush_size = 8

# Persistent drawing surface
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# State for drawing
drawing = False
start_pos = None
current_pos = None
last_pos = None

# Simple color palette
palette = [
    (BLACK, pygame.Rect(20, 20, 30, 30)),
    (RED, pygame.Rect(60, 20, 30, 30)),
    (GREEN, pygame.Rect(100, 20, 30, 30)),
    (BLUE, pygame.Rect(140, 20, 30, 30)),
    (YELLOW, pygame.Rect(180, 20, 30, 30)),
    (PURPLE, pygame.Rect(220, 20, 30, 30)),
]

# Tool buttons
tool_buttons = {
    TOOL_BRUSH: pygame.Rect(300, 15, 90, 40),
    TOOL_RECT: pygame.Rect(400, 15, 110, 40),
    TOOL_CIRCLE: pygame.Rect(520, 15, 90, 40),
    TOOL_ERASER: pygame.Rect(620, 15, 90, 40),
}


def draw_toolbar():
    """Draw the toolbar with color selection and tool selection."""
    pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))

    title = font.render("Colors", True, BLACK)
    screen.blit(title, (20, 55))

    # Draw color boxes
    for color, rect in palette:
        pygame.draw.rect(screen, color, rect)
        border_width = 3 if color == current_color else 1
        pygame.draw.rect(screen, BLACK, rect, border_width)

    # Draw tool buttons
    for tool_name, rect in tool_buttons.items():
        button_color = YELLOW if current_tool == tool_name else WHITE
        pygame.draw.rect(screen, button_color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        label = font.render(tool_name.capitalize(), True, BLACK)
        screen.blit(
            label,
            (rect.x + rect.width // 2 - label.get_width() // 2,
             rect.y + rect.height // 2 - label.get_height() // 2)
        )

    help_text = small_font.render("Keys: B brush | R rectangle | C circle | E eraser", True, BLACK)
    screen.blit(help_text, (20, 60))


def draw_line(surface, color, start, end, width):
    """Draw a smooth line by stamping circles between two points."""
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy))

    if iterations == 0:
        pygame.draw.circle(surface, color, start, width)
        return

    for i in range(iterations + 1):
        progress = i / iterations
        x = int(start[0] + (end[0] - start[0]) * progress)
        y = int(start[1] + (end[1] - start[1]) * progress)
        pygame.draw.circle(surface, color, (x, y), width)


def toolbar_hit(mouse_pos):
    """Check whether a click is on the toolbar area."""
    return mouse_pos[1] < TOOLBAR_HEIGHT


def canvas_position(mouse_pos):
    """Convert screen coordinates into canvas coordinates."""
    return mouse_pos[0], mouse_pos[1] - TOOLBAR_HEIGHT


def apply_toolbar_click(mouse_pos):
    """Handle color and tool selection from the toolbar."""
    global current_color, current_tool

    for color, rect in palette:
        if rect.collidepoint(mouse_pos):
            current_color = color
            return

    for tool_name, rect in tool_buttons.items():
        if rect.collidepoint(mouse_pos):
            current_tool = tool_name
            return


def draw_preview():
    """Draw the current canvas and, if needed, show a rectangle/circle preview."""
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    if drawing and start_pos and current_pos:
        preview_surface = canvas.copy()

        if current_tool == TOOL_RECT:
            rect = pygame.Rect(
                min(start_pos[0], current_pos[0]),
                min(start_pos[1], current_pos[1]),
                abs(current_pos[0] - start_pos[0]),
                abs(current_pos[1] - start_pos[1]),
            )
            pygame.draw.rect(preview_surface, current_color, rect, 2)

        elif current_tool == TOOL_CIRCLE:
            rect = pygame.Rect(
                min(start_pos[0], current_pos[0]),
                min(start_pos[1], current_pos[1]),
                abs(current_pos[0] - start_pos[0]),
                abs(current_pos[1] - start_pos[1]),
            )
            pygame.draw.ellipse(preview_surface, current_color, rect, 2)

        screen.blit(preview_surface, (0, TOOLBAR_HEIGHT))


def commit_shape():
    """Draw the finished rectangle or circle to the canvas."""
    if not start_pos or not current_pos:
        return

    rect = pygame.Rect(
        min(start_pos[0], current_pos[0]),
        min(start_pos[1], current_pos[1]),
        abs(current_pos[0] - start_pos[0]),
        abs(current_pos[1] - start_pos[1]),
    )

    if current_tool == TOOL_RECT:
        pygame.draw.rect(canvas, current_color, rect, 2)

    elif current_tool == TOOL_CIRCLE:
        pygame.draw.ellipse(canvas, current_color, rect, 2)


def main():
    global drawing, start_pos, current_pos, last_pos, current_tool

    while True:
        pressed = pygame.key.get_pressed()

        alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

        for event in pygame.event.get():
            # Determine if the program should close
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and ctrl_held:
                    return
                if event.key == pygame.K_F4 and alt_held:
                    return
                if event.key == pygame.K_ESCAPE:
                    return

                # Tool selection by keyboard
                if event.key == pygame.K_b:
                    current_tool = TOOL_BRUSH
                elif event.key == pygame.K_r:
                    current_tool = TOOL_RECT
                elif event.key == pygame.K_c:
                    current_tool = TOOL_CIRCLE
                elif event.key == pygame.K_e:
                    current_tool = TOOL_ERASER

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if toolbar_hit(event.pos):
                        apply_toolbar_click(event.pos)
                    else:
                        drawing = True
                        start_pos = canvas_position(event.pos)
                        current_pos = start_pos
                        last_pos = start_pos

                        # For brush and eraser, draw immediately on click.
                        if current_tool == TOOL_BRUSH:
                            pygame.draw.circle(canvas, current_color, start_pos, brush_size)
                        elif current_tool == TOOL_ERASER:
                            pygame.draw.circle(canvas, WHITE, start_pos, brush_size * 2)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    if current_tool in (TOOL_RECT, TOOL_CIRCLE):
                        commit_shape()

                    drawing = False
                    start_pos = None
                    current_pos = None
                    last_pos = None

            if event.type == pygame.MOUSEMOTION and drawing:
                if not toolbar_hit(event.pos):
                    current_pos = canvas_position(event.pos)

                    # Freehand drawing for brush and eraser.
                    if current_tool == TOOL_BRUSH and last_pos is not None:
                        draw_line(canvas, current_color, last_pos, current_pos, brush_size)
                    elif current_tool == TOOL_ERASER and last_pos is not None:
                        draw_line(canvas, WHITE, last_pos, current_pos, brush_size * 2)

                    last_pos = current_pos

        draw_toolbar()
        draw_preview()

        pygame.display.flip()
        clock.tick(60)


main()
