import pygame

def menu(fenetre):
    pause = True
    # Afficher le menu
    menu_image = pygame.image.load('pause.jpg').convert_alpha()
    menu_rect = menu_image.get_rect(center=(fenetre.get_width() // 2, fenetre.get_height() // 2))
    
    # Définir les boutons
    bouton_reprendre = pygame.Rect(menu_rect.centerx - 100, menu_rect.centery - 50, 200, 50)
    bouton_options = pygame.Rect(menu_rect.centerx - 100, menu_rect.centery + 20, 200, 50)
    bouton_quitter = pygame.Rect(menu_rect.centerx - 130, menu_rect.centery + 95, 260, 50)

    # actualiser l'affichage du menu
    fenetre.blit(menu_image, menu_rect)

    while pause:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if bouton_reprendre.collidepoint(event.pos):
                    return False  # Reprendre le jeu
                #elif bouton_options.collidepoint(event.pos):
                    
                elif bouton_quitter.collidepoint(event.pos):
                    pygame.quit()  # Quitter le jeu
                    exit()
          # Dessiner les boutons
        pygame.draw.rect(fenetre, (255, 255, 255), bouton_reprendre, 2)
        pygame.draw.rect(fenetre, (255, 255, 0), bouton_options, 2)
        pygame.draw.rect(fenetre, (255, 0, 0), bouton_quitter, 2)
        pygame.display.update()
    return pause