import pygame

class Ball:
    def __init__(self, x, y, radius=20):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = (255, 0, 0)
        self.step = 5

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def check_bounds(self, width, height):
        
        if self.x - self.radius < 0:
            self.x = self.radius

        
        if self.x + self.radius > width:
            self.x = width - self.radius

        
        if self.y - self.radius < 0:
            self.y = self.radius

       
        if self.y + self.radius > height:
            self.y = height - self.radius