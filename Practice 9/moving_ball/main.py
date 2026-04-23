import pygame
from ball import Ball

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball Game")

ball = Ball(WIDTH // 2, HEIGHT // 2)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        ball.move(-ball.step, 0)
    if keys[pygame.K_d]:
        ball.move(ball.step, 0)
    if keys[pygame.K_w]:
        ball.move(0, -ball.step)
    if keys[pygame.K_s]:
        ball.move(0, ball.step)

    ball.check_bounds(WIDTH, HEIGHT)

    screen.fill((255, 255, 255))
    ball.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()