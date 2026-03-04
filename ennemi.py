import pygame

pygame.init()

class ennemi_debutant():
    def __init__(self, fenetre):
        self.ecran = fenetre
        self.clock = pygame.time.Clock()
        # Charger une image d'ennemi
        self.sheet = pygame.image.load('insecte_sheet2.png').convert_alpha()
        self.frames_droite = []
        self.frames_gauche = []
        for i in range(8): 
            # stocker les frames d'animation dans des listes pour la droite et la gauche
            frame = self.changer_frame(i, 70, 50)
            self.frames_droite.append(frame)
            self.frames_gauche.append(pygame.transform.flip(frame, True, False))
        
        # variable d'aniamtion
        self.index_image = 0.0
        self.vitesse_animation = 0.1
        self.direction = 1  # 1 pour droite, -1 pour gauche
        self.vitesse_deplacement = 1.70
        self.position_initiale_x = 100 # Position de départ de l'ennemi sur l'axe x
        self.distance_patrouille = 400 # Distance max avant de faire demi-tour

        # définir coordonnées de l'ennemi
        self.image = self.frames_droite[0]
        self.rect = self.image.get_rect(center=(self.position_initiale_x, 300))
    
    def changer_frame(self, index, width, height):
        # Extraire une frame de la feuille de sprite
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(self.sheet, (0, 0), (13+index * width,250 , width, height))
        return frame
    
    def gestion_animation(self):
        # Mettre à jour l'index de la frame pour l'animation
        self.index_image += self.vitesse_animation
        if self.index_image >= len(self.frames_droite):
            # Réinitialiser l'index pour recommencer l'animation
            self.index_image = 0.0
        self.image = self.frames_droite[int(self.index_image)] if self.direction == 1 else self.frames_gauche[int(self.index_image)]
        self.rect.x += self.vitesse_deplacement * self.direction
        # Vérifier si l'ennemi a atteint la distance de patrouille et changer de direction si nécessaire
        if self.rect.x >= self.position_initiale_x + self.distance_patrouille:
            self.direction = -1
        elif self.rect.x <= self.position_initiale_x:
            self.direction = 1

if __name__ == "__main__":
     # Créer une fenêtre de jeu
    ecran = pygame.display.set_mode((800, 600))
    ennemi = ennemi_debutant(ecran)
    pygame.quit()