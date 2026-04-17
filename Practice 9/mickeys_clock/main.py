from pathlib import Path
import pygame
from clock import MickeyClock

SCREEN_SIZE = (700, 700)
FPS = 30


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Mickey's Clock")
    clock = pygame.time.Clock()

    image_path = Path(__file__).resolve().parent / "images" / "mickey_hand.png"
    mickey_clock = MickeyClock(image_path, SCREEN_SIZE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mickey_clock.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()