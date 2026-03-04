import pygame

pygame.init()

class ennemi_debutant(pygame.sprite.Sprite):
    def __init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, vitesse, marge):
        super().__init__()
        self.ecran = fenetre
        self.clock = pygame.time.Clock()
        # Charger une image d'ennemi
        self.sheet = pygame.image.load(sprite_sheet).convert_alpha()
        self.frames_droite = []
        self.frames_gauche = []
        for i in range(nb_frames): 
            # stocker les frames d'animation dans des listes pour la droite et la gauche
            frame = self.changer_frame(i, width, height, marge)
            self.frames_droite.append(frame)
            self.frames_gauche.append(pygame.transform.flip(frame, True, False))
        
        # variable d'animation
        self.index_image = 0.0
        self.vitesse_animation = 0.1

        # définir coordonnées de l'ennemi
        self.image = self.frames_droite[0]
        self.rect = self.image.get_rect(center=(x, y))

    def changer_frame(self, index, width, height, marge):
        # Extraire une frame de la feuille de sprite
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(self.sheet, (0, 0), (marge + (index * width), 250 , width, height))
        return frame
    
    def gestion_animation(self):
        # Mettre à jour l'index de la frame pour l'animation
        self.index_image += self.vitesse_animation
        if self.index_image >= len(self.frames_droite):
            # Réinitialiser l'index pour recommencer l'animation
            self.index_image = 0.0

class Araignee(ennemi_debutant):
    def __init__(self, fenetre, x, y):
        # On applique les caractéristique de l'ennemi débutant à l'araignée
        super().__init__(fenetre, x, y, 'insecte_sheet2.png', 8, 70, 50, 1.7, 13)

        self.direction = 1  # 1 pour droite, -1 pour gauche
        self.vitesse_deplacement = 1.7
        self.position_initiale_x = x # Position de départ de l'ennemi sur l'axe x
        self.distance_patrouille = 200 # Distance max avant de faire demi-tour

    def patrouille(self):
        ennemi_debutant.gestion_animation(self)
        # Afficher la bonne frame en fonction de la direction (orientation perso)
        self.image = self.frames_droite[int(self.index_image)] if self.direction == 1 else self.frames_gauche[int(self.index_image)]
        self.rect.x += self.vitesse_deplacement * self.direction
        # Vérifier si l'ennemi a atteint la distance de patrouille et changer de direction si nécessaire
        if self.rect.x >= self.position_initiale_x + self.distance_patrouille:
            self.direction = -1
        elif self.rect.x <= self.position_initiale_x:
            self.direction = 1
    
class Volant(ennemi_debutant):
    def __init__(self, fenetre, x, y):
        # On applique les caractéristique de l'ennemi débutant au volant
        super().__init__(fenetre, x, y, 'sprit_sheet_volant.png', 4, 50, 50, 1.7, 5)

        self.direction = 1  # 1 pour droite, -1 pour gauche
        self.vitesse_deplacement = 1.7
        self.position_initiale_x = x # Position de départ de l'ennemi sur l'axe x
        
    def poursuite(self, player_rect):
            ennemi_debutant.gestion_animation(self)
            # Afficher la bonne frame en fonction de la direction (orientation perso)
            self.image = self.frames_droite[int(self.index_image)] if self.direction == 1 else self.frames_gauche[int(self.index_image)]
            if player_rect.x > self.rect.x:
                self.direction = 1 # Aller vers la droite
            else:
                self.direction = -1 # Aller vers la gauche
            self.rect.x += self.vitesse_deplacement * self.direction # Déplacer horizontalement vers le joueur
            if player_rect.y > self.rect.y: # Si le joueur est en dessous de l'ennemi, descendre
                self.rect.y += self.vitesse_deplacement
            else:
                self.rect.y -= self.vitesse_deplacement # Si le joueur est au dessus de l'ennemi, monter

if __name__ == "__main__":
     # Créer une fenêtre de jeu
    ecran = pygame.display.set_mode((800, 600))
    ennemi = ennemi_debutant(ecran)
    pygame.quit()