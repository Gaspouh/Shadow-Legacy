import pygame

class Animation:
    def __init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, scale):
        self.ecran = fenetre
        self.scale = scale

        # Charger une image d'ennemi
        sheet = pygame.image.load(sprite_sheet).convert_alpha()
        frames_droite = []
        frames_gauche = []
        for i in range(nb_frames): 
            # stocker les frames d'animation dans des listes pour la droite et la gauche
            frame = pygame.Surface((width, height), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0),(marge + (i * width), ligne * height, width, height))

            #Rescale pour pièges
            if scale != 1:
                frame = pygame.transform.scale(frame, (width * self.scale, height * self.scale))

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
        self.image = image  # Ajouter l'attribut image manquant
        
    def gestion_animation(self):
            # Mettre à jour l'index de la frame pour l'animation
            self.index_image += self.vitesse_animation
            if self.index_image >= len(self.frames_droite):
                # Réinitialiser l'index pour recommencer l'animation
                self.index_image = 0.0
            self.image = self.frames_droite[int(self.index_image)]
            return self.image
    
    def gestion_animation_once(self):
        self.vitesse_animation = 0.2
        fin = False
        self.index_image += self.vitesse_animation

        if self.index_image >= len(self.frames_droite) - 1:
            self.index_image = len(self.frames_droite) - 1  # Rester sur la dernière frame
            fin = True

        self.image = self.frames_droite[int(self.index_image)]
        return self.image, fin  # Retourner le bool fin pour indiquer si l'animation est terminée
    

# 2eme classe pour d'autres types de spritesheet
class VerticalAnimation:
    def __init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, colonne):
        self.ecran = fenetre
        sheet = pygame.image.load(sprite_sheet).convert_alpha()
        
        frames_droite = []
        frames_gauche = []
        
        for i in range(nb_frames): 
            # Verticalement
            frame = pygame.Surface((width, height), pygame.SRCALPHA)
            # multiplie le height
            frame.blit(sheet, (0, 0),(colonne * width, marge + (i * height), width, height))
            frames_droite.append(frame)
            frames_gauche.append(pygame.transform.flip(frame, True, False))
        
        self.frames_droite = frames_droite
        self.frames_gauche = frames_gauche
        self.rect = frames_droite[0].get_rect(center=(x, y))
        self.image = frames_droite[0]
        self.index_image = 0.0
        self.vitesse_animation = 0.1

    def gestion_animation(self):
        self.index_image += self.vitesse_animation
        if self.index_image >= len(self.frames_droite):
            self.index_image = 0.0
        self.image = self.frames_droite[int(self.index_image)]  
        return self.index_image
    
    def start_animation(self):
        """Lance l'animation"""
        self.is_playing = True
    
    def stop_animation(self, reset_frame=True):
        """Arrête l'animation"""
        self.is_playing = False
        if reset_frame:
            self.index_image = 0.0