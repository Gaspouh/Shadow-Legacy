import pygame

pygame.init()

class ennemi_debutant:
    def __init__(self):
        # Créer une fenêtre
        self.ecran = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        # Charger une image d'ennemi
        self.sheet = pygame.image.load('insecte_sheet2.png').convert_alpha()
        self.frames_droite = []
        self.frames_gauche = []
        for i in range(8): 
            frame = self.changer_frame(i, 70, 50)
            self.frames_droite.append(frame)
            self.frames_gauche.append(pygame.transform.flip(frame, True, False))

        self.index_image = 0.0
        self.vitesse_animation = 0.1
        self.direction = 1  # 1 pour droite, -1 pour gauche
        self.vitesse_deplacement = 1.70
        self.position_initiale_x = 100
        self.distance_patrouille = 400 # Distance max avant de faire demi-tour

        # définir coordonnées de l'ennemi
        self.image = self.frames_droite[0]
        self.rect = self.image.get_rect(center=(self.position_initiale_x, 300))
        self.afficher()

    def afficher(self):
        continuer = True
        while continuer:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    continuer = False
            self.gestion_animation()
            # Remplir le fond 
            self.ecran.fill((30, 30, 30))
            # Dessiner le personnage
            self.ecran.blit(self.image, self.rect)
            # Mettre à jour l'affichage
            pygame.display.flip()
            self.clock.tick(60)
    
    def changer_frame(self, index, width, height):
        # Extraire une frame de la feuille de sprite
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(self.sheet, (0, 0), (13+index * width,250 , width, height))
        return frame
    
    def gestion_animation(self):
        self.index_image += self.vitesse_animation
        if self.index_image >= len(self.frames_droite):
            self.index_image = 0.0
        centre_actuel = self.rect.center
        self.image = self.frames_droite[int(self.index_image)] if self.direction == 1 else self.frames_gauche[int(self.index_image)]
        self.rect = self.image.get_rect(center=centre_actuel)
        self.rect.x += self.vitesse_deplacement * self.direction
        # Vérifier si l'ennemi a atteint la distance de patrouille
        if self.rect.x >= self.position_initiale_x + self.distance_patrouille:
            self.direction = -1
        elif self.rect.x <= self.position_initiale_x:
            self.direction = 1

if __name__ == "__main__":
    ennemi_debutant()
    pygame.quit()