import pygame
from Core.save import sauvegarder, charms_images, SAVE_FILE, supprimer_sauvegarde
import os
import json
from World.objets import Receptacle

pygame.mixer.init()
over_sound = pygame.mixer.Sound("Assets/Sounds/over_button.mp3")

def effet_bouton(image, rect, over_state):
    """ Effet d'animation quand la souris passe sur un bouton (colidepoint), plus pratique en fonction pour utiliser dans home_screen """
    mouse_pos = pygame.mouse.get_pos()
    mouse_hover = rect.collidepoint(mouse_pos)
    # il faut créer une nouvelle image pour pas écraser celle de base
    if rect.collidepoint(mouse_pos):
        if not over_state:
            over_sound.play()
        # Agrandir l'image
        new_width = int(image.get_width() * 1.1)
        new_height = int(image.get_height() * 1.1)
        new_image = pygame.transform.scale(image, (new_width, new_height))
        new_rect = new_image.get_rect(center=rect.center)   # nouveau rect aussi
        return new_image, new_rect, True
    else:
        return image, rect, False
    
def home_screen(fenetre):
    """ Affiche l'écran d'accueil du jeu avec les options de démarrage, de chargement et de sortie. """
    running = True
    over_reprendre = False
    over_quitter = False
    over_nouvelle_game = False

    click_sound = pygame.mixer.Sound("Assets/Sounds/click_button.mp3")

    # Charger les images
    background = pygame.image.load("Assets/Home/background_home_screen.png").convert()
    background = pygame.transform.scale(background, (fenetre.get_width(), fenetre.get_height()))

    # deplacer les bouttons à gauche de l'écran
    boutton_reprendre = pygame.image.load("Assets/Home/boutton_reprendre.png").convert_alpha()
    boutton_reprendre = pygame.transform.scale(boutton_reprendre, (boutton_reprendre.get_width()//1.4, boutton_reprendre.get_height()//1.4))
    rect_reprendre = boutton_reprendre.get_rect(topleft=(50, 190))

    boutton_quitter = pygame.image.load("Assets/Home/boutton_quitter.png").convert_alpha()
    boutton_quitter = pygame.transform.scale(boutton_quitter, (boutton_quitter.get_width()//3.1, boutton_quitter.get_height()//3.1))
    rect_quitter = boutton_quitter.get_rect(topleft=(50, 500))

    boutton_nouvelle_game = pygame.image.load("Assets/Home/boutton_nouvelle_game.png").convert_alpha()
    boutton_nouvelle_game = pygame.transform.scale(boutton_nouvelle_game, (boutton_nouvelle_game.get_width()//1.45, boutton_nouvelle_game.get_height()//1.45))
    rect_nouvelle_game = boutton_nouvelle_game.get_rect(topleft=(50, 350))
    
    while running:
        mouse_pos =pygame.mouse.get_pos()   # position de la souris pour chaque frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if rect_reprendre.collidepoint(event.pos):
                        click_sound.play()
                        pygame.time.delay(320)  # sinon le son a pas le temps de se jouer (running=false)
                        running = False # Passe au boucle du main pour lancer une game
                    elif rect_quitter.collidepoint(event.pos):
                        click_sound.play()
                        pygame.time.delay(320)
                        pygame.quit()  # Quitter le jeu
                        exit()
                    elif rect_nouvelle_game.collidepoint(event.pos):
                        click_sound.play()
                        pygame.time.delay(320)
                        # Supprimer les données de sauvegarde existantes pour une nouvelle partie
                        supprimer_sauvegarde()
                        running = False  # Supprime la save + Passe au boucle du main pour lancer une game

        # Affichage des éléements
        fenetre.blit(background, (0, 0))    

        # Utiliser l'effet de bulle pour les boutons
        img, rect, over_reprendre = effet_bouton(boutton_reprendre, rect_reprendre, over_reprendre) # on utilise "img" et "rect" pour chaque bouton car dans tout les cas 1 seul bouton à la fois est selectionné
        fenetre.blit(img, rect)

        img, rect, over_quitter = effet_bouton(boutton_quitter, rect_quitter, over_quitter)
        fenetre.blit(img, rect)

        img, rect, over_nouvelle_game = effet_bouton(boutton_nouvelle_game, rect_nouvelle_game, over_nouvelle_game)
        fenetre.blit(img, rect)
            
        pygame.display.update()

def menu(fenetre, player, checkpoints, current_map_name):
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
                    sauvegarder(player, checkpoints, current_map_name) # Sauvegarder avant de quitter
                    return "QUIT"   # au lieu de mainloop.continuer = False

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


def sit_on_bench(fenetre, player):
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

    j = player.receptacles_total // 3 # pour afficher les receptacles en les regroupant par 3 dans l'inventaire

    for i in range (j): # montre les réceptacles en les regroupant par 3
        image = pygame.image.load("Assets/Images/fragment3.png").convert_alpha()
        image2 = pygame.transform.scale(image, (image.get_width()/10.5, image.get_height()/10.5 - 10))
        rect = image2.get_rect(topleft=(430 + 73 * i, 275 ))
        charms_afficher.append({"img": image2, "rect": rect, "name": "receptacle"}) #les utiliser commme des charmes affichés dans l'inventaire
    
    if player.receptacles > 0: # Affiche les réceptacles en cours d'obtention dans l'inventaire

        if player.receptacles == 1:
            image = pygame.image.load("Assets/Images/fragment1.png").convert_alpha()

        elif player.receptacles == 2:
            image = pygame.image.load("Assets/Images/fragment2.png").convert_alpha()
    
        image2 = pygame.transform.scale(image, (image.get_width()/10.5, image.get_height()/10.5 - 10))
        rect = image2.get_rect(topleft=(430 + 73 * j, 275 ))
        charms_afficher.append({"img": image2, "rect": rect, "name": "receptacle"}) #les utiliser commme des charmes affichés dans l'inventaire

    for i in range (player.minerais):
        image = pygame.image.load("Assets/Images/minerai.png").convert_alpha()
        image3 = pygame.transform.scale(image, (image.get_width()/10.5 - 10, image.get_height()/10.5 - 10))
        if i < 4: # par ligne d'inventaire
            rect = image3.get_rect(topleft=(385 + 74 * i, 335))
        else:
            rect = image3.get_rect(topleft=(385 + 74 * (i-4), 403)) # ligne d'en dessous
        charms_afficher.append({"img": image3, "rect": rect, "name": "minerai"}) #les utiliser commme des charmes affichés dans l'inventaire
                                            
        
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