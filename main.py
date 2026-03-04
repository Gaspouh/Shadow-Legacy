import pygame
from perso import Player, Platform
from ennemi import ennemi_debutant, Araignee, Volant
from map import platforms

pygame.init()
# Créer une fenêtre de jeu
fenetre = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
# Définir le titre de la fenêtre
pygame.display.set_caption("Shadow Legacy")
 
# Création des objets du jeu
araignee1 = Araignee(fenetre, 300, 10)
volant1 = Volant(fenetre, 400, 200)
player = Player(100, 100, fenetre)

# Liste des ennemis
araignee = [araignee1]
volant = [volant1]

continuer = True
while continuer:
    for event in pygame.event.get():
        # quitter le jeu
        if event.type == pygame.QUIT:
            continuer = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # faire sauter le joueur
                player.jump()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                # arrêter le saut du joueur pour permettre un saut plus court
                player.stop_jump()

    player.update(platforms)# Mettre à jour le joueur avec les plateformes pour gérer les collisions
    
    for elem in araignee:
        #lancer la fonction de patrouille pour chaque araignée
        elem.patrouille()
    for elem in volant:
        #lancer la fonction de poursuite pour chaque volant
        elem.poursuite(player.rect)
    
      # Remplir le fond 
    fenetre.fill((135, 206, 235))  # Couleur de fond (ciel bleu)

    for platform in platforms:
        # Dessiner les plateformes
        fenetre.blit(platform.image, platform.rect)

    # Dessiner les personnages
    for elem in araignee:
        fenetre.blit(elem.image, elem.rect)
    for elem in volant:
        fenetre.blit(elem.image, elem.rect)
    image_rect = player.image.get_rect(midbottom=player.rect.midbottom)
    fenetre.blit(player.image, image_rect)
    
# Mettre à jour l'affichage
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
