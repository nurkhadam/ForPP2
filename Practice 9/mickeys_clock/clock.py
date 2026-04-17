from __future__ import annotations

from datetime import datetime
from pathlib import Path
import math
import pygame


def blit_rotate_pivot(
    surface: pygame.Surface,
    image: pygame.Surface,
    pivot_world: tuple[int, int],
    angle_degrees: float,
    pivot_local: tuple[int, int],
) -> None:
    """
    Rotate an image around a custom point inside that image and draw it so the
    chosen pivot stays exactly at ``pivot_world``.

    ``pivot_local`` is measured in image coordinates.
    """
    image_rect = image.get_rect(
        topleft=(pivot_world[0] - pivot_local[0], pivot_world[1] - pivot_local[1])
    )

    offset_center_to_pivot = pygame.math.Vector2(pivot_world) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle_degrees)
    rotated_center = (
        pivot_world[0] - rotated_offset.x,
        pivot_world[1] - rotated_offset.y,
    )

    rotated_image = pygame.transform.rotate(image, angle_degrees)
    rotated_rect = rotated_image.get_rect(center=rotated_center)
    surface.blit(rotated_image, rotated_rect)


class MickeyClock:
    def __init__(self, image_path: Path, size: tuple[int, int] = (700, 700)):
        self.width, self.height = size
        self.center = (self.width // 2, self.height // 2 + 40)
        self.background_color = (245, 245, 245)
        self.clock_face_color = (255, 255, 255)
        self.outline_color = (30, 30, 30)

        base_hand = pygame.image.load(str(image_path)).convert_alpha()

        # Slightly different sizes make both hands easier to see.
        self.minute_hand = pygame.transform.smoothscale(base_hand, (70, 210))
        self.second_hand = pygame.transform.smoothscale(base_hand, (76, 240))

        # Mirror one hand so the clock has a left and right Mickey arm.
        self.minute_hand = pygame.transform.flip(self.minute_hand, True, False)

        # The pivot must be at the yellow cuff area, not at the glove.
        # These values come from the source image geometry.
        cuff_center_original = (80, 396)  # center of the yellow cuff on 160x480 image
        self.minute_pivot = (
            round(cuff_center_original[0] * self.minute_hand.get_width() / 160),
            round(cuff_center_original[1] * self.minute_hand.get_height() / 480),
        )
        self.second_pivot = (
            round(cuff_center_original[0] * self.second_hand.get_width() / 160),
            round(cuff_center_original[1] * self.second_hand.get_height() / 480),
        )

        self.face_radius = 180
        self.ear_radius = 70

    def _draw_background(self, screen: pygame.Surface) -> None:
        screen.fill(self.background_color)

        left_ear = (self.center[0] - 130, self.center[1] - 170)
        right_ear = (self.center[0] + 130, self.center[1] - 170)

        pygame.draw.circle(screen, self.outline_color, left_ear, self.ear_radius + 4)
        pygame.draw.circle(screen, self.clock_face_color, left_ear, self.ear_radius)

        pygame.draw.circle(screen, self.outline_color, right_ear, self.ear_radius + 4)
        pygame.draw.circle(screen, self.clock_face_color, right_ear, self.ear_radius)

        pygame.draw.circle(screen, self.outline_color, self.center, self.face_radius + 4)
        pygame.draw.circle(screen, self.clock_face_color, self.center, self.face_radius)

        font = pygame.font.SysFont(None, 34)
        title = font.render("Mickey's Clock - Minutes / Seconds", True, self.outline_color)
        screen.blit(title, (self.width // 2 - title.get_width() // 2, 24))

        for i in range(60):
            angle = math.radians(i * 6 - 90)
            outer = (
                self.center[0] + int(math.cos(angle) * self.face_radius),
                self.center[1] + int(math.sin(angle) * self.face_radius),
            )
            inner_length = self.face_radius - (20 if i % 5 == 0 else 10)
            inner = (
                self.center[0] + int(math.cos(angle) * inner_length),
                self.center[1] + int(math.sin(angle) * inner_length),
            )
            width = 4 if i % 5 == 0 else 2
            pygame.draw.line(screen, self.outline_color, inner, outer, width)

        digital_font = pygame.font.SysFont(None, 50)
        now = datetime.now()
        digital_text = digital_font.render(now.strftime("%M:%S"), True, self.outline_color)
        screen.blit(digital_text, (self.width // 2 - digital_text.get_width() // 2, self.center[1] + 210))

    def draw(self, screen: pygame.Surface) -> None:
        now = datetime.now()
        self._draw_background(screen)

        minute_angle = -((now.minute + now.second / 60) * 6)
        second_angle = -(now.second * 6)

        # Both hands now rotate around the actual clock center.
        blit_rotate_pivot(
            screen,
            self.minute_hand,
            self.center,
            minute_angle,
            self.minute_pivot,
        )
        blit_rotate_pivot(
            screen,
            self.second_hand,
            self.center,
            second_angle,
            self.second_pivot,
        )

        pygame.draw.circle(screen, self.outline_color, self.center, 10)
        pygame.draw.circle(screen, (255, 220, 120), self.center, 6)