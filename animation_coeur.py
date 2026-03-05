import pygame
from ennemi import ennemi_debutant
from perso import Player
 
class Coeur(pygame.sprite.Sprite):

    def __init__(self):

        self.height = 30
        self.width = 30
        self.marge = 5
        self.sheet = pygame.image.load('coeur.png').convert_alpha()
        self.rect = self.sheet.get_rect()
        self.index_image = 0.0
        self.vitesse_animation = 0.1
        self.frames = []
        coeur_plein = self.frames[0]
        coeur_vide = self.frames[0:5]

        for i in range(5): 
            self.frames.append(self.get_frame(i))


    def get_frame(self, index):
        frame = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Découpage (x, y, largeur, hauteur)
        frame.blit(self.sheet, (0, 0), (index * self.width, 0, self.width, self.height))
  
        return pygame.transform.scale(frame, (30, 30))
    
    def animation(self):
        self.index_image += self.vitesse_animation
        if self.index_image >= len(self.frames):
            self.index_image = 0.0
    
    def update(self, player_health, index):
        # LOGIQUE DE CHANGEMENT D'ÉTAT
        if index < player_health:
            self.state = "ALIVE"
        elif index == player_health and self.state == "ALIVE":
            # Si le joueur vient de perdre ce point de vie
            self.state = "DYING"
            self.index_anim = 0 # Réinitialiser l'index d'animation pour la mort
        elif index > player_health and self.state != "DYING":
            self.state = "DEAD"

        # GESTION DES ANIMATIONS SELON L'ÉTAT
        if self.state == "ALIVE":
            self.index_anim += self.vitesse_animation
            self.image = self.frames_idle[int(self.index_anim % len(self.frames_idle))]
            
        elif self.state == "DYING":
            self.index_anim += self.vitesse_animation
            if self.index_anim < len(self.frames_death):
                self.image = self.frames_death[int(self.index_anim)]
            else:
                self.state = "DEAD" # Une fois l'animation finie, on passe en mort
                
        elif self.state == "DEAD":
            self.image = self.frames_death[-1] # On reste sur la dernière frame 