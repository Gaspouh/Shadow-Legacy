import pygame

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
    
platforms = [
    Platform(0, 500, 8000, 100),
    Platform(300, 350, 200, 20),
    Platform(500, 200, 200, 20),
    Platform(800, 0, 20, 350),
    Platform(1100, 300, 200, 20),
    Platform(1400, 400, 200, 20),
]