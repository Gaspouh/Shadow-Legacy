import pygame
import random
from perso import Player, Platform
from ennemi import ennemi_debutant, Araignee, Volant
from map import platforms
from camera import Camera

pygame.init()
# Créer une fenêtre de jeu
fenetre = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = fenetre.get_size()

GAME_WIDTH, GAME_HEIGHT = 1920, 1080
virtuelle = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

MAP_WIDTH, MAP_HEIGHT = 5000, 2000
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
hitstop_until = -1 # Temps jusqu'auquel le hitstop est actif (initialisé à une valur passée)
shake_amount = 0 # Intensité du screen shake


def reset():
        # Fonction de réinitialisation du jeu après la mort du joueur
        player.health = player.max_health
        player.position = pygame.math.Vector2(100, 400)
        player.velocity = pygame.math.Vector2(0, 0)
        player.acceleration = pygame.math.Vector2(0, 0)
        player.coyote_timer = -1000
        player.jump_buffer_timer = -1000
        player.attack_timer = 0
        player.last_attack_time = -1000
        player.invincibility_timer = 0
        player.stun_timer = 0 
        for ennemi in liste_ennemis:
            # Chaque ennemi retourne à sa position de départ
            ennemi.rect.x = ennemi.position_initiale_x
            ennemi.rect.y = ennemi.position_initiale_y

continuer = True
while continuer:
    virtuelle.fill((135, 206, 235)) 
    if player.health > 0:
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
        camera.update(player) # Mettre à jour la caméra pour suivre le joueur

        for elem in araignee:
            #lancer la fonction de patrouille pour chaque araignée
            elem.patrouille()
        """
        for elem in volant:
            #lancer la fonction de poursuite pour chaque volant
            elem.poursuite(player.rect)"""
        
        # Gestion du recul et du pogo après une attaque
        keys = pygame.key.get_pressed()
        for ennemi in liste_ennemis:
            if player.is_attacking and player.attack_rect.colliderect(ennemi.rect):
                if ennemi in player.ennemis_touches: # Si l'ennemi a déjà été touché par cette attaque, ne pas le toucher à nouveau
                    continue
                player.ennemis_touches.append(ennemi) # Ajouter l'ennemi à la liste des ennemis déjà touchés
                ennemi.toucher(player.rect) # Appliquer les effets de toucher à l'ennemi 

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
        
            elif ennemi.rect.colliderect(player.rect):
                player.toucher(player.rect, ennemi.rect) # Appliquer les effets de toucher au joueur si un ennemi le touche
        
        # Gestion du screen shake
        render_offset = [0, 0] # Décalage de rendu pour le screen shake 
        if shake_amount > 0:
            render_offset = [random.randint(-shake_amount, shake_amount), \
                            random.randint(-shake_amount, shake_amount)] # Appliquer un décalage aléatoire pour créer l'effet de tremblement
            shake_amount -= 1 # Réduire progressivement l'intensité du screen shake

        for platform in platforms:
        # Dessiner les plateformes
            virtuelle.blit(platform.image, camera.apply(platform.rect).move(render_offset)) # Appliquer le décalage de rendu pour le screen shake

        # Dessiner les personnages
        for elem in araignee:
            virtuelle.blit(elem.image, camera.apply(elem.rect.move(render_offset))) # Appliquer le décalage de rendu pour le screen shake
        for elem in volant:
            virtuelle.blit(elem.image, camera.apply(elem.rect.move(render_offset))) # Appliquer le décalage de rendu pour le screen shake
        image_rect = player.image.get_rect(midbottom=player.rect.midbottom)

        if not player.invincible or (pygame.time.get_ticks() // 100) % 2 == 0: # Clignoter le sprite du joueur lorsqu'il est invincible
            virtuelle.blit(player.image, camera.apply(image_rect.move(render_offset)))

        if player.is_attacking:
            pygame.draw.rect(virtuelle, (255, 0, 0), player.attack_rect.move(render_offset)) # Afficher la hitbox de l'attaque pour les tests
    else:
        virtuelle.fill((0, 0, 0)) # Afficher un écran noir lorsque le joueur n'a plus de santé
        reset() # Réinitialiser le jeu lorsque la santé du joueur atteint 0

# Mettre à jour l'affichage
    image_ecran = pygame.transform.scale(virtuelle, (SCREEN_WIDTH, SCREEN_HEIGHT)) # Redimensionner la surface virtuelle pour l'adapter à la taille de l'écran
    fenetre.blit(image_ecran, (0, 0)) # Afficher la surface
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
