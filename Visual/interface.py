import pygame
from Core.save import sauvegarder, charms_images, SAVE_FILE
import os
import json

def menu(fenetre, player, checkpoints, current_map):
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
                    sauvegarder(player, checkpoints, current_map) # Sauvegarder avant de quitter
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


def sit_on_bench(fenetre):
    """ Ouvre l'inventaire lorsque le joueur est assis sur un banc + gestion des charms equippés et drag """
    open_inventory = True
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    found_charms_data = data.get("player", {}).get("found_charms", {})
    assets_path = charms_images()
    charms_afficher = []    # Initialisation des charms trouvé affichable
    decalage_x = 100 # valeur test pour apres pouvroi aligner les charms

    for name, active in found_charms_data.items():  # Pour récupérer valeur et clé de chaque charm
        if active == True:  # Si charm trouvé c'est True, il est affiché alors
            if name in assets_path:
                image_1 = pygame.image.load(assets_path[name]).convert_alpha()   #Compare avec la liste de path d'image, pour récuperer l'asset
                image = pygame.transform.scale(image_1, (image_1.get_width()/1.8, image_1.get_height()/1.8))
                rect = image.get_rect(topleft=(decalage_x, 200))
                charms_afficher.append({"img": image, "rect": rect, "name": name})
                decalage_x += 50 + image.get_width()
        
    charm_selected = None   # Pouvoir selectionner un item à la fois pour le drag and drop
    offset_x, offset_y = 0, 0

    # Fond (meme que menu)
    noir_transparent = pygame.Surface((fenetre.get_width(), fenetre.get_height()))
    noir_transparent.fill((0, 0, 0))
    noir_transparent.set_alpha(220) 
    
    inventaire_pic = pygame.image.load("Assets/Images/inventaire_charms.png").convert_alpha()
    inventaire_rec = inventaire_pic.get_rect(center=(fenetre.get_width()//2, fenetre.get_height()//2))

    # centrer l'image
    pos_x = fenetre.get_width() // 2 - inventaire_pic.get_width() // 2
    pos_y = fenetre.get_height() // 2 - inventaire_pic.get_height() // 2

    pygame.display.update()

    while open_inventory:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if event.type == pygame.KEYDOWN:
                # Quitter avec Echap ou E
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_e:
                    open_inventory = False
                    # Return False

            # Gestion du clic
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:    # le clic gauche
                    for charm in charms_afficher:
                        if charm["rect"].collidepoint(mouse_pos):
                            charm_selected = charm  # le charm selectionné est le charm où la pos de la souris y est
                            # ajout d'un delta pour calculer la différence entre la ou on clic et la ou se situe le rect :
                            offset_x = charm["rect"].x - mouse_pos[0]
                            offset_y = charm["rect"].y- mouse_pos[1]
                            break
                                    
            # si relachement il n'y a plus de charme selectionné
            if event.type == pygame.MOUSEBUTTONUP:
                charm_selected = None
            
        # gestion deplacement quand un charm est selectionné
        if charm_selected != None:
            charm_selected["rect"].x = mouse_pos [0] + offset_x
            charm_selected["rect"].y = mouse_pos [1] + offset_y

        # Affichage
        fenetre.blit(noir_transparent, (0, 0))
        fenetre.blit(inventaire_pic, inventaire_rec)

        # dessiner chaque charms possédés
        for charm in charms_afficher:
            fenetre.blit(charm["img"], charm["rect"])

        pygame.display.update()