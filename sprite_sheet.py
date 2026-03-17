import pygame

def charger_sprite(fenetre, x, y, sprite_sheet, nb_frames, width, height, vitesse, marge):
        
    ecran = fenetre
    
    # Charger une image d'ennemi
    sheet = pygame.image.load(sprite_sheet).convert_alpha()
    frames_droite = []
    frames_gauche = []
    for i in range(nb_frames): 
        # stocker les frames d'animation dans des listes pour la droite et la gauche
        frame = changer_frame(i, width, height, marge)
        frames_droite.append(frame)
        frames_gauche.append(pygame.transform.flip(frame, True, False))
    
    # variable d'animation
    index_image = 0.0
    vitesse_animation = 0.1

    # définir coordonnées du sprite
    image = frames_droite[0]
    rect = image.get_rect(center=(x, y))

    # mouvement du sprite
    velocity_x = 0
    velocity_y = 0

    def changer_frame(index, width, height, marge):
        # Extraire une frame de la feuille de sprite
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (marge + (index * width), 250 , width, height))
        return frame
    
    def gestion_animation():
        # Mettre à jour l'index de la frame pour l'animation
        index_image += vitesse_animation
        if index_image >= len(frames_droite):
            # Réinitialiser l'index pour recommencer l'animation
            index_image = 0.0