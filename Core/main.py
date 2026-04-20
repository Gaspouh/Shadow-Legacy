import pygame
import os
import sys
from random import randint
# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Entities.perso import Player
from Entities.ennemi import Ennemi, Araignee, Volant, Projectile, Tourelle
from World.map import Platform, platforms, special_platforms, Checkpoint, checkpoints
from Visual.camera import Camera
from Visual.vfx import particles, Particle
from World.traps import *
from World.objets import Coeur, Monnaie
from Visual.sprite_sheet import *
from Core.save import sauvegarder, charger, get_spawn_from_checkpoints
from Entities.boss import Golem, Gravelion
from Visual.interface import menu
from Core.reset import reset
from Entities.player_abilities import sort

os.environ['SDL_RENDER_SCALE_QUALITY'] = '0' 
pygame.init()

# Créer une fenêtre de jeu
GAME_WIDTH, GAME_HEIGHT = 1920, 1080
MAP_WIDTH, MAP_HEIGHT = 7000, 2000

fenetre = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF, vsync=1)

spawn_point = pygame.math.Vector2(100, 100)  # point de spawn par défaut

camera = Camera(GAME_WIDTH, GAME_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
clock = pygame.time.Clock()

# Image
ui_reposer = pygame.image.load("Assets/Images/UI_'Pressez_E'.png").convert_alpha()
ui_reposer = pygame.transform.scale(ui_reposer, (ui_reposer.get_width() /5.15, ui_reposer.get_height() / 5.15))

# Sons
set_spawn_sound = pygame.mixer.Sound("Assets/Sounds/set_spawn_sound.mp3")
death_sound = pygame.mixer.Sound("Assets/Sounds/elden-ring-death.mp3")

arene_gravelion = pygame.Rect(5000, 0, 1000, 600) 
trigger_combat = pygame.Rect(5100, 0, 50, 600)
porte_arene = Platform(5000, 0, 20, 600, (80, 80, 80))  # mur gauche

# Définir le titre de la fenêtre
pygame.display.set_caption("Shadow Legacy")

# Création des objets du jeu
araignee1 = Araignee(fenetre, 300, 10)
volant1 = Volant(fenetre, 400, 200)
player = Player(100, 100, fenetre)
hearts = [Coeur(fenetre, 100 + i*110, 35) for i in range(player.max_health)]
monnaie = Monnaie(fenetre, 200, 200)
golem = Golem(fenetre, 800, 300) # spawn
gravelion = Gravelion(fenetre, 5600, 300, arene_gravelion) # spawn dans l'arène de Gravelion
tourelle1 = Tourelle(fenetre, 600, 300)


spawn_point = charger(player, checkpoints)  # charge la save si elle existe, sinon spawn par défaut
player.position = pygame.math.Vector2(spawn_point.x, spawn_point.y)  # position du joueur maj à partir du spawn point
player.rect.midbottom = player.position # pareil avec la hitbox

# Liste des ennemis
araignee = [araignee1]
volant = [volant1]
tourelle = [tourelle1]
liste_ennemis = araignee + volant + tourelle

# Liste des pièges
spike = [Spike(300, 300, 40, 40), Spike(1560, 950, 40, 40)]
thorn = []
lava = []
traps = spike + thorn + lava

# Liste des projectiles
projectiles = []
tir_tourelle = []

# Variables pour le screen shake et le hitstop à initialiser
hitstop_until = -1 # Temps jusqu'auquel le hitstop est actif (initialisé à une valeur passée)
shake_amount = 0 # Intensité du screen shake

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
                    pause = menu(fenetre, player, checkpoints)
                if event.key == pygame.K_f:
                    # faire lancer le sort
                    if player.sort.use(player):
                        direction = player.direction
                        x = player.rect.centerx + (direction * 30)
                        y = player.rect.centery
                        target_x = x + (direction * 1000)  # tire loin devant
                        target_y = y
                        projectile = Projectile(x, y, target_x, target_y, 15, 80, 80, 3)
                        projectiles.append(projectile)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    # faire attaquer le joueur
                    player.press_attack()
                    shake_amount = randint(2, 3)
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
            player.on_ice = False
        
            # Pieges
            for trap in traps:
                now = pygame.time.get_ticks()

                if player.is_attacking and player.attack_rect.colliderect(trap.rect):

                    if trap not in player.entite_touches: # Vérifier que ce piège n'a pas déjà été touché par cette attaque

                        player.entite_touches.append(trap) # Ajouter le piège à la liste d'entités déjà touchées
                        player.attack_feedback(trap)

                if trap.rect.colliderect(player.rect):

                    if trap.attack_data["damage"] > 0:

                        if trap.damage_cooldown == 0 or now - trap.last_damage_time >= trap.damage_cooldown :
                            
                            hitstop_duration, shake_amount = player.take_damage(trap.attack_data, trap.rect, trap)
                            trap.last_damage_time = now

                    if trap.special_effect == "wind":
                        player.wind_force_x = trap.force_x
                        player.wind_force_y = trap.force_y

            special_surfaces = []
            for sp in special_platforms:

                if sp.surface is not None:
                    special_surfaces.append(sp.surface)

                if sp.rect.colliderect(player.rect):

                    if sp.effect == "mud":
                        player.current_slow_factor = sp.slow_factor
                        player.current_jump_factor = sp.jump_factor
                    
                    elif sp.effect == "quicksand":
                        player.in_quicksand = True

                    elif sp.effect == "ice":
                        player.on_ice = True

            player.update(platforms + special_surfaces)# Mettre à jour le joueur avec les plateformes pour gérer les collisions
            camera.update(player, shake_amount) # Mettre à jour la caméra pour suivre le joueur
            
            if shake_amount > 0:
                shake_amount -= 1 # Réduire progressivement l'intensité du screen shake

            for elem in araignee:
                if elem.alive and abs(elem.position.x - player.position.x) < 700: # Vérifier que l'ennemi est vivant et proche avant de le mettre à jour
                #lancer la fonction de patrouille pour chaque qaraignée
                    elem.patrouille(platforms)
            
            for elem in volant:
                if elem.alive and abs(elem.position.x - player.position.x) < 700: # Vérifier que l'ennemi est vivant et proche avant de le mettre à jour
                    #lancer la fonction de poursuite pour chaque volant
                    elem.poursuite(player.rect)
            
            for elem in tourelle: 
                if elem.alive and abs(elem.position.x - player.position.x) < 700: # Vérifier que l'ennemi est vivant et proche avant de le mettre à jour
                    elem.update(player.rect)
                    elem.tir(player.rect, tir_tourelle)#lancer la fonction de tir pour chaque tourelle
            
        # Gestion du recul et du pogo après une attaque
        for ennemi in liste_ennemis:
            if player.is_attacking and player.attack_rect.colliderect(ennemi.rect):
                if ennemi not in player.entite_touches and ennemi.alive: # Vérifier que cet ennemi n'a pas déjà été touché par cette attaque ou est mort
                    if player.sang < player.sang_max:
                        player.sang += 11 # charge la jauge de sang 
                    else :
                        player.sang = player.sang_max
                    player.entite_touches.append(ennemi) # Ajouter l'ennemi à la liste d'entités déjà touchées
                    if player.attack_data["critical"] : # Si coup critique
                        player.attack_data["damage"] = player.attack * 3
                        print("CRIT !!!")
                    player.attack_feedback(ennemi)
                    ennemi.receive_hit(player.attack_data, player.rect, player) # Appliquer les effets de recul à l'ennemi 
                    for _ in range(15): # 15 étincelles par coup
                        particles.append(Particle(ennemi.rect.centerx, ennemi.rect.centery))

                    hitstop_until = now + 50 # Activer le hitstop pendant 50ms
                    shake_amount = 4 # Définir l'intensité du screen shake 
            if not ennemi.alive:
                ennemi.mort()
            
            if not ennemi.alive and ennemi.animation_mort.index_image >= len(ennemi.animation_mort.frames_droite)-1:
                liste_ennemis.remove(ennemi)
            
            if ennemi.rect.colliderect(player.rect):
                hitstop_duration, shake_amount = player.take_damage(ennemi.attack_data, ennemi.rect, ennemi) # Appliquer les effets de recul au joueur si un ennemi le touche
                hitstop_until = pygame.time.get_ticks() + hitstop_duration
            
        for tir in projectiles:
            if tir.rect.colliderect(ennemi.rect):
                if ennemi not in player.tir_touches and ennemi.alive:
                    player.tir_touches.append(ennemi)  
                    ennemi.receive_hit(tir.attack_data, tir.rect, player)
                    for _ in range(15):
                        particles.append(Particle(ennemi.rect.centerx, ennemi.rect.centery))

        # Dessiner les éléments du jeu sur la fenêtre
        fenetre.fill((135, 206, 235)) # Remplir le fond avec une couleur de ciel
            
        # Plateformes
        for platform in platforms:
            fenetre.blit(platform.image, camera.apply(platform.rect)) # Appliquer le décalage de rendu pour le screen shake

        # Plateformes spéciales (boue, sable mouvant, eau)
        for sp in special_platforms:
            fenetre.blit(sp.image, camera.apply(sp.rect)) # Appliquer le décalage de rendu pour le screen shake

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

        # Pièges
        for trap in traps:
            fenetre.blit(trap.image, camera.apply(trap.rect)) 
            pygame.draw.rect(fenetre, (0, 255, 255), camera.apply(trap.rect), 2)

        # Boss
        golem.update(player.rect, player)
        if golem.shake > 0:
            shake_amount = golem.shake
            golem.shake = 0
        golem.draw(fenetre, camera) # A modifier : Dans golem.py dans la fonction draw pour afficher les hitbox ou non
        if player.is_attacking and player.attack_rect.colliderect(golem.hitbox):
            if golem not in player.entite_touches: # Vérifier que cet ennemi n'a pas déjà été touché par cette attaque
                player.entite_touches.append(golem)
                golem.knockback(player.rect, player)
                shake_amount = randint(8, 10) # addictif sah

                if player.sang < player.sang_max:
                    player.sang += 11 # charge la jauge de sang 
                else :
                    player.sang = player.sang_max

            if golem.hitbox.colliderect(player.rect):
                hitstop_duration, shake_amount = player.take_damage(golem.attack_data, golem.rect, golem) # Recul du joueur
                hitstop_until = pygame.time.get_ticks() + hitstop_duration
        for tir in projectiles:
            if tir.rect.colliderect(golem.hitbox):
                if not tir.hit:
                    tir.hit = True
                    golem.knockback(player.rect, player)
                    shake_amount = randint(8, 10) # addictif sah
    
        # Joueur
        image_rect = player.image.get_rect(midbottom=(
            player.rect.midbottom[0],
            player.rect.midbottom[1] + player.sprite_offset_y  # offset
        ))
        if not player.invincible or (pygame.time.get_ticks() // 100) % 2 == 0: # Pour faire clignoter le joueur quand il est invincible
            fenetre.blit(player.image, camera.apply(image_rect))

        """
        if player.is_attacking:
            pygame.draw.rect(fenetre, (255, 0, 0), camera.apply(player.attack_rect)) # Afficher la hitbox de l'attaque pour les tests
        """


        # Ennemis
        for elem in liste_ennemis:
            fenetre.blit(elem.image, camera.apply(elem.rect)) # Shake
        
        # --- GESTION DU GRAVELION ---
        if gravelion.alive:
            # 1. Mise à jour et affichage
            gravelion.update(player.rect, player)
            gravelion.draw(fenetre, camera)

            # 2. Le joueur tape le Gravelion
            if player.is_attacking and player.attack_rect.colliderect(gravelion.hitbox):
                if gravelion not in player.entite_touches:
                    player.entite_touches.append(gravelion)
                    # On utilise receive_hit (ta méthode de boss) plutôt que knockback
                    gravelion.receive_hit(player.attack_data, player.rect, player) 
                    
                    # Feedback visuel et sang (identique à tes autres ennemis)
                    if player.sang < player.sang_max:
                        player.sang += 11
                    else:
                        player.sang = player.sang_max
                    
                    for _ in range(15):
                        particles.append(Particle(gravelion.rect.centerx, gravelion.rect.centery))
                    
                    hitstop_until = now + 50
                    shake_amount = 4
            for tir in projectiles:
                if tir.rect.colliderect(gravelion.hitbox):
                    if not tir.hit:
                        tir.hit = True
                        gravelion.receive_hit(tir.attack_data, tir.rect, player)
                        for _ in range(15):
                            particles.append(Particle(gravelion.rect.centerx, gravelion.rect.centery))

            # 3. Le boss touche le joueur avec son corps
            if gravelion.hitbox.colliderect(player.rect):
                hitstop_duration, shake_amount = player.take_damage(gravelion.attack_data, gravelion.rect, gravelion)
                hitstop_until = pygame.time.get_ticks() + hitstop_duration

            # 4. Les attaques/projectiles du boss touchent le joueur
            # On parcourt la liste des hitboxs générées par le boss (bras, ondes, laser...)
            for attaque in gravelion.hitboxs:
                # Si l'attaque a un rect et touche le joueur
                if hasattr(attaque, 'rect') and attaque.rect.colliderect(player.rect):
                    # On passe les dégâts spécifiques de l'attaque
                    hitstop_duration, shake_amount = player.take_damage(attaque.attack_data, attaque.rect, gravelion)
                    hitstop_until = pygame.time.get_ticks() + hitstop_duration

        if not gravelion.combat_lance and player.rect.colliderect(trigger_combat):
            gravelion.combat_lance = True
            platforms.append(porte_arene) # Fermer l'arène en ajoutant le mur gauche
            gravelion.enter_state(gravelion.IDLE)
            shake_amount = 10 # Gros screen shake pour annoncer le début du combat

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

        # Afficher les orbs
        monnaie.draw(fenetre)

        # Afficher la jauge de sang
        font = pygame.font.Font(None, 50)
        barre_sang = font.render(str(player.sang), True, (255, 0, 0))
        fenetre.blit(barre_sang, (10, 40))

        for elem in projectiles:
            elem.update()
            elem.draw(fenetre, camera)
         # supprimer si trop vieux ou hors map
            if elem.lifetime_expired() or elem.out_of_bounds(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)):
                projectiles.remove(elem)
        
        for elem in tir_tourelle:# On parcourt la liste des projectiles tirés par les tourelles
            elem.update()
            elem.draw(fenetre, camera)
            if elem.rect.colliderect(player.rect) and not elem.hit:# Si un projectile de tourelle touche le joueur
                elem.hit = True # Pour éviter que le même projectile touche plusieurs fois
                hitstop_duration, shake_amount = player.take_damage(elem.attack_data, elem.rect, elem)# Appliquer les dégâts et le recul au joueur
                hitstop_until = pygame.time.get_ticks() + hitstop_duration # Activer le hitstop
         # supprimer si trop vieux ou hors map
            if elem.lifetime_expired() or elem.out_of_bounds(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)):
                tir_tourelle.remove(elem)
            
    # Gestion de mort
    else:
        death_sound.play()
        debut_mort = pygame.time.get_ticks()
        duree_mort = 6000

        you_died = pygame.image.load("Assets/Images/YOU_DIED_text.png").convert_alpha()
        w_base, h_base = you_died.get_width(), you_died.get_height()

        while pygame.time.get_ticks() - debut_mort < duree_mort:
            temps = pygame.time.get_ticks() - debut_mort

            # Rouge qui monte
            rouge = int((temps / duree_mort) * 40)
            voile_rouge = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            voile_rouge.fill((15, 0, 0, rouge))
            fenetre.blit(voile_rouge, (0, 0))

            # "YOU DIED" s'affiche (opacité = 0) à partir de 1200ms
            if temps >= 1200:
                avancement = (temps - 2000) / (duree_mort - 2000)  # de 0 à 1

                opacite = int(avancement * 255)
                taille = 1.0 + avancement * 0.15
                new_w = int(w_base * taille)
                new_h = int(h_base * taille)

                img = pygame.transform.scale(you_died, (new_w, new_h))
                img.set_alpha(opacite)

                pos = img.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2)) # centrer le txt
                fenetre.blit(img, pos)

            pygame.display.update()
            clock.tick(60)

        reset(player, liste_ennemis, hearts, spawn_point)

# Mettre à jour l'affichage
    if not pause:
        pygame.display.update()
        clock.tick(60)

pygame.quit()