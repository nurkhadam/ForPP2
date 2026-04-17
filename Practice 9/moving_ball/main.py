import pygame
from ball import Ball

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
BACKGROUND_COLOR = (255, 255, 255)
FPS = 60


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Moving Ball")
    clock = pygame.time.Clock()

    ball = Ball(x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                ball.handle_key(event.key, SCREEN_WIDTH, SCREEN_HEIGHT)

        screen.fill(BACKGROUND_COLOR)
        ball.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()