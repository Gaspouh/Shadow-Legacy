import pygame
import random

class Particle:
    def __init__(self, x, y, direction_x=0, direction_y=0):
        self.x, self.y = x, y
        # Réduire la vitesse pour plus de discrétion
        self.vx = random.uniform(-2, 2) + (direction_x * 3)
        self.vy = random.uniform(-2, 2) + (direction_y * 3)
        self.life = 15  # Durée de vie plus courte
        self.max_life = 15
        # Couleur avec variation pour plus réaliste
        self.color = (random.randint(150, 200), random.randint(0, 50), random.randint(0, 50))  # Tons rougeâtres

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Ajout de gravité
        self.life -= 1

    def draw(self, surface, camera):
        if self.life > 0:
            # rétrécit plus lentement
            size = max(1, int(self.life / 3))
            # "Alpha" pour un fondu (plus discret)
            alpha = int((self.life / self.max_life) * 255)
            color_with_alpha = (*self.color, alpha)
            # On dessine un cercle au lieu d'un carré - à optimiser...
            temp_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color_with_alpha, (size, size), size)
            surface.blit(temp_surface, camera.apply(pygame.Rect(self.x - size, self.y - size, size*2, size*2)))

particles = []