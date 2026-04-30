import pygame
import random

class Camera:
    def __init__(self, width, height, map_width, map_height, zoom=2):
        """ Ajout d'un zoom pour faire des effets plus tard et controler la caméra """
        self.zoom = zoom
        self.zoom_w = int(width/zoom)
        self.zoom_h = int(height/zoom)
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height
        self.camera = pygame.Rect(0, 0, self.zoom_w, self.zoom_h)


    def apply(self, entity_rect):
        return entity_rect.move(self.camera.topleft)
    
    def update_map_size(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height

    def update(self, target, shake_amount=0):
        target_x = -target.rect.centerx + self.zoom_w // 2
        target_y = -target.rect.centery + self.zoom_h // 2

        # Appliquer un lissage pour un mouvement de caméra plus fluide
        self.camera.x += (target_x - self.camera.x) * 0.15
        self.camera.y += (target_y - self.camera.y) * 0.15

        # Limiter le déplacement de la caméra pour ne pas montrer les zones hors limites
        self.camera.x = min(0, max(-(self.map_width - self.zoom_w), self.camera.x))
        self.camera.y = min(0, max(-(self.map_height - self.zoom_h), self.camera.y))
        

        if shake_amount > 0:
            self.camera.x += random.randint(-shake_amount, shake_amount)
            self.camera.y += random.randint(-shake_amount, shake_amount)