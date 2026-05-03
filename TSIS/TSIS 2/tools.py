import pygame   # pygame is needed here for Rect, event loop, drawing, and display
import sys      # sys.exit() is used to close the program cleanly on quit
import math     # math.hypot() calculates the radius for the circle tool

# Import everything we need from paint.py
# paint.py acts as a shared "library" — it holds all constants, classes, and helpers
from paint import (
    # UI classes and rendering functions
    ToolButton,    # class for a clickable toolbar button
    draw_toolbar,  # function that draws the entire toolbar each frame
    to_canvas,     # converts screen coordinates to canvas-local coordinates

    # Shape drawing helpers (one function per shape)
    draw_square, draw_right_triangle,
    draw_equilateral_triangle, draw_rhombus,

    # New tool helpers added for TSIS 2
    draw_line,    # draws a straight line between two points
    flood_fill,   # BFS flood-fill — fills a connected region with a color
    save_canvas,  # saves the canvas Surface to a PNG file and returns the path

    # Shared pygame objects (created once in paint.py, reused here)
    screen,     # the main OS window Surface
    clock,      # pygame Clock used to cap FPS
    canvas,     # the off-screen drawing Surface where strokes are stored
    font,       # small bold Arial font for toolbar labels
    text_font,  # larger Arial font for text typed on the canvas

    # Layout constants
    SCREEN_W, SCREEN_H,   # total window dimensions
    TOOLBAR_H,            # height of the toolbar strip at the top

    # Color constants
    BG_CANVAS,    # white — canvas background color (also the eraser color)
    BG_TOOLBAR,   # dark grey-blue — toolbar background
    BORDER_CLR,   # grey — used for button borders and the cursor circle

    # The 18-color palette list
    PALETTE,

    # Tool ID strings — each constant is a unique string identifying one tool
    TOOL_PEN, TOOL_RECT, TOOL_SQUARE, TOOL_CIRCLE,
    TOOL_ERASER, TOOL_RTRI, TOOL_ETRI, TOOL_RHOMBUS,
    TOOL_LINE, TOOL_FILL, TOOL_TEXT,

    # Brush size preset values (integers: 2, 5, 10)
    SIZE_SMALL, SIZE_MEDIUM, SIZE_LARGE,

    # Fixed Rect objects for toolbar controls (defined once in paint.py)
    plus_rect, minus_rect, clear_rect,     # +, -, Clear button rects
    size_s_rect, size_m_rect, size_l_rect, # S, M, L size preset button rects
)


def main():
    # ── Tool buttons ──────────────────────────────────────────────────────────
    # Create one ToolButton instance per tool, placed in 3 rows inside the toolbar.
    # ToolButton(x, y, width, height, label, tool_id)
    tool_buttons = [
        # Row 1 (y=4) — basic drawing tools from Practice 10
        ToolButton( 10,  4, 58, 26, "✏ Pen",     TOOL_PEN),     # freehand pencil
        ToolButton( 72,  4, 58, 26, "▭ Rect",    TOOL_RECT),    # rectangle outline
        ToolButton(134,  4, 62, 26, "□ Square",  TOOL_SQUARE),  # equal-sided square
        ToolButton(200,  4, 62, 26, "○ Circle",  TOOL_CIRCLE),  # circle by radius
        ToolButton(266,  4, 58, 26, "⌫ Erase",   TOOL_ERASER),  # eraser (paints white)

        # Row 2 (y=34) — shape tools added in Practice 11
        ToolButton( 10, 34, 72, 26, "◺ R-Tri",   TOOL_RTRI),    # right-angle triangle
        ToolButton( 86, 34, 72, 26, "△ E-Tri",   TOOL_ETRI),    # equilateral triangle
        ToolButton(162, 34, 72, 26, "◇ Rhombus", TOOL_RHOMBUS), # rhombus / diamond

        # Row 3 (y=64) — new tools added for TSIS 2
        ToolButton( 10, 64, 62, 26, "/ Line",    TOOL_LINE),    # straight line with preview
        ToolButton( 76, 64, 62, 26, "⬛ Fill",    TOOL_FILL),    # BFS flood-fill on click
        ToolButton(142, 64, 62, 26, "T Text",    TOOL_TEXT),    # click-to-type text tool
    ]

    # ── Colour palette swatch rects ───────────────────────────────────────────
    # Pre-calculate the screen Rect for each of the 18 palette colour swatches.
    # Arranged in a 9×2 grid; each swatch is 20×20 px with a 2 px gap.
    # Starting x=500 keeps the palette clear of the S/M/L size buttons (which end ~x=479).
    palette_rects = []
    for i in range(len(PALETTE)):
        rx = 500 + (i % 9) * 22   # column: 9 swatches per row, each 22 px apart
        ry = 5   + (i // 9) * 22  # row: new row every 9 swatches, 22 px apart
        palette_rects.append(pygame.Rect(rx, ry, 20, 20))   # store the Rect for click detection and drawing

    # ── Application state variables ──────────────────────────────────────────
    cur_tool  = TOOL_PEN    # currently active tool (starts as the pen)
    cur_color = (0, 0, 0)   # currently selected drawing color (starts as black)
    cur_size  = SIZE_SMALL  # current brush thickness in pixels (starts as 2)
    drawing   = False       # True while the left mouse button is held down on the canvas
    start_pos = None        # canvas coordinate where the current drag started
    preview   = None        # temporary canvas copy used for live shape/line preview while dragging

    # ── Text tool state ──────────────────────────────────────────────────────
    # The text tool works in two stages:
    #   1. User clicks on the canvas → text_active = True, cursor appears
    #   2. User types characters → they accumulate in text_buffer
    #   3. Enter = stamp text onto canvas; Escape = cancel without drawing
    text_active = False   # True while the user is typing (between click and Enter/Escape)
    text_buffer = ""      # string of characters typed so far in this session
    text_pos    = (0, 0)  # canvas coordinate where the text will be stamped on Enter

    # ── Save notification state ───────────────────────────────────────────────
    save_msg       = ""    # the message to show after a successful Ctrl+S save
    save_msg_timer = 0     # countdown in frames; banner is shown while this is > 0

    # ══════════════════════════════════════════════════════════════════════════
    # MAIN LOOP — runs at 60 FPS until the user closes the window
    # Each iteration: 1) process events → 2) update state → 3) render frame
    # ══════════════════════════════════════════════════════════════════════════
    while True:
        clock.tick(60)   # wait until 1/60 second has passed (caps the frame rate at 60 FPS)
        mouse_pos = pygame.mouse.get_pos()   # current cursor position (screen coordinates)

        # ── Event loop ────────────────────────────────────────────────────────
        # pygame.event.get() returns all events that happened since the last frame
        for event in pygame.event.get():

            # ── Window close button ───────────────────────────────────────────
            if event.type == pygame.QUIT:   # user clicked the X button on the window
                pygame.quit()   # shut down all pygame modules cleanly
                sys.exit()      # terminate the Python process

            # ════════════════════════════════════════════════════════════════
            # KEYBOARD EVENTS
            # ════════════════════════════════════════════════════════════════
            if event.type == pygame.KEYDOWN:   # a key was pressed this frame

                # ── Text tool typing mode ────────────────────────────────────
                if text_active:   # we are currently typing text on the canvas
                    if event.key == pygame.K_RETURN:        # Enter key — commit text
                        if text_buffer:                     # only stamp if something was typed
                            rendered = text_font.render(text_buffer, True, cur_color)  # render text to Surface
                            canvas.blit(rendered, text_pos)   # stamp text permanently onto canvas
                        text_active = False   # exit text-entry mode
                        text_buffer = ""      # clear the buffer for next time

                    elif event.key == pygame.K_ESCAPE:   # Escape key — cancel text entry
                        text_active = False   # exit text-entry mode without drawing anything
                        text_buffer = ""      # discard everything typed

                    elif event.key == pygame.K_BACKSPACE:   # Backspace — delete last character
                        text_buffer = text_buffer[:-1]       # slice off the last character

                    else:
                        if event.unicode:               # event.unicode is the typed character string
                            text_buffer += event.unicode  # append character to the live buffer

                # ── Global keyboard shortcuts (only active when NOT typing text) ──
                else:
                    if event.key == pygame.K_1:      # key "1" → switch to small brush
                        cur_size = SIZE_SMALL
                    elif event.key == pygame.K_2:    # key "2" → switch to medium brush
                        cur_size = SIZE_MEDIUM
                    elif event.key == pygame.K_3:    # key "3" → switch to large brush
                        cur_size = SIZE_LARGE

                    # Cmnd+S — save the canvas to a PNG file
                    if event.key == pygame.K_s and (
                        pygame.key.get_mods() & pygame.KMOD_CTRL or
                        pygame.key.get_mods() & pygame.KMOD_META
                    ):
                        saved_path = save_canvas(canvas)       # save and get the file path back
                        save_msg = f"Saved: {saved_path}"      # build the notification message
                        save_msg_timer = 180   # show the banner for 180 frames = 3 seconds at 60 FPS

            # ════════════════════════════════════════════════════════════════
            # MOUSE BUTTON PRESSED (left button = 1)
            # ════════════════════════════════════════════════════════════════
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos   # screen coordinates of the click

                # ── Click inside the toolbar (y < TOOLBAR_H) ─────────────────
                if y < TOOLBAR_H:

                    # Check each tool button to see if it was clicked
                    for btn in tool_buttons:
                        if btn.is_clicked((x, y)):
                            cur_tool = btn.tool_id   # switch to the clicked tool
                            text_active = False      # cancel any ongoing text entry
                            text_buffer = ""

                    # Check each palette swatch to see if it was clicked
                    for idx, rect in enumerate(palette_rects):
                        if rect.collidepoint(x, y):
                            cur_color = PALETTE[idx]   # switch drawing color to this swatch

                    # S / M / L size preset buttons
                    if size_s_rect.collidepoint(x, y):        # clicked "S"
                        cur_size = SIZE_SMALL
                    elif size_m_rect.collidepoint(x, y):      # clicked "M"
                        cur_size = SIZE_MEDIUM
                    elif size_l_rect.collidepoint(x, y):      # clicked "L"
                        cur_size = SIZE_LARGE

                    # Fine ±1 adjustment buttons (only reached if S/M/L not clicked)
                    elif plus_rect.collidepoint(x, y):        # clicked "+"
                        cur_size = min(50, cur_size + 1)       # increase by 1, cap at 50
                    elif minus_rect.collidepoint(x, y):       # clicked "−"
                        cur_size = max(1, cur_size - 1)        # decrease by 1, minimum 1

                    # Clear button — wipe the entire canvas back to white
                    elif clear_rect.collidepoint(x, y):
                        canvas.fill(BG_CANVAS)   # fill every pixel with the background color

                # ── Click inside the canvas area (y >= TOOLBAR_H) ────────────
                else:
                    canvas_pos = to_canvas(x, y)   # translate screen y to canvas-local y

                    if cur_tool == TOOL_TEXT:
                        # Text tool: start a text-entry session at the clicked position
                        text_active = True        # enable typing mode
                        text_buffer = ""          # start with an empty string
                        text_pos    = canvas_pos  # remember where to stamp the text

                    elif cur_tool == TOOL_FILL:
                        # Flood-fill tool: fill the clicked region immediately (no drag)
                        flood_fill(canvas, canvas_pos, cur_color)   # BFS fill starting here

                    else:
                        # All other tools start a drag on mouse press
                        drawing   = True        # flag that a drag is in progress
                        start_pos = canvas_pos  # record the drag start point

                        # Pen and eraser take effect immediately on press (no drag needed)
                        if cur_tool == TOOL_PEN:
                            pygame.draw.circle(canvas, cur_color, start_pos, cur_size)   # dot at click
                        elif cur_tool == TOOL_ERASER:
                            pygame.draw.circle(canvas, BG_CANVAS, start_pos, cur_size * 3)  # erase dot

            # ════════════════════════════════════════════════════════════════
            # MOUSE BUTTON RELEASED (left button = 1)
            # Commit the final shape to the canvas when the drag ends.
            # ════════════════════════════════════════════════════════════════
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and start_pos:   # only act if a drag was in progress
                    end_pos = to_canvas(*event.pos)   # canvas coordinate of the release point

                    if cur_tool == TOOL_RECT:
                        # Rectangle: bounding box from drag start to release
                        rx = min(start_pos[0], end_pos[0])           # left edge
                        ry = min(start_pos[1], end_pos[1])           # top edge
                        rw = abs(end_pos[0] - start_pos[0])          # width
                        rh = abs(end_pos[1] - start_pos[1])          # height
                        pygame.draw.rect(canvas, cur_color, (rx, ry, rw, rh), cur_size)

                    elif cur_tool == TOOL_SQUARE:
                        draw_square(canvas, cur_color, start_pos, end_pos, cur_size)

                    elif cur_tool == TOOL_CIRCLE:
                        # Radius = straight-line (Euclidean) distance from start to release
                        rad = int(math.hypot(end_pos[0] - start_pos[0],
                                             end_pos[1] - start_pos[1]))
                        if rad > 0:
                            pygame.draw.circle(canvas, cur_color, start_pos, rad, cur_size)

                    elif cur_tool == TOOL_RTRI:
                        draw_right_triangle(canvas, cur_color, start_pos, end_pos, cur_size)

                    elif cur_tool == TOOL_ETRI:
                        draw_equilateral_triangle(canvas, cur_color, start_pos, end_pos, cur_size)

                    elif cur_tool == TOOL_RHOMBUS:
                        draw_rhombus(canvas, cur_color, start_pos, end_pos, cur_size)

                    elif cur_tool == TOOL_LINE:
                        # Commit the straight line to the real canvas (replaces the preview)
                        draw_line(canvas, cur_color, start_pos, end_pos, cur_size)

                    drawing = False    # drag is over — clear the drawing flag
                    preview = None     # discard the live preview surface

            # ════════════════════════════════════════════════════════════════
            # MOUSE MOTION while left button is held (drawing = True)
            # Used for freehand drawing and live shape previews.
            # ════════════════════════════════════════════════════════════════
            if event.type == pygame.MOUSEMOTION and drawing:
                cx, cy = to_canvas(*event.pos)   # canvas coordinate of current cursor

                # Only draw when the cursor is inside the canvas area (not over the toolbar)
                if event.pos[1] >= TOOLBAR_H:

                    if cur_tool == TOOL_PEN:
                        # Freehand pen: connect previous position to current with a line
                        rel  = event.rel              # (dx, dy) movement since last MOUSEMOTION
                        prev = (cx - rel[0], cy - rel[1])   # calculate the previous canvas position
                        pygame.draw.line(canvas, cur_color, prev, (cx, cy), cur_size * 2)   # thick stroke
                        pygame.draw.circle(canvas, cur_color, (cx, cy), cur_size)           # round cap

                    elif cur_tool == TOOL_ERASER:
                        # Eraser: paint a large white circle at the cursor
                        pygame.draw.circle(canvas, BG_CANVAS, (cx, cy), cur_size * 3)

                    else:
                        # ── Live preview for shape and line tools ──────────
                        # Copy the committed canvas so the ghost shape doesn't permanently alter it
                        preview = canvas.copy()   # fresh copy each motion event (old preview discarded)

                        if cur_tool == TOOL_RECT:
                            rx = min(start_pos[0], cx)       # bounding box left
                            ry = min(start_pos[1], cy)       # bounding box top
                            rw = abs(cx - start_pos[0])      # bounding box width
                            rh = abs(cy - start_pos[1])      # bounding box height
                            pygame.draw.rect(preview, cur_color, (rx, ry, rw, rh), cur_size)

                        elif cur_tool == TOOL_SQUARE:
                            draw_square(preview, cur_color, start_pos, (cx, cy), cur_size)

                        elif cur_tool == TOOL_CIRCLE:
                            rad = int(math.hypot(cx - start_pos[0], cy - start_pos[1]))  # live radius
                            if rad > 0:
                                pygame.draw.circle(preview, cur_color, start_pos, rad, cur_size)

                        elif cur_tool == TOOL_RTRI:
                            draw_right_triangle(preview, cur_color, start_pos, (cx, cy), cur_size)

                        elif cur_tool == TOOL_ETRI:
                            draw_equilateral_triangle(preview, cur_color, start_pos, (cx, cy), cur_size)

                        elif cur_tool == TOOL_RHOMBUS:
                            draw_rhombus(preview, cur_color, start_pos, (cx, cy), cur_size)

                        elif cur_tool == TOOL_LINE:
                            # Live straight line from start to current cursor position
                            draw_line(preview, cur_color, start_pos, (cx, cy), cur_size)

            # ── Mouse wheel — fine-adjust brush size by scrolling ──────────
            if event.type == pygame.MOUSEWHEEL:
                # event.y = +1 (scroll up = bigger) or -1 (scroll down = smaller)
                cur_size = max(1, min(50, cur_size + event.y))   # clamp between 1 and 50

        # ════════════════════════════════════════════════════════════════════
        # RENDER — draw everything to the screen each frame
        # ════════════════════════════════════════════════════════════════════

        screen.fill(BG_TOOLBAR)   # clear the window with the toolbar background color

        # ── Canvas area ──────────────────────────────────────────────────────
        # While dragging a shape/line: show the preview copy (ghost shape).
        # At all other times: show the committed canvas directly.
        display_surface = preview if preview else canvas   # choose which surface to display
        screen.blit(display_surface, (0, TOOLBAR_H))       # draw it below the toolbar

        # ── Text tool live preview ────────────────────────────────────────────
        # Show what the user has typed so far, with a blinking "|" cursor at the end.
        # This is drawn each frame directly on the screen (not on the canvas) until Enter.
        if text_active and text_buffer:
            ghost = text_font.render(text_buffer + "|", True, cur_color)   # text + cursor character
            screen.blit(ghost, (text_pos[0], text_pos[1] + TOOLBAR_H))     # offset back to screen coords
        elif text_active:
            # Empty buffer — still show just the cursor so the user knows input is active
            ghost = text_font.render("|", True, cur_color)
            screen.blit(ghost, (text_pos[0], text_pos[1] + TOOLBAR_H))

        # ── Toolbar ───────────────────────────────────────────────────────────
        # draw_toolbar redraws all toolbar elements on top of the screen each frame
        draw_toolbar(screen, tool_buttons, cur_tool, cur_color, cur_size, palette_rects)

        # ── Cursor size indicator circle ──────────────────────────────────────
        # Draw a circle outline around the cursor to show the effective brush/eraser radius.
        # Only visible when the cursor is in the canvas area (below the toolbar).
        if mouse_pos[1] >= TOOLBAR_H:
            r = cur_size * 3 if cur_tool == TOOL_ERASER else cur_size   # eraser uses 3× radius
            pygame.draw.circle(screen, BORDER_CLR, mouse_pos, max(r, 2), 1)   # 1 px outline, min radius 2

        # ── Save notification banner ──────────────────────────────────────────
        # Shown for 3 seconds (180 frames) after a successful Ctrl+S save.
        if save_msg_timer > 0:
            save_msg_timer -= 1   # count down one frame each iteration

            notif_surf = font.render(save_msg, True, (255, 255, 180))   # yellow-white text
            notif_w = notif_surf.get_width() + 20    # banner width = text width + padding
            notif_h = notif_surf.get_height() + 12   # banner height = text height + padding
            notif_x = (SCREEN_W - notif_w) // 2      # center the banner horizontally
            notif_y = TOOLBAR_H + 10                  # just below the toolbar

            bg = pygame.Surface((notif_w, notif_h), pygame.SRCALPHA)   # surface with alpha channel
            bg.fill((30, 30, 30, 200))       # semi-transparent dark background (alpha=200 out of 255)
            screen.blit(bg, (notif_x, notif_y))           # draw the background box
            screen.blit(notif_surf, (notif_x + 10, notif_y + 6))   # draw the text inside the box

        # Push the completed frame to the display (swap buffers)
        pygame.display.flip()


# ── Entry point ───────────────────────────────────────────────────────────────
# This block only executes when the file is run directly (python tools.py).
# If tools.py were imported as a module, main() would NOT be called automatically.
if __name__ == "__main__":
    main()