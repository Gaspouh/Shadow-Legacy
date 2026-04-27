import pygame
from Core.save import sauvegarder
def menu(fenetre, player, checkpoints):
    pause = True
    # Afficher le menu
    noir_transparent = pygame.Surface((fenetre.get_width(), fenetre.get_height()))
    noir_transparent.fill((0, 0, 0)) # Remplir avec du noir
    noir_transparent.set_alpha(220) # Définir la transparence 
    image_menu = pygame.image.load("Assets/Images/pause.png").convert_alpha()
        
    # Définir les boutons
    bouton_reprendre = pygame.Rect(fenetre.get_width() // 2 - 100, fenetre.get_height() // 2 - 50, 200, 40)
    bouton_options = pygame.Rect(fenetre.get_width() // 2 - 100, fenetre.get_height() // 2 + 20, 200, 40)
    bouton_quitter = pygame.Rect(fenetre.get_width() // 2 - 130, fenetre.get_height() // 2 + 95, 260, 40)

    # actualiser l'affichage du menu
    fenetre.blit(noir_transparent, (0, 0)) 
    fenetre.blit(image_menu, (fenetre.get_width() // 2 - image_menu.get_width() // 2, fenetre.get_height() // 2 - image_menu.get_height() // 2))

    while pause:
        souris_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if bouton_reprendre.collidepoint(event.pos):
                    return False  # Reprendre le jeu
                #elif bouton_options.collidepoint(event.pos):
                    
                elif bouton_quitter.collidepoint(event.pos):
                    sauvegarder(player, checkpoints, map) # Sauvegarder avant de quitter
                    pygame.quit()  # Quitter le jeu
                    exit()

        if bouton_reprendre.collidepoint(souris_pos):
            r1, g1, b1 = 255, 255 , 255
        else :
            r1, g1, b1 = 0, 0, 0

        if bouton_options.collidepoint(souris_pos):
            r2, g2, b2 = 255, 255 , 255
        else :
            r2, g2, b2 = 0, 0, 0

        if bouton_quitter.collidepoint(souris_pos):
            r3, g3, b3 = 255, 255 , 255
        else :
            r3, g3, b3 = 0, 0, 0

        # Dessiner les boutons
        pygame.draw.rect(fenetre, (r1, g1, b1), bouton_reprendre, 2)
        pygame.draw.rect(fenetre, (r2, g2, b2), bouton_options, 2)
        pygame.draw.rect(fenetre, (r3, g3, b3), bouton_quitter, 2)
        pygame.display.update()
    return pause