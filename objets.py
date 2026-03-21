import pygame
from sprite_sheet import *
 
class Coeur(Animation):
    def __init__(self, fenetre, x, y):
        super().__init__(fenetre, x, y, 'coeur.png', 5, 135, 95, 0)

    def update(self, current_player_health, heart_index):
        # on compare l'index du cœur avec la santé actuelle du joueur pour déterminer l'état du cœur
        if heart_index >= current_player_health and self.state == "ALIVE":
            # on enlève un cœur si la santé du joueur diminue
            self.state = "DYING"
            self.index_anim = 0  # On reset l'anim pour jouer la séquence de mort
        
        # on ajoute un coeur si la santé du joueur augmente
        elif heart_index < current_player_health and self.state != "ALIVE":
            self.state = "ALIVE"
        
        # on laisse le coeur vivant
        if self.state == "ALIVE":
            self.index_anim += self.vitesse_animation
            self.image = self.frames[0]
        
        # on joue l'animation de mort du cœur
        elif self.state == "DYING":
            self.index_anim += self.vitesse_animation
            if self.index_anim < len(self.frames):
                self.image = self.frames[int(self.index_anim)]
            else:
                self.state = "DEAD"
                
        # on affiche un cœur vide si le cœur est mort
        elif self.state == "DEAD":
            self.index_anim = 0  
            self.index_anim += self.vitesse_animation
            if self.index_anim >= len(self.frames):
                self.index_anim = 0
        
        Animation.gestion_animation(self)
            
