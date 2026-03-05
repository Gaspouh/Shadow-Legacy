import pygame
import random 
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
liste_ennemis = araignee + volant

# Variables pour le screen shake et le hitstop à initialiser
hitstop_until = -1 # Temps jusqu'auquel le hitstop est actif (initialisé à une valur passée)
shake_amount = 0 # Intensité du screen shake

continuer = True
while continuer:
    now = pygame.time.get_ticks()
    if now < hitstop_until:
        continue # tant que le hitstop est actif on skip le reste de la boucle pour geler le jeu
    for event in pygame.event.get():
        # quitter le jeu
        if event.type == pygame.QUIT:
            continuer = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # faire sauter le joueur
                player.press_jump()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                # faire attaquer le joueur
                player.press_attack()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                # arrêter le saut du joueur pour permettre un saut plus court
                player.release_jump()

    player.update(platforms)# Mettre à jour le joueur avec les plateformes pour gérer les collisions
    
    for elem in araignee:
        #lancer la fonction de patrouille pour chaque araignée
        elem.patrouille()
    """
    for elem in volant:
        #lancer la fonction de poursuite pour chaque volant
        elem.poursuite(player.rect)"""
    
    # Gestion du recul et du pogo après une attaque
    keys = pygame.key.get_pressed()
    for enemi in liste_ennemis:
        if player.is_attacking and player.attack_rect.colliderect(enemi.rect):
            if enemi in player.ennemis_touches: # Si l'ennemi a déjà été touché par cette attaque, ne pas le toucher à nouveau
                continue
            player.ennemis_touches.append(enemi) # Ajouter l'ennemi à la liste des ennemis déjà touchés
            enemi.toucher(player.rect) # Appliquer les effets de toucher à l'ennemi (par exemple, réduire sa vie ou le faire reculer)

            hitstop_until = now + 100 # Activer le hitstop pendant 50ms
            shake_amount = 3 # Définir l'intensité du screen shake 

            if player.attack_direction == "DOWN": 
                player.velocity.y = -10 # Rebondir vers le haut après une attaque vers le bas
                print("Pogo")
            else :
                knockback_force = 40
                if player.direction == 1: # Reculer vers la droite
                    player.velocity.x = -knockback_force
                else: # Reculer vers la gauche
                    player.velocity.x = knockback_force
                print("Recul")
    
    # Gestion du screen shake
    render_offset = [0, 0] # Décalage de rendu pour le screen shake 
    if shake_amount > 0:
        render_offset = [random.randint(-shake_amount, shake_amount), \
                         random.randint(-shake_amount, shake_amount)] # Appliquer un décalage aléatoire pour créer l'effet de tremblement
        shake_amount -= 1 # Réduire progressivement l'intensité du screen shake
    
    # Remplir le fond 
    fenetre.fill((135, 206, 235))  # Couleur de fond (ciel bleu)

    for platform in platforms:
    # Dessiner les plateformes
        fenetre.blit(platform.image, platform.rect.move(render_offset)) # Appliquer le décalage de rendu pour le screen shake

    # Dessiner les personnages
    for elem in araignee:
        fenetre.blit(elem.image, elem.rect)
    for elem in volant:
        fenetre.blit(elem.image, elem.rect)
    image_rect = player.image.get_rect(midbottom=player.rect.midbottom)
    fenetre.blit(player.image, image_rect)

    if player.is_attacking:
        pygame.draw.rect(fenetre, (255, 0, 0), player.attack_rect) # Afficher la hitbox de l'attaque pour les tests
    
# Mettre à jour l'affichage
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
