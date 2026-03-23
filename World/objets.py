import pygame
from Visual.sprite_sheet import *
 
class Coeur(Animation):
    def __init__(self, fenetre, x, y):
        super().__init__(fenetre, x, y, 'Assets/Images/coeur2.png', 8, 92, 90, 0, 2)
        self.state = "ALIVE"

        for frame in self.frames_droite:
            # Redimensionner pour l'affichage
            self.frames_droite.append(pygame.transform.smoothscale(frame, (70, 70)))
            self.frames_droite.remove(frame)
       
    def update(self, current_player_health, heart_index):

        # on compare l'index du cœur avec la santé actuelle du joueur pour déterminer l'état du cœur
        if heart_index >= current_player_health and self.state == "ALIVE":
            # on enlève un cœur si la santé du joueur diminue
            self.state = "DYING"
            self.index_image = 0  # On reset l'anim pour jouer la séquence de mort
        
        # on ajoute un coeur si la santé du joueur augmente
        elif heart_index < current_player_health and self.state != "ALIVE":
            self.state = "ALIVE"
        
        # on laisse le coeur vivant
        if self.state == "ALIVE":
            self.index_image += self.vitesse_animation
            self.image = self.frames_droite[0]
        
        # on joue l'animation de mort du cœur
        elif self.state == "DYING":
            self.index_image += self.vitesse_animation
            if self.index_image < len(self.frames_droite):
                self.image = self.frames_droite[int(self.index_image)]
            else:
                self.state = "DEAD"
                
        # on affiche un cœur vide si le cœur est mort
        elif self.state == "DEAD":
            self.index_image = 0  
            self.index_image += self.vitesse_animation
            if self.index_image >= len(self.frames_droite):
                self.index_image = len(self.frames_droite) - 1  # Rester sur la frame du cœur vide
        Animation.gestion_animation(self)
            
