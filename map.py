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

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img_width = 324
        img_height = 484
        Facteur = 8.5
        self.image = pygame.image.load('spike2.png')
        self.image = pygame.transform.scale(self.image, (img_width//Facteur, img_height//Facteur))
        self.rect = self.image.get_rect(topleft=(x, y))
spikes = [
    Spike(400, 445), # à mettre directement sur le sol pour éviter les pb de collision
    Spike(540, 445), 
    Spike(500, 445)
]
