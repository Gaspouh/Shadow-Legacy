import pygame

class animation:
    def __init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge):
            
        ecran = fenetre
        
        # Charger une image d'ennemi
        sheet = pygame.image.load(sprite_sheet).convert_alpha()
        frames_droite = []
        frames_gauche = []
        for i in range(nb_frames): 
            # stocker les frames d'animation dans des listes pour la droite et la gauche
            frame = self.changer_frame(i, width, height, marge, sheet)
            frames_droite.append(frame)
            frames_gauche.append(pygame.transform.flip(frame, True, False))
        
        # variable d'animation
        index_image = 0.0
        vitesse_animation = 0.1

        # définir coordonnées du sprite
        image = frames_droite[0]
        rect = image.get_rect(center=(x, y))

        # mouvement du sprite
        self.frames_droite = frames_droite
        self.frames_gauche = frames_gauche
        self.rect = rect
        self.index_image = index_image
        self.vitesse_animation = vitesse_animation

    def changer_frame(self, index, width, height, marge, sheet ):
            # Extraire une frame de la feuille de sprite
            frame = pygame.Surface((width, height), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), (marge + (index * width), 250 , width, height))
            return frame
        
    def gestion_animation(self, index_image, vitesse_animation, frames_droite):
            # Mettre à jour l'index de la frame pour l'animation
            index_image += vitesse_animation
            if index_image >= len(frames_droite):
                # Réinitialiser l'index pour recommencer l'animation
                index_image = 0.0
            return index_image