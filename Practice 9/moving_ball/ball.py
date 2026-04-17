import pygame


class Ball:
    def __init__(self, x: int, y: int, radius: int = 25, color=(255, 0, 0), step: int = 5):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.step = step

    def move(self, dx: int, dy: int, screen_width: int, screen_height: int):
        new_x = self.x + dx
        new_y = self.y + dy

        if self.radius <= new_x <= screen_width - self.radius:
            self.x = new_x
        if self.radius <= new_y <= screen_height - self.radius:
            self.y = new_y

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


def main():
    pygame.init()

    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Moving Ball")

    clock = pygame.time.Clock()

    ball = Ball(400, 300)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            ball.move(-ball.step, 0, screen_width, screen_height)
        if keys[pygame.K_RIGHT]:
            ball.move(ball.step, 0, screen_width, screen_height)
        if keys[pygame.K_UP]:
            ball.move(0, -ball.step, screen_width, screen_height)
        if keys[pygame.K_DOWN]:
            ball.move(0, ball.step, screen_width, screen_height)

        screen.fill((0, 0, 0))
        ball.draw(screen)

        pygame.display.flip()
        clock.tick(60)  # 60 FPS (чтобы движение было плавное)

    pygame.quit()


if __name__ == "__main__":
    main()