import pygame
import os
import sys
from random import randint
# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from Entities.perso import Player
from Entities.ennemi import Projectile
from World.map import Map_Manager
from Visual.camera import Camera, background_luciole, intro, Background_effect, create_parallax_layers, draw_parallax
from Visual.vfx import particles, Particle, Fade, HealParticle, heal_particles
from World.traps import *
from World.objets import Coeur, Monnaie, Receptacle
from Entities.boss_gravelion import Gravelion
from Core.save import *
from Visual.interface import menu, sit_on_bench, home_screen
from Core.reset import reset

new_game = save_backup()

os.environ['SDL_RENDER_SCALE_QUALITY'] = '0'
pygame.init()

info_ecran = pygame.display.Info()

# Configs
GAME_WIDTH, GAME_HEIGHT = 1920, 1080
fenetre = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pygame.FULLSCREEN | pygame.DOUBLEBUF, vsync=1) 
pygame.display.set_caption("Shadow Legacy") # Définir le titre de la fenêtre

zoom = 1.5 # zoom
game_fenetre = pygame.Surface((GAME_WIDTH//zoom, GAME_HEIGHT//zoom))

Chemin_absolu = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

home_screen(fenetre)

#Map
MAP_PATH_TO_NAME = {v: k for k, v in MAP_PATHS.items()} # ça permet d'inverser le dico en gardant clé:valeur
current_map_name, current_map_path = get_saved_map()  # recupère la map actuelle depuis la save
map_manager = Map_Manager()
map_manager.load_map(os.path.join(Chemin_absolu, "Graphics", current_map_name, current_map_path)) # charge la map actuelle
layers = create_parallax_layers(os.path.join(Chemin_absolu, "Graphics", current_map_name), nb_layers=map_manager.nb_parallax_layers, fenetre=game_fenetre) # créer les layers de parallax pour la map actuelle

MAP_WIDTH, MAP_HEIGHT = map_manager.map_width, map_manager.map_height
MAP_RECT = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)

camera = Camera(GAME_WIDTH, GAME_HEIGHT, MAP_WIDTH, MAP_HEIGHT, zoom=zoom)
clock = pygame.time.Clock()

platforms = map_manager.platforms
special_platforms = map_manager.special_platforms
traps = map_manager.traps
decorations = map_manager.decorations 
objects = map_manager.objets
checkpoints = map_manager.checkpoints
spawnpoints = map_manager.spawnpoints
doors = map_manager.doors
entities_to_spawn = map_manager.entities_to_spawn

special_surfaces = [sp.surface for sp in special_platforms if sp.surface is not None]

liste_entites = map_manager.spawn_entities(fenetre)

#Joueur
player = Player(100, 100, fenetre)
spawn_point = charger(player, checkpoints, current_map_name)  # charge la save si elle existe, sinon spawn par défaut
player.position = pygame.math.Vector2(spawn_point.x, spawn_point.y)  # position du joueur maj à partir du spawn point
player.rect.midbottom = player.position # pareil avec la hitbox

#Boss


# UI
ui_reposer = pygame.image.load("Assets/Images/UI_'Pressez_Z'.png").convert_alpha()
ui_reposer = pygame.transform.scale(ui_reposer, (ui_reposer.get_width() /7, ui_reposer.get_height() / 7))

# Sons
set_spawn_sound = pygame.mixer.Sound("Assets/Sounds/set_spawn_sound.mp3")
set_spawn_sound.set_volume(0.5)
death_sound = pygame.mixer.Sound("Assets/Sounds/elden-ring-death.mp3")
death_sound.set_volume(0.7)

#Attributs
hearts = [Coeur(fenetre, 100 + i*110, 35) for i in range(player.max_health)]
monnaie = Monnaie(fenetre, 200, 200)
fade = Fade(GAME_WIDTH, GAME_HEIGHT)
door_collided = None
wait = False

# Liste des projectiles
projectiles = []
tir_tourelle = []

# Variables pour le screen shake et le hitstop à initialiser
hitstop_until = -1 # Temps jusqu'auquel le hitstop est actif (initialisé à une valeur passée)
shake_amount = 0 # Intensité du screen shake

#Loop
continuer = True
pause = False

while continuer:
    now = pygame.time.get_ticks()

    if new_game:
        intro(game_fenetre, fenetre)
        new_game = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            continuer = False
            
        if now > hitstop_until and player.health > 0: # On traite les touches que si on n'est pas en histstop et en vie
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # faire sauter le joueurddd
                    player.press_jump()
                if event.key == pygame.K_LSHIFT:
                    # faire dasher le joueur
                    player.press_dash()
                if event.key == pygame.K_ESCAPE:
                    etat_menu = menu(fenetre, player, checkpoints, current_map_name)
                    if etat_menu == "QUIT":
                        home_screen(fenetre) # quitte le jeu pour aller au menu home
                        pause = False
                    else:
                        pause = etat_menu # Si c'est False, le jeu reprend

                if event.key == pygame.K_f:
                    # faire lancer le sort
                    player.sort.use(player, projectiles)
            
                if event.key == pygame.K_o:
                    player.soin.use(player)

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
        
        # Mise à jour du soin
        player.soin.update(player)

        if now > hitstop_until :
            #Reset effets
            player.current_slow_factor = 1
            player.current_jump_factor = 1
            player.wind_force_x = 0
            player.wind_force_y = 0
            player.in_quicksand = False
            player.on_ice = False

            # Plateformes spéciales
            for sp in special_platforms:

                if sp.rect.colliderect(player.rect):

                    if sp.effect == "mud":
                        player.current_slow_factor = sp.slow_factor
                        player.current_jump_factor = sp.jump_factor
                    
                    elif sp.effect == "quicksand":
                        player.in_quicksand = True

                    elif sp.effect == "ice":
                        player.on_ice = True

            #update joueur
            player.update(platforms + special_surfaces)# Mettre à jour le joueur avec les plateformes pour gérer les collisions
            camera.update(player, shake_amount) # Mettre à jour la caméra pour suivre le joueur

            for e in liste_entites[:]:

                if hasattr(e, "update"):
                    e.update(player.rect, player, platforms)

                if not e.alive:
                    fin = e.mort()
                    if fin:
                        liste_entites.remove(e)
                    continue

                              
                if hasattr(e, "patrouille"): #pour les patrouilleurs
                    e.patrouille(platforms)
                
                if hasattr(e, "poursuite"): #pour les volants
                    e.poursuite(player.rect, platforms)

                if hasattr(e, "mouvement"): #pour les fighters
                    e.mouvement(player.rect, player, platforms)
                
                if hasattr(e, "tir"): #pour les tourelles
                    e.tir(player.rect, tir_tourelle)

                if hasattr(e, "charge"): #pour les chargeurs
                    e.charge(player.rect, platforms)

                if hasattr(e, "update"):
                    e.update(player.rect, player, platforms) 

                if e.rect.colliderect(player.rect):
                    hitstop_duration, shake_amount = player.take_damage(e.attack_data, e.rect, e) # Appliquer les effets de recul au joueur si un ennemi le touche
                    hitstop_until = now + hitstop_duration

                if hasattr(e, "hitboxs"):
                    for atk in e.hitboxs:
                        if hasattr(atk, "rect") and atk.rect.colliderect(player.rect):
                            hitstop_duration, shake_amount = player.take_damage(atk.attack_data, atk.rect, e) 
                            hitstop_until = now + hitstop_duration

            #Sort sur entités
            for tir in projectiles:
                for e in liste_entites:
                    if tir.rect.colliderect(e.rect) and e.alive and e not in player.tir_touches:
                        player.tir_touches.append(e)  
                        e.receive_hit(tir.attack_data, tir.rect, player)
                        for _ in range(15):
                            particles.append(Particle(e.rect.centerx, e.rect.centery))

            #Joueur attaque
            for e in liste_entites:
                if player.is_attacking and player.attack_rect.colliderect(e.rect) and e.alive:
                    if e not in player.entite_touches : # Vérifier que cet ennemi n'a pas déjà été touché par cette attaque
                        player.entite_touches.append(e)

                        if player.attack_data["critical"] : # Si coup critique
                            player.attack_data["damage"] = player.attack * 3
                        else:
                            player.attack_data["damage"] = player.attack
                        
                        e.receive_hit(player.attack_data, player.rect, player) # Appliquer les effets de recul à l'ennemi 
                        
                        player.sang = min(player.sang_max, player.sang + 11)
                        player.attack_feedback(e)
                    
                        hitstop_until = now + 50 # Activer le hitstop pendant 50ms
                        shake_amount = 4 # Définir l'intensité du screen shake 

                        for _ in range(15): # 15 étincelles par coup
                            particles.append(Particle(e.rect.centerx, e.rect.centery))

            # Dessiner les éléments du jeu sur la fenêtre
            offset_x = -camera.camera.x
            offset_y = -camera.camera.y
            
            if current_map_name == "Parcours.tmx":
                background_luciole(game_fenetre, offset_x, offset_y, now) # Remplir le fond 

            # Backgroud avec parallax
            else:
                draw_parallax(game_fenetre, camera, layers)
                
            # Plateformes
            for platform in platforms:
                game_fenetre.blit(platform.image, camera.apply(platform.rect)) # Appliquer le décalage de rendu pour le screen shake

            # Plateformes spéciales (boue, sable mouvant, eau)
            for sp in special_platforms:
                game_fenetre.blit(sp.image, camera.apply(sp.rect))

            # Pieges
            for trap in traps:
                trap.update()
                game_fenetre.blit(trap.image, camera.apply(trap.image_rect))
                if pygame.key.get_pressed()[pygame.K_a]:
                    pygame.draw.rect(game_fenetre, (0, 255, 0), camera.apply(trap.rect), 2)

                if player.is_attacking and player.attack_rect.colliderect(trap.rect):
                    if trap not in player.entite_touches: # Vérifier que ce piège n'a pas déjà été touché par cette attaque
                        player.entite_touches.append(trap) # Ajouter le piège à la liste d'entités déjà touchées
                        player.attack_feedback(trap)

                if trap.rect.colliderect(player.rect): #trap touche joueur
                    if trap.attack_data["damage"] > 0:
                        if trap.damage_cooldown == 0 or now - trap.last_damage_time >= trap.damage_cooldown :
                            hitstop_duration, shake_amount = player.take_damage(trap.attack_data, trap.rect, trap, fade)
                            hitstop_until = now + hitstop_duration
                            trap.last_damage_time = now

                    if trap.special_effect == "wind":
                        player.wind_force_x = trap.force_x
                        player.wind_force_y = trap.force_y

                for e in liste_entites:
                    if trap.rect.colliderect(e.rect) and hasattr(e, "receive_hit") : #trap touche ennemi
                        e.receive_hit(trap.attack_data, trap.rect, trap)

            if shake_amount > 0:
                shake_amount -= 1 # Réduire progressivement l'intensité du screen shake

            for deco in decorations:
                game_fenetre.blit(deco.image, camera.apply(deco.rect))

            for obj in objects[:]:
                obj.update(player, objects)# Mettre à jour les réceptacles
                if not obj.taken:# Afficher les objets qui n'ont pas été pris
                    game_fenetre.blit(obj.image, camera.apply(obj.rect))
                obj.draw_big(game_fenetre, player)# Afficher les objets pris en grand pour indiquer qu'ils ont été ramassés

        # Checkpoints
        for i, cp in enumerate(checkpoints):
            # On calcule la position a l'écran
            cp_screen_rect = camera.apply(cp.rect)
            game_fenetre.blit(cp.image, cp_screen_rect)

            # Quand le joueur est proche du banc
            if cp.rect.colliderect(player.rect):
                
                # Si le joueur est debout, on affiche l'UI pour s'asseoir
                if not player.is_sitting:
                    # UI (centrage)
                    ui_x = cp_screen_rect.centerx - (ui_reposer.get_width() // 2)
                    ui_y = cp_screen_rect.top - ui_reposer.get_height() + 135
                    game_fenetre.blit(ui_reposer, (ui_x, ui_y)) 

                    # Au lieu de juste "if 'Z' pressed" qui appuierai 60 fois/s :
                    if pygame.key.get_pressed()[pygame.K_z]:
                        player.is_sitting = True
                        cp.activated = True
                        player.health = player.max_health
                        spawn_point = pygame.math.Vector2(cp.rect.topleft)
                        sauvegarder(player, checkpoints, current_map_name, index_last_checkpoint=i)
                        set_spawn_sound.play()
                
                # Si le joueur est déjà assis, on permet d'ouvrir l'inventaire avec E
                else:
                    if pygame.key.get_pressed()[pygame.K_e]:
                        sit_on_bench(fenetre)

        # Portes
        for door in doors:
            if pygame.key.get_pressed()[pygame.K_a]:
                pygame.draw.rect(game_fenetre, (255, 0, 255), camera.apply(door.rect))

            if player.rect.colliderect(door.rect) and fade.state is None:
                door_collided = door
                player.stun_timer = pygame.time.get_ticks()
                player.stun_duration = 1000
                fade.start("out", 5)

        if door_collided and fade.intensity >= 255 and fade.state == "out":
                print("doored")
                liste_entites.clear()
                projectiles.clear()
                tir_tourelle.clear()

                current_map_path = door_collided.target_map
                current_map_name = TMX_TO_FOLDER.get(os.path.basename(current_map_path))
                map_manager.load_map(os.path.join(Chemin_absolu, "Graphics", door_collided.target_map))
                spawn = map_manager.get_spawn(door_collided.target_spawn)

                platforms = map_manager.platforms
                special_platforms = map_manager.special_platforms
                special_surfaces = [sp.surface for sp in special_platforms if sp.surface is not None]
                traps = map_manager.traps
                decorations = map_manager.decorations
                checkpoints = map_manager.checkpoints
                spawnpoints = map_manager.spawnpoints
                doors = map_manager.doors
                entities_to_spawn = map_manager.entities_to_spawn

                MAP_WIDTH, MAP_HEIGHT = map_manager.map_width, map_manager.map_height
                MAP_RECT = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
                camera.update_map_size(MAP_WIDTH, MAP_HEIGHT)
                layers = create_parallax_layers(os.path.join(Chemin_absolu, "Graphics", current_map_name), nb_layers=map_manager.nb_parallax_layers, fenetre=game_fenetre) # créer les layers de parallax pour la map actuelle

                liste_entites = map_manager.spawn_entities(fenetre)
                spawn = map_manager.get_spawn(door_collided.target_spawn)

                player.position = spawn.position
                player.rect.midbottom = player.position
                door_collided = None
                player.on_ground=False
                wait = True

        if wait and player.on_ground:
            wait = False
            fade.start("in", 5)

        # Joueur
        image_rect = player.image.get_rect(midbottom=(
            player.rect.midbottom[0],
            player.rect.midbottom[1] + player.sprite_offset_y  # offset
        ))
        if not player.invincible or (pygame.time.get_ticks() // 100) % 2 == 0: # Pour faire clignoter le joueur quand il est invincible
            game_fenetre.blit(player.image, camera.apply(image_rect))

        if player.is_attacking and pygame.key.get_pressed()[pygame.K_a]:
            pygame.draw.rect(game_fenetre, (255, 0, 0), camera.apply(player.attack_rect)) # Afficher la hitbox de l'attaque pour les tests
        if pygame.key.get_pressed()[pygame.K_a]:
            pygame.draw.rect(game_fenetre, (0, 0, 255), camera.apply(player.rect), 2) # Afficher la hitbox de l'attaque pour les tests
        
        if player.soin.is_healing:
            if (now // 150) % 2 == 0: # Clignotement de l'effet de soin
                heal_effect = pygame.Surface((player.rect.width, player.rect.height), pygame.SRCALPHA)
                heal_effect.fill((255, 255, 255, 100)) # Blanc transparent
                game_fenetre.blit(heal_effect, camera.apply(player.rect))
            if (now // 80) % 2 == 0:
                heal_particles.append(HealParticle(
                    player.rect.centerx + randint(-20, 20),
                    player.rect.bottom - randint(0, 30)
                ))

        
        #Lancement Gravelion
         # Gros screen shake pour annoncer le début du combat

        total_particles = particles + heal_particles  # Liste combinée pour faciliter la mise à jour et le dessin

        # Particules
        for p in total_particles[:]: # On utilise [:] pour copier la liste et éviter les erreurs de suppression
            p.update()
            if p.life <= 0:
                if p in particles:
                    particles.remove(p)
                elif p in heal_particles:
                    heal_particles.remove(p)
            else:
                p.draw(game_fenetre, camera)
        
        # Afficher les cœurs
        for heart in hearts:
            game_fenetre.blit(heart.image, heart.rect) # Les cœurs sont fixes à l'écran, pas besoin d'appliquer le décalage de la caméra
        
        if len(hearts) < player.max_health:
            i = len(hearts)
            hearts.append(Coeur(fenetre, 100 + i*110, 35))

        for e in liste_entites:
            if pygame.key.get_pressed()[pygame.K_a]:
                pygame.draw.rect(game_fenetre, (255, 255, 0), camera.apply(e.rect), 2)

            if hasattr(e, "draw"):
                e.draw(game_fenetre, camera)
            else:
                game_fenetre.blit(e.image, camera.apply(e.rect))
        # Afficher les orbs
        monnaie.draw(game_fenetre)

        # Afficher la jauge de sang
        font = pygame.font.Font(None, 50)
        barre_sang = font.render(str(player.sang), True, (255, 0, 0))
        game_fenetre.blit(barre_sang, (10, 40))

        for elem in projectiles[:]:
            delete = elem.update(platforms, MAP_RECT)
            if delete:
                projectiles.remove(elem)
            else:
                elem.draw(game_fenetre, camera)
        
        for elem in tir_tourelle[:]:# On parcourt la liste des projectiles tirés par les tourelles
            delete = elem.update(platforms, MAP_RECT)
            if delete:
                tir_tourelle.remove(elem)
            else :
                elem.draw(game_fenetre, camera)
            if elem.rect.colliderect(player.rect) and not elem.hit:# Si un projectile de tourelle touche le joueur
                elem.hit = True # Pour éviter que le même projectile touche plusieurs fois
                hitstop_duration, shake_amount = player.take_damage(elem.attack_data, elem.rect, elem)# Appliquer les dégâts et le recul au joueur
                hitstop_until = pygame.time.get_ticks() + hitstop_duration # Activer le hitstop

    # Gestion de mort
    else:
        death_sound.play()
        debut_mort = pygame.time.get_ticks()
        duree_mort = 4500

        you_died = pygame.image.load("Assets/Images/YOU_DIED_text.png").convert_alpha()
        w_base, h_base = you_died.get_width(), you_died.get_height()

        while pygame.time.get_ticks() - debut_mort < duree_mort:
            temps = pygame.time.get_ticks() - debut_mort

            # Rouge qui monte
            rouge = int((temps / duree_mort) * 40)
            voile_rouge = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            voile_rouge.fill((15, 0, 0, rouge))
            fenetre.blit(voile_rouge, (0, 0))

            # "YOU DIED" s'affiche (opacité à 0) à partir de 1200ms
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

        reset(player, liste_entites, hearts, spawn_point)

# Mettre à jour l'affichage
    if not pause or not new_game:
        fenetre.blit(pygame.transform.scale(game_fenetre, (GAME_WIDTH, GAME_HEIGHT)), (0, 0))
        fade.update(fenetre)
        pygame.display.update()
    clock.tick(60)
pygame.quit()