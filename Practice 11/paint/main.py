import pygame
import sys
import math

from paint import (
    ToolButton, draw_toolbar, to_canvas,
    draw_square, draw_right_triangle,
    draw_equilateral_triangle, draw_rhombus,
    screen, clock, canvas, font,
    SCREEN_W, SCREEN_H, TOOLBAR_H,
    BG_CANVAS, BG_TOOLBAR, BORDER_CLR,
    PALETTE,
    TOOL_PEN, TOOL_RECT, TOOL_SQUARE, TOOL_CIRCLE,
    TOOL_ERASER, TOOL_RTRI, TOOL_ETRI, TOOL_RHOMBUS,
    plus_rect, minus_rect, clear_rect,
)


def main():
    # ── Tool buttons ──────────────────────────
    # Two rows of 4 buttons each fit comfortably in the 900-px wide toolbar.
    # Row 1: basic tools
    # Row 2: new shape tools (Practice 11)
    tool_buttons = [
        ToolButton( 10,  4, 58, 26, "✏ Pen",     TOOL_PEN),
        ToolButton( 72,  4, 58, 26, "▭ Rect",    TOOL_RECT),
        ToolButton(134,  4, 62, 26, "□ Square",  TOOL_SQUARE),
        ToolButton(200,  4, 62, 26, "○ Circle",  TOOL_CIRCLE),
        ToolButton(266,  4, 58, 26, "⌫ Erase",   TOOL_ERASER),
        # New shapes on second row
        ToolButton( 10, 34, 72, 26, "◺ R-Tri",   TOOL_RTRI),
        ToolButton( 86, 34, 72, 26, "△ E-Tri",   TOOL_ETRI),
        ToolButton(162, 34, 72, 26, "◇ Rhombus", TOOL_RHOMBUS),
    ]

    # Build palette swatch rects (18 colours, 9 per row, starting at x=455)
    palette_rects = []
    for i in range(len(PALETTE)):
        rx = 455 + (i % 9) * 22   # x: advance 22 px per swatch in a row of 9
        ry = 5   + (i // 9) * 22  # y: next row after every 9 swatches
        palette_rects.append(pygame.Rect(rx, ry, 20, 20))

    # ── State variables ───────────────────────
    cur_tool  = TOOL_PEN
    cur_color = (0, 0, 0)
    cur_size  = 4        # brush / outline thickness
    drawing   = False    # True while the left mouse button is held on the canvas
    start_pos = None     # canvas-coordinate where the drag began
    preview   = None     # temporary copy of canvas used for live shape preview

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── Mouse button pressed ──────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos

                if y < TOOLBAR_H:
                    # Click in the toolbar area ─────────────────────────────

                    # Check each tool button
                    for btn in tool_buttons:
                        if btn.is_clicked((x, y)):
                            cur_tool = btn.tool_id

                    # Check colour palette swatches
                    for idx, rect in enumerate(palette_rects):
                        if rect.collidepoint(x, y):
                            cur_color = PALETTE[idx]

                    # Size controls and clear button
                    if plus_rect.collidepoint(x, y):
                        cur_size = min(50, cur_size + 1)
                    elif minus_rect.collidepoint(x, y):
                        cur_size = max(1, cur_size - 1)
                    elif clear_rect.collidepoint(x, y):
                        canvas.fill(BG_CANVAS)   # wipe the entire canvas

                else:
                    # Click on the canvas area ──────────────────────────────
                    drawing   = True
                    start_pos = to_canvas(x, y)

                    # Pen and eraser begin drawing immediately on press
                    if cur_tool in (TOOL_PEN, TOOL_ERASER):
                        color = BG_CANVAS if cur_tool == TOOL_ERASER else cur_color
                        pygame.draw.circle(canvas, color, start_pos, cur_size)

            # ── Mouse button released ─────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing:
                    end_pos = to_canvas(*event.pos)

                    # Commit the final shape to the canvas
                    if cur_tool == TOOL_RECT and start_pos:
                        rx = min(start_pos[0], end_pos[0])
                        ry = min(start_pos[1], end_pos[1])
                        rw = abs(end_pos[0] - start_pos[0])
                        rh = abs(end_pos[1] - start_pos[1])
                        pygame.draw.rect(canvas, cur_color, (rx, ry, rw, rh), cur_size)

                    elif cur_tool == TOOL_SQUARE and start_pos:
                        draw_square(canvas, cur_color, start_pos, end_pos, cur_size)

                    elif cur_tool == TOOL_CIRCLE and start_pos:
                        rad = int(math.hypot(end_pos[0] - start_pos[0],
                                             end_pos[1] - start_pos[1]))
                        if rad > 0:
                            pygame.draw.circle(canvas, cur_color, start_pos, rad, cur_size)

                    elif cur_tool == TOOL_RTRI and start_pos:
                        draw_right_triangle(canvas, cur_color, start_pos, end_pos, cur_size)

                    elif cur_tool == TOOL_ETRI and start_pos:
                        draw_equilateral_triangle(canvas, cur_color, start_pos, end_pos, cur_size)

                    elif cur_tool == TOOL_RHOMBUS and start_pos:
                        draw_rhombus(canvas, cur_color, start_pos, end_pos, cur_size)

                    drawing = False
                    preview = None   # discard the preview surface

            # ── Mouse moved while drawing ─────
            if event.type == pygame.MOUSEMOTION and drawing:
                cx, cy = to_canvas(*event.pos)

                if event.pos[1] >= TOOLBAR_H:   # only paint in the canvas area

                    if cur_tool == TOOL_PEN:
                        # Draw a line segment from the previous position to the current one
                        rel = event.rel   # pixel movement since last event
                        pygame.draw.line(canvas, cur_color,
                                         (cx - rel[0], cy - rel[1]), (cx, cy),
                                         cur_size * 2)
                        pygame.draw.circle(canvas, cur_color, (cx, cy), cur_size)

                    elif cur_tool == TOOL_ERASER:
                        # Erase a circle at the current position
                        pygame.draw.circle(canvas, BG_CANVAS, (cx, cy), cur_size * 3)

                    else:
                        # All shape tools: render a live preview on a canvas copy
                        preview = canvas.copy()

                        if cur_tool == TOOL_RECT:
                            rx = min(start_pos[0], cx)
                            ry = min(start_pos[1], cy)
                            rw = abs(cx - start_pos[0])
                            rh = abs(cy - start_pos[1])
                            pygame.draw.rect(preview, cur_color,
                                             (rx, ry, rw, rh), cur_size)

                        elif cur_tool == TOOL_SQUARE:
                            draw_square(preview, cur_color, start_pos, (cx, cy), cur_size)

                        elif cur_tool == TOOL_CIRCLE:
                            rad = int(math.hypot(cx - start_pos[0], cy - start_pos[1]))
                            if rad > 0:
                                pygame.draw.circle(preview, cur_color,
                                                   start_pos, rad, cur_size)

                        elif cur_tool == TOOL_RTRI:
                            draw_right_triangle(preview, cur_color,
                                                start_pos, (cx, cy), cur_size)

                        elif cur_tool == TOOL_ETRI:
                            draw_equilateral_triangle(preview, cur_color,
                                                      start_pos, (cx, cy), cur_size)

                        elif cur_tool == TOOL_RHOMBUS:
                            draw_rhombus(preview, cur_color,
                                         start_pos, (cx, cy), cur_size)

            # ── Mouse wheel: adjust brush size ─
            if event.type == pygame.MOUSEWHEEL:
                cur_size = max(1, min(50, cur_size + event.y))

        # ── Render ────────────────────────────
        screen.fill(BG_TOOLBAR)
        # Show preview while dragging a shape, otherwise the committed canvas
        screen.blit(preview if preview else canvas, (0, TOOLBAR_H))
        draw_toolbar(screen, tool_buttons, cur_tool, cur_color, cur_size, palette_rects)

        # Cursor size indicator (circle outline following the mouse)
        if mouse_pos[1] >= TOOLBAR_H:
            r = cur_size * 3 if cur_tool == TOOL_ERASER else cur_size
            pygame.draw.circle(screen, BORDER_CLR, mouse_pos, max(r, 2), 1)

        pygame.display.flip()


if __name__ == "__main__":
    main()