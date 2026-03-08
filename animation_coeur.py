import pygame
from ennemi import ennemi_debutant
from perso import Player
 
class Coeur(pygame.sprite.Sprite):

    def __init__(self):

        self.height = 123
        self.width = 112
        self.marge = 0
        self.display_size = 42
        self.sheet = pygame.image.load('coeur.png').convert_alpha()
        self.rect = self.sheet.get_rect()
        self.index_anim = 0.0
        self.vitesse_animation = 0.12
        self.frames_idle = []
        self.frames_death = []
        self.state = "ALIVE"

        for i in range(6): # 6 frames d'animation pour le cœur vivant (ligne 0 du sheet)
            self.frames_idle.append(self.get_frame(i, 0))

        for row in range(1, 3): # 2 lignes de mort (lignes 1 et 2 du sheet)
            for i in range(6):
                self.frames_death.append(self.get_frame(i, row))

        self.image = self.frames_idle[0]


    def get_frame(self, index, row):
        frame = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Découpage (x, y, largeur, hauteur)
        frame.blit(self.sheet, (0, 0), (index * self.width, row * self.height, self.width, self.height))
  
        return pygame.transform.scale(frame, (self.display_size, self.display_size))
    
    def update(self, player_health, index):
        """
        LOGIQUE DE CHANGEMENT D'ÉTAT
        """
        if index < player_health:
            if self.state != "ALIVE": # Réinitialiser l'animation si le joueur récupère de la vie (reset)
                self.state = "ALIVE"
                self.index_anim = 0.0
        elif index == player_health and self.state == "ALIVE":
            # Si le joueur vient de perdre ce point de vie
            self.state = "DYING"
            self.index_anim = 0.0 # Réinitialiser l'index d'animation pour la mort
        elif index > player_health and self.state not in ("DYING", "DEAD"):
            self.state = "DEAD"
            self.index_anim = float(len(self.frames_death) - 1)

        """
        GESTION DES ANIMATIONS SELON L'ÉTAT
        """
        if self.state == "ALIVE":
            self.index_anim = (self.index_anim + self.vitesse_animation) % len(self.frames_idle)
            self.image = self.frames_idle[int(self.index_anim)]
            
        elif self.state == "DYING":
            self.index_anim += self.vitesse_animation
            if self.index_anim < len(self.frames_death):
                self.image = self.frames_death[int(self.index_anim)]
            else:
                self.state = "DEAD" # Une fois l'animation finie, on passe en mort
                
        elif self.state == "DEAD":
            self.image = self.frames_death[-1] # On reste sur la dernière frame