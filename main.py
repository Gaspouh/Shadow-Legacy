import pygame
import os
from perso import Player
from ennemi import ennemi_debutant, Araignee, Volant
from map import Platform, platforms, Checkpoint, checkpoints
from camera import Camera
from vfx import particles, Particle
from traps import *
from objets import Coeur
from sprite_sheet import *
from save import sauvegarder, charger, get_spawn_from_checkpoints
from golem import Golem
from interface import menu


os.environ['SDL_RENDER_SCALE_QUALITY'] = '0' 
pygame.init()

# Créer une fenêtre de jeu
GAME_WIDTH, GAME_HEIGHT = 1920, 1080
MAP_WIDTH, MAP_HEIGHT = 5000, 2000

fenetre = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF, vsync=1)

spawn_point = pygame.math.Vector2(100, 100)  # point de spawn par défaut

camera = Camera(GAME_WIDTH, GAME_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
clock = pygame.time.Clock()

# Image
ui_reposer = pygame.image.load("player.png").convert_alpha()
ui_reposer = pygame.transform.scale(ui_reposer, (ui_reposer.get_width() /5.15, ui_reposer.get_height() / 5.15))

# Sons
set_spawn_sound = pygame.mixer.Sound("set_spawn_sound.mp3")


# Définir le titre de la fenêtre
pygame.display.set_caption("Shadow Legacy")
 
# Création des objets du jeu
araignee1 = Araignee(fenetre, 300, 10)
volant1 = Volant(fenetre, 400, 200)
player = Player(100, 100, fenetre)
hearts = [Coeur(fenetre, 100 + i*110, 35) for i in range(player.max_health)]
golem = Golem(fenetre, 800, 500) # spawn

spawn_point = charger(player, checkpoints)  # charge la save si elle existe, sinon spawn par défaut
player.position = pygame.math.Vector2(spawn_point.x, spawn_point.y)  # position du joueur maj à partir du spawn point
player.rect.midbottom = player.position # pareil avec la hitbox

# Liste des ennemis
araignee = [araignee1]
volant = [volant1]
liste_ennemis = araignee + volant

# Liste des pièges
spike = [Spike(300, 300, 40, 40), Spike(1560, 950, 40, 40)]
thorn = []
lava = []
quicksand = [Quicksand(1000, 420, 300, 100)]

traps = spike + thorn + lava + quicksand

# Variables pour le screen shake et le hitstop à initialiser
hitstop_until = -1 # Temps jusqu'auquel le hitstop est actif (initialisé à une valeur passée)
shake_amount = 0 # Intensité du screen shake



def reset():
        # Fonction de réinitialisation du jeu après la mort du joueur
    global spawn_point
    player.health = player.max_health
    player.position = pygame.math.Vector2(spawn_point.x, spawn_point.y)
    player.rect.midbottom = player.position
    player.velocity = pygame.math.Vector2(0, 0)
    player.acceleration = pygame.math.Vector2(0, 0)
    player.invincible = False
    for ennemi in liste_ennemis:
        # Chaque ennemi retourne à sa position de départ et reinitialise sa vitesse
        ennemi.rect.x = ennemi.position_initiale_x
        ennemi.rect.y = ennemi.position_initiale_y 
        ennemi.velocity_y = 0
        ennemi.velocity_x = 0
        ennemi.alive = True # Réactiver les ennemis
        ennemi.pv_ennemi = ennemi.pv_max  # Réinitialiser la santé de l'ennemi
    # Réinitialiser les cœurs
    for heart in hearts:
        heart.state = "ALIVE"
        heart.index_anim = 0

continuer = True
pause = False
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
                if event.key == pygame.K_ESCAPE:
                    pause = menu(fenetre)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    # faire attaquer le joueur
                    player.press_attack()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    # arrêter le saut du joueur pour permettre un saut plus court
                    player.stop_jump()

    if player.health > 0:

        # Mise à jour des cœurs
        for i, heart in enumerate(hearts):
            heart.update(player.health, i)

        if now > hitstop_until :
            player.current_slow_factor = 1
            player.current_jump_factor = 1
            player.wind_force_x = 0
            player.wind_force_y = 0
            player.in_quicksand = False

            for trap in traps:
                now = pygame.time.get_ticks()
                if trap.rect.colliderect(player.rect):

                    if trap.attack_data["damage"] > 0:
                        if trap.damage_cooldown == 0 or now - trap.last_damage_time >= trap.damage_cooldown :
                            
                            hitstop_duration, shake_amount = player.take_damage(trap.attack_data, trap.rect, trap)
                            trap.last_damage_time = now
                    
                    if trap.special_effect == "mud":
                        player.current_slow_factor = trap.slow_factor
                        player.current_jump_factor = trap.jump_factor
                    
                    if trap.special_effect == "wind":
                        player.wind_force_x = trap.force_x
                        player.wind_force_y = trap.force_y

                    if trap.special_effect == "quicksand":
                        player.in_quicksand = True
                        
            player.update(platforms)# Mettre à jour le joueur avec les plateformes pour gérer les collisions
            camera.update(player, shake_amount) # Mettre à jour la caméra pour suivre le joueur
            
            if shake_amount > 0:
                shake_amount -= 1 # Réduire progressivement l'intensité du screen shake

            for elem in araignee:
                if elem.alive: # Vérifier que l'ennemi est vivant avant de le mettre à jour
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
                    ennemi.knockback(player.rect, player) # Appliquer les effets de recul à l'ennemi 

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
                hitstop_duration, shake_amount = player.take_damage(ennemi.attack_data, ennemi.rect, ennemi) # Appliquer les effets de recul au joueur si un ennemi le touche
                hitstop_until = pygame.time.get_ticks() + hitstop_duration



        # Dessiner les éléments du jeu sur la fenêtre
        if player.health > 0 :
            fenetre.fill((135, 206, 235)) # Remplir le fond avec une couleur de ciel
            
            # Plateformes
            for platform in platforms:
                fenetre.blit(platform.image, camera.apply(platform.rect)) # Appliquer le décalage de rendu pour le screen shake

            # Checkpoints
            for cp in checkpoints:
                # 1. On calcule la position à l'écran UNE SEULE FOIS
                cp_screen_rect = camera.apply(cp.rect)
                fenetre.blit(cp.image, cp_screen_rect)

                # Quand le joueur est proche du banc
                if cp.rect.colliderect(player.rect) and not cp.activated:
                    
                    # UI (centrage)
                    ui_x = cp_screen_rect.centerx - (ui_reposer.get_width() // 2)
                    ui_y = cp_screen_rect.top - ui_reposer.get_height() - 10
                    fenetre.blit(ui_reposer, (ui_x, ui_y)) 

                    # Au lieu de juste "if 'E' pressed" qui appuierai 60 fois/s :
                    if pygame.key.get_pressed()[pygame.K_e]:
                        cp.activated = True
                        spawn_point = pygame.math.Vector2(cp.rect.topleft)
                        sauvegarder(player, checkpoints)
                        set_spawn_sound.play()
        """
        # Pièges
        for trap in traps:
            fenetre.blit(trap.image, camera.apply(trap.rect)) 
            pygame.draw.rect(fenetre, (0, 255, 255), camera.apply(trap.rect), 2)
        """

        # Joueur
        image_rect = player.image.get_rect(midbottom=player.rect.midbottom)
        if not player.invincible or (pygame.time.get_ticks() // 100) % 2 == 0: # Clignoter le sprite du joueur lorsqu'il est invincible
            fenetre.blit(player.image, camera.apply(image_rect))

        if player.is_attacking:
            pygame.draw.rect(fenetre, (255, 0, 0), camera.apply(player.attack_rect)) # Afficher la hitbox de l'attaque pour les tests

        # Ennemis
        for elem in araignee:
            fenetre.blit(elem.image, camera.apply(elem.rect)) # Shake
        for elem in volant:
            fenetre.blit(elem.image, camera.apply(elem.rect))
        
        # Boss
        golem.update(player.rect)
        golem.draw(fenetre, camera) # A modifier : Dans golem.py dans la fonction draw pour afficher les hitbox ou non
        if player.is_attacking and player.attack_rect.colliderect(golem.hitbox):
            golem.knockback(player.rect, player)
            fenetre.blit(golem.image, camera.apply(golem.rect))
        if golem.hitbox.colliderect(player.rect):
            hitstop_duration, shake_amount = player.take_damage(golem.attack_data, golem.rect, golem) # Recul du joueur
            hitstop_until = pygame.time.get_ticks() + hitstop_duration

        # Particules
        for p in particles[:]: # On utilise [:] pour copier la liste et éviter les erreurs de suppression
            p.update()
            if p.life <= 0:
                particles.remove(p)
            else:
                p.draw(fenetre, camera)
        
         # Afficher les cœurs
        for heart in hearts:
            fenetre.blit(heart.image, heart.rect) # Les cœurs sont fixes à l'écran, pas besoin d'appliquer le décalage de la caméra

    else:
        fenetre.fill((0, 0, 30)) # Afficher un écran noir lorsque le joueur n'a plus de santé
        pygame.display.update()
        pygame.time.delay(1000)
        reset()

        

# Mettre à jour l'affichage
    if not pause:
        pygame.display.update()
        clock.tick(60)

pygame.quit()
