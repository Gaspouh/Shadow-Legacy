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
heal_particles = []

class Fade:
    def __init__(self):
        self.intensity = 0
        self.state = None #"in", "out", "wait" ou None
        self.overlay = pygame.Surface ((1920, 1080)) #Taille de la fenetre
        self.overlay.fill((0, 0, 0)) #Fond noir
        self.wait_start = None

    def start(self, state, speed, wait=0):
        self.state = state
        self.speed = speed
        self.wait = wait

        if state == "out":
            self.intensity = 0 #Commence dans le noir pour passer au transparent
        else : #pour le fade in et le wait
            self.intensity = 255 #Commence dans le transparent pour passer au noir

    def update(self, fenetre):
        if self.state is not None:
            if self.state == "out":
                self.intensity = min(255, self.intensity + self.speed)

            elif self.state == "wait":
                if self.wait_start is None:
                    self.wait_start = pygame.time.get_ticks()
                if pygame.time.get_ticks() - self.wait_start >= self.wait:
                    self.wait_start = None
                    self.state = "in"

            elif self.state == "in":
                self.intensity = max(0, self.intensity - self.speed)
                if self.intensity == 0:
                    self.state = None
            self.overlay.set_alpha(self.intensity) #Définir l'opacité du fond
            fenetre.blit(self.overlay, (0, 0)) #Affiche le fondu sur la fenetre depuis le point 0,0

class HealParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.size = random.randint(2, 5)
        self.vy = -random.randint(1, 3)  # Monte vers le haut
        self.vx = random.randint(-1, 1)  

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface, camera):
        alpha = int(255 * (self.life / self.max_life))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, alpha), (self.size, self.size), self.size)
        pos = camera.apply(pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2))
        surface.blit(s, pos)