import pygame

class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height

    def apply(self, entity_rect):
        return entity_rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + self.width // 2
        y = -target.rect.centery + self.height // 2

        # Limiter le déplacement de la caméra pour ne pas montrer les zones hors limites
        x = min(0, x)  # Bord gauche
        y = min(0, y)  # Bord haut
        x = max(-(self.map_width - self.width), x)  # Bord droit
        y = max(-(self.map_height - self.height), y)  # Bord bas

        self.camera = pygame.Rect(x, y, self.width, self.height)