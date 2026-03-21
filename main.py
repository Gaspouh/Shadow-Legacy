import pygame
import os
from perso import Player
from ennemi import ennemi_debutant, Araignee, Volant
from map import Platform, platforms, Checkpoint, checkpoints
from camera import Camera
from vfx import particles, Particle
from traps import Spike
from objets import Coeur
from sprite_sheet import *
from save import sauvegarder, charger, get_spawn_from_checkpoints


os.environ['SDL_RENDER_SCALE_QUALITY'] = '0' 
pygame.init()

# Sons
set_spawn_sound = pygame.mixer.Sound("set_spawn_sound.mp3")

# Créer une fenêtre de jeu
GAME_WIDTH, GAME_HEIGHT = 1920, 1080
MAP_WIDTH, MAP_HEIGHT = 5000, 2000

fenetre = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF, vsync=1)


camera = Camera(GAME_WIDTH, GAME_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
clock = pygame.time.Clock()

pygame.display.set_caption("Shadow Legacy")
 
# Création des objets du jeu
araignee1 = Araignee(fenetre, 300, 10)
volant1 = Volant(fenetre, 400, 200)
player = Player(100, 100, fenetre)
hearts = [Coeur(fenetre, 100 + i*110, 20) for i in range(player.max_health)]

spawn_point = charger(player, checkpoints)  # charge la save si elle existe, sinon spawn par défaut
player.position = pygame.math.Vector2(spawn_point.x, spawn_point.y)  # position du joueur maj à partir du spawn point
player.rect.midbottom = player.position # pareil avec la hitbox

# Liste des ennemis
araignee = [araignee1]
volant = [volant1]
liste_ennemis = araignee + volant

# Liste des pièges
spikes = [Spike(300, 300, 40), Spike(1560, 950, 40)]

# Variables pour le screen shake et le hitstop à initialiser
hitstop_until = -1
shake_amount = 0


def reset():
    global spawn_point
    player.health = player.max_health
    player.position = pygame.math.Vector2(spawn_point.x, spawn_point.y)  # respawn au dernier checkpoint
    player.velocity = pygame.math.Vector2(0, 0)
    player.acceleration = pygame.math.Vector2(0, 0)
    player.invincible = False
    for ennemi in liste_ennemis:
        ennemi.rect.x = ennemi.position_initiale_x
        ennemi.rect.y = ennemi.position_initiale_y 
        ennemi.velocity_y = 0
        ennemi.velocity_x = 0
    for heart in hearts:
        heart.state = "ALIVE"
        heart.index_anim = 0

continuer = True
while continuer:
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            continuer = False

        if now > hitstop_until and player.health > 0:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.press_jump()
                if event.key == pygame.K_LSHIFT:
                    player.dash.start_dash(player)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.press_attack()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    player.stop_jump()

    if player.health > 0:

        for i, heart in enumerate(hearts):
            heart.update(player.health, i)

        if now > hitstop_until:
            player.update(platforms)
            camera.update(player, shake_amount)
            
            if shake_amount > 0:
                shake_amount -= 1

            for elem in araignee:
                if elem.alive:  # vérifier que l'ennemi est vivant avant de le mettre à jour
                    elem.patrouille()
            """
            for elem in volant:
                elem.poursuite(player.rect)
            """
        
        # Gestion du recul et du pogo après une attaque
        for ennemi in liste_ennemis:
            if player.is_attacking and player.attack_rect.colliderect(ennemi.rect):
                if ennemi not in player.ennemis_touches:
                    player.ennemis_touches.append(ennemi)
                    ennemi.knockback(player.rect, player)  # argument player en plus

                    for _ in range(15):
                        particles.append(Particle(ennemi.rect.centerx, ennemi.rect.centery))

                    hitstop_until = now + 50
                    shake_amount = 5

                    if player.attack_direction == "DOWN": 
                        player.velocity.y = -10
                        player.double_jump.reset()
                    else:
                        knockback_force = 40
                        if player.direction == 1:
                            player.velocity.x = -knockback_force
                        else:
                            player.velocity.x = knockback_force
            
            if ennemi.rect.colliderect(player.rect):
                hitstop_duration, shake_amount = player.take_damage(ennemi.attack_data, ennemi.rect, "MOB")
                hitstop_until = pygame.time.get_ticks() + hitstop_duration

        for spike in spikes:
            if spike.rect.colliderect(player.rect):
                hitstop_duration, shake_amount = player.take_damage(spike.attack_data, spike.rect, "SPIKE")
                hitstop_until = pygame.time.get_ticks() + hitstop_duration

    # Dessiner les éléments du jeu sur la fenêtre
    if player.health > 0:
        fenetre.fill((135, 206, 235))
        
        # Plateformes
        for platform in platforms:
            fenetre.blit(platform.image, camera.apply(platform.rect))

        # Checkpoints (avant le joueur pour qu'il passe devant)
        for cp in checkpoints:
            fenetre.blit(cp.image, camera.apply(cp.rect))
            if cp.rect.colliderect(player.rect) and not cp.activated:
                cp.activated = True
                spawn_point = get_spawn_from_checkpoints(checkpoints)   # recalcul depuis les checkpoints
                sauvegarder(player, checkpoints)    # sauvegarde automatique
                set_spawn_sound.play()
                
        # Ennemis
        for elem in araignee:
            fenetre.blit(elem.image, camera.apply(elem.rect))
        for elem in volant:
            fenetre.blit(elem.image, camera.apply(elem.rect))

        # Pièges
        for spike in spikes:
            fenetre.blit(spike.image, camera.apply(spike.rect)) 

        # Joueur
        image_rect = player.image.get_rect(midbottom=player.rect.midbottom)
        if not player.invincible or (pygame.time.get_ticks() // 100) % 2 == 0:
            fenetre.blit(player.image, camera.apply(image_rect))

        if player.is_attacking:
            pygame.draw.rect(fenetre, (255, 0, 0), camera.apply(player.attack_rect))

        # Particules
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)
            else:
                p.draw(fenetre, camera)
        
        # Cœurs (UI — fixes à l'écran, sans camera.apply)
        for heart in hearts:
            fenetre.blit(heart.image, heart.rect)

    else:
        fenetre.fill((0, 0, 0))
        pygame.display.update()
        pygame.time.delay(1000)
        reset()

    pygame.display.update()
    clock.tick(60)

pygame.quit()