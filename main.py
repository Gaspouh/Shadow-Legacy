import pygame
import random
import os
from perso import Player
from ennemi import ennemi_debutant, Araignee, Volant
from map import Platform, platforms
from camera import Camera
from vfx import particles, Particle
from map import Platform, platforms, Spike, spikes

os.environ['SDL_RENDER_SCALE_QUALITY'] = '0' 
pygame.init()

# Créer une fenêtre de jeu
GAME_WIDTH, GAME_HEIGHT = 1920, 1080
MAP_WIDTH, MAP_HEIGHT = 5000, 2000

fenetre = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF, vsync=1) # Créer une fenêtre en plein écran avec double buffering et accélération matérielle

camera = Camera(GAME_WIDTH, GAME_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
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
hitstop_until = -1 # Temps jusqu'auquel le hitstop est actif (initialisé à une valeur passée)
shake_amount = 0 # Intensité du screen shake


def reset():
        # Fonction de réinitialisation du jeu après la mort du joueur
        player.health = player.max_health
        player.position = pygame.math.Vector2(100, 400)
        player.velocity = pygame.math.Vector2(0, 0)
        player.acceleration = pygame.math.Vector2(0, 0)
        player.invincible = False
        for ennemi in liste_ennemis:
            # Chaque ennemi retourne à sa position de départ et reinitialise sa vitesse
            ennemi.rect.x = ennemi.position_initiale_x
            ennemi.rect.y = ennemi.position_initiale_y
            ennemi.velocity_y = 0
            ennemi.velocity_x = 0

continuer = True
while continuer:
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            continuer = False

        if now > hitstop_until and player.health > 0: # On traite les touches que si on n'est pas en histstop et en vie
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # faire sauter le joueur
                    player.press_jump()
                if event.key == pygame.K_LSHIFT:
                    # faire dasher le joueur
                    player.dash.start_dash(player) # Dash dans la direction du joueur
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    # faire attaquer le joueur
                    player.press_attack()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    # arrêter le saut du joueur pour permettre un saut plus court
                    player.stop_jump()

    if player.health > 0:
        if now > hitstop_until :
            player.update(platforms)# Mettre à jour le joueur avec les plateformes pour gérer les collisions
            camera.update(player, shake_amount) # Mettre à jour la caméra pour suivre le joueur
            
            if shake_amount > 0:
                shake_amount -= 1 # Réduire progressivement l'intensité du screen shake

            for elem in araignee:
                #lancer la fonction de patrouille pour chaque araignée
                elem.patrouille()
            """
            for elem in volant:
                #lancer la fonction de poursuite pour chaque volant
                elem.poursuite(player.rect)
            """
        
        # Gestion du recul et du pogo après une attaque
        for ennemi in liste_ennemis:
            if player.is_attacking and player.attack_rect.colliderect(ennemi.rect):
                if ennemi not in player.ennemis_touches: # Vérifier que cet ennemi n'a pas déjà été touché par cette attaque
                    player.ennemis_touches.append(ennemi) # Ajouter l'ennemi à la liste des ennemis déjà touchés
                    ennemi.toucher(player.rect) # Appliquer les effets de toucher à l'ennemi 

                    for _ in range(15): # 15 étincelles par coup
                        particles.append(Particle(ennemi.rect.centerx, ennemi.rect.centery))

                    hitstop_until = now + 50 # Activer le hitstop pendant 50ms
                    shake_amount = 5 # Définir l'intensité du screen shake 

                    if player.attack_direction == "DOWN": 
                        player.velocity.y = -10 # Rebondir vers le haut après une attaque vers le bas
                        player.double_jump.reset()
                    else :
                        knockback_force = 40
                        if player.direction == 1: # Reculer vers la droite
                            player.velocity.x = -knockback_force
                        else: # Reculer vers la gauche
                            player.velocity.x = knockback_force
            
            if ennemi.rect.colliderect(player.rect):
                player.toucher(player.rect, ennemi.rect) # Appliquer les effets de toucher au joueur si un ennemi le touche
    else :
        reset() # Réinitialiser le jeu si le joueur n'a plus de vie
   
    # Dessiner les éléments du jeu sur la fenêtre
    if player.health > 0 :
        fenetre.fill((135, 206, 235)) # Remplir le fond avec une couleur de ciel
        """ map """
        # Plateformes
        for platform in platforms:
            fenetre.blit(platform.image, camera.apply(platform.rect)) # Appliquer le décalage de rendu pour le screen shake

        # Spikes
        for spike in spikes:
            fenetre.blit(spike.image, camera.apply(spike.rect))
            
        """ ennemis et joueur """
        # Ennemis
        for elem in araignee:
            fenetre.blit(elem.image, camera.apply(elem.rect)) # Appliquer le décalage de rendu pour le screen shake

        for elem in volant:
            fenetre.blit(elem.image, camera.apply(elem.rect))
        
        # Affiner la collision du spike (de carre à triangle forme du spike)
        for spike in spikes:
            if spike.rect.colliderect(player.rect):
                player.toucher(player.rect, spike.rect)
        # Joueur
        image_rect = player.image.get_rect(midbottom=player.rect.midbottom)
        if not player.invincible or (pygame.time.get_ticks() // 100) % 2 == 0: # Clignoter le sprite du joueur lorsqu'il est invincible
            fenetre.blit(player.image, camera.apply(image_rect))

        if player.is_attacking:
            pygame.draw.rect(fenetre, (255, 0, 0), camera.apply(player.attack_rect)) # Afficher la hitbox de l'attaque pour les tests

        # Particules
        for p in particles[:]: # On utilise [:] pour copier la liste et éviter les erreurs de suppression
            p.update()
            if p.life <= 0:
                particles.remove(p)
            else:
                p.draw(fenetre, camera)

    else:
        fenetre.fill((0, 0, 0)) # Afficher un écran noir lorsque le joueur n'a plus de santé

        

# Mettre à jour l'affichage
    pygame.display.update()
    clock.tick(60)

pygame.quit()
