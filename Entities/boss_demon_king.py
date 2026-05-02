import pygame
import random
from Entities.ennemi import Ennemi
from Entities.boss_logic import Boss
from Visual.sprite_sheet import Animation

class Demon_King(Boss):

    #Indices points de téléportation
    SOL_GAUCHE = 0
    SOL_MILIEU = 1
    SOL_DROIT = 2

    #Noms des attaques :
    ATK_CLEAVE       = "cleave"
    ATK_SMASH        = "smash"
    ATK_FIRE_BREATH  = "fire_breath"
    ATK_CAST_SPELL   = "cast_spell"

    #Etats spécifiques à ce boss
    TRANSFORMING = "TRANSFORMING"
    DISAPPEARING = "DISAPPEARING"
    REAPPEARING = "REAPPEARING"

    def __init__(self, fenetre,x, y, arene_rect):
        marge_x = 150
        tp_points = [
            (arene_rect.left + marge_x, arene_rect.bottom),
            (arene_rect.right - marge_x, arene_rect.bottom),
            (arene_rect.centerx, arene_rect.bottom)
        ]
        super().__init__(fenetre, x, y, "Assets/Boss/Demon_King/slime_idle.png", 6, 64, 64, 0, 0, 100, 1.5,\
                        {"damage": 1, "knockback_x": 60, "knockback_y": -5}, tp_points, stagger_threshold=9999, scale=1)

        self.arene_rect = arene_rect
        self.use_gravity = True # Gravité pour ce boss
        self.transformed = False

        self.pv_demon = 500
        self.pv_demon_max = 500
        self.phase_en_attente = None

        self.intensity = 255 # Pour les effets de fade lors des transitions de phase
        self.smash_jumped = False # Pour gérer le saut de l'attaque Smash

        self.slime_hitbox = pygame.Rect(0, 0, 40, 40) # Hitbox spécifique pour la forme slime
        self.hitbox = pygame.Rect(0, 0, 130, 160) # Hitbox pour la forme roi démon

        self.lava_zones = []

        # Animations 
        self.anims = {
            #animations slime
            "idle":               Animation(fenetre, x, y, "Assets/Boss/Demon_King/slime_idle.png", 6, 64, 64, 0, 0, 1),
            "move":               Animation(fenetre, x, y, "Assets/Boss/Demon_King/slime_move.png", 8, 128, 64, 0, 0, 1),
            "transform":          Animation(fenetre, x, y, "Assets/Boss/Demon_King/demon_king_transform.png", 32, 256, 253, 0, 0, 1),
            #Animations roi démon
            "demon_idle":         Animation(fenetre, x, y, "Assets/Boss/Demon_King/demon_king_general.png", 6, 288, 160, 0, 0, 1),
            "demon_walk":         Animation(fenetre, x, y, "Assets/Boss/Demon_King/demon_king_general.png", 12, 288, 160, 0, 0, 1),
            "demon_cleave":       Animation(fenetre, x, y, "Assets/Boss/Demon_King/demon_king_general.png", 15, 288, 160, 0, 0, 1),
            "demon_smash":        Animation(fenetre, x, y, "Assets/Boss/Demon_King/demon_king_smash.png", 18, 448, 292, 0, 6, 1),
            #"demon_fire_breath":  Animation(fenetre, x, y, "Assets/Boss/Demon_King/demon_king_fire_breath.png", 21, 1000, 100, 0, 7, 1),
            #"demon_cast_spell":   Animation(fenetre, x, y, "Assets/Boss/Demon_King/demon_king_cast_spell.png", 6, 100, 100, 0, 3, 1),
            "death":        Animation(fenetre, x, y, "Assets/Boss/Demon_King/demon_king_general.png", 22, 288, 160, 0, 0, 1),
            
        }   
        
        v=60
        speeds = {
            "idle": 6 / v / 2,
            "move": 8 / v,
            "transform": 32 / v / 2,
            "demon_idle": 8 / v,
            "demon_walk": 12 / v,
            "demon_cleave": 15 / v * 1.5,
            "demon_smash": 18 / v * 1.5,
            #"demon_fire_breath": 7 / v * 1.5,
            #"demon_cast_spell": 6 / v,
            "death": 22 / v / 2
        }

        for state, speed in speeds.items():
            self.anims[state].vitesse_animation = speed
        
        self.sprite_offset = {
            # Slime  — sprite 64x64, hitbox 40x40
            "idle":         (-12, -12),
            "move":         (-44, -12),
            "transform":    (-108, -106),

            # Démon général — sprite 288x160, hitbox 130x160
            "demon_idle":   (-79, 0),
            "demon_walk":   (-79, 0),
            "demon_cleave": (-79, 0),
            "death":        (-79, 0),

            # Smash — sprite 488x292, hitbox 130x160
            "demon_smash":  (-179, -66),
        }

        self.current_anim = "idle"
        self.image = self.anims["idle"].frames_droite[0]
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.enter_state(self.NOT_TRIGGERED)

        #Override de speed() et receive_hit pour le boss final ayant 3 et non 2 phases
        def speed(self, valeur, is_proj=False): 
        # Augmente la vitesse de déplacement et d'animation en fonction de la phase
            if self.phase == 1:
                return valeur
            if self.phase == 2:
                return valeur * 1.5 if is_proj else valeur / 1.2
            return valeur * 1.8 if is_proj else valeur / 1.4
        
        def receive_hit(self, attack_data, source_rect, source):
            if not self.alive:
                return
                
            if self.state in (self.TRANSFORMING, self.DISAPPEARING, self.REAPPEARING, self.DYING):
                return
            
            if not self.transformed: #Forme slime
                Ennemi().receive_hit(attack_data, source_rect, source)
                if self.pv_ennemi == 0:
                    self.alive = True #Pour override le false de Ennemi.receive_hit()
                    self.enter_state(self.TRANSFORMING)
            else : #Forme roi démon
                self.pv_demon -= attack_data["damage"] #Pas usage de la méthode de Ennemi car pas de recul sur ce boss et il ne doit pas mourir au contact de lave

                # Changement de phase
                if self.pv_demon <= self.pv_demon_max // 3 and self.phase == 2:
                    self.phase_en_attente = 3
                    self.enter_state(self.DISAPPEARING)
                elif self.pv_demon <= self.pv_demon_max * 2 // 3 and self.phase == 1:
                    self.phase_en_attente = 2
                    self.enter_state(self.DISAPPEARING)
                elif self.pv_demon <= 0 and self.state != self.DYING:
                    self.enter_state(self.DYING)

    #Attaques
    def choose_attack(self, player_rect):
        distance = abs(player_rect.centerx - self.rect.centerx)
        
        if self.phase == 1:
            if distance <= 200:
                return self.ATK_CLEAVE
            else :
                return random.choices(self.ATK_CLEAVE, self.ATK_SMASH)
        else : #Phase 2 et 3
            return random.choices(self.ATK_CLEAVE, self.ATK_SMASH, self.ATK_FIRE_BREATH, self.ATK_CAST_SPELL)

    #Update général
    def update(self, player_rect, platforms):
        now = pygame.time.get_ticks()
        elapsed = now - self.state_timer

        if not self.transformed:
            self.update_slime(player_rect, platforms)
        else :
            self.update_demon(elapsed, player_rect, platforms)

        self.update_hitbox(platforms, self.arene_rect)
                
        once_states = ["transform", "demon_cleave", "demon_smash", "demon_fire_breath", "demon_death"]
        self.update_anim(self.current_anim in once_states)


    #Update slime
    def update_slime(self, player_rect, platforms):
        if self.state == self.NOT_TRIGGERED:
            if self.dans_trigger(player_rect, 500):
                self.combat_lance = True
                self.enter_state(self.IDLE)
            
        elif self.state == self.IDLE:
            self.current_anim = "move"
            self.face_player(player_rect)
            self.velocity.x = self.speed(self.vitesse_deplacement * self.direction)
        
        elif self.state == self.TRANSFORMING:
            self.current_anim = "transform"
            self.velocity.x = 0
            self.physics_update(platforms)
            if self.anim_over():
                self.transformed = True
                self.current_anim = "demon_idle"
                self.enter_state(self.IDLE)

        self.physics_update(platforms)

    def update_demon(self, elapsed, player_rect, platforms):
        if self.state == self.IDLE:
            self.update_idle(elapsed, player_rect)

        elif self.state == self.ATTACKING:
            self.update_attack(elapsed, player_rect, platforms)

        elif self.state == self.DISAPPEARING:
            self.update_disappearing(elapsed, player_rect)

        elif self.state == self.REAPPEARING:
            self.update_reappearing(elapsed, player_rect)

        elif self.state == self.DYING:
            self.update_dying(elapsed)

        if self.state != self.DYING:
            self.physics_update(platforms)

        # ETATS

    def update_idle(self, elapsed, player_rect):
        self.current_anim ="demon_walk"
        self.face_player(player_rect)
        distance = abs(self.rect.centerx - player_rect.centerx)

        self.velocity.x = self.speed(self.vitesse_deplacement * self.direction)
        idle_max = self.speed(2000)
        if distance <= 150 or elapsed >= idle_max:
            self.face_player(player_rect)
            self.current_attack = self.choose_attack(player_rect)
            self.enter_state(self.ATTACKING)

    def update_attack(self, elapsed, player_rect):
        if self.current_attack == self.ATK_CLEAVE:
            self.attack_cleave(elapsed)
        elif self.current_attack == self.ATK_SMASH:
            self.attack_smash(elapsed, player_rect)
        elif self.current_attack == self.ATK_FIRE_BREATH:
            self.attack_fire_breath(elapsed, player_rect)
        elif self.current_attack == self.ATK_CAST_SPELL:
            self.attack_cast_spell(elapsed, player_rect)

    #transitions avec Fade
    def update_disappearing(self, elapsed, player_rect, player):
        self.current_anim = "demon_idle"
        self.velocity.x = 0

        progression = int((elapsed / 800) * 255)
        self.intensity = max(0, 255 - progression)

        if elapsed > 800:
            self.intensity = 0
            self.appliquer_phase(self.phase_en_ettente)
            self.enter_state(self.REAPPEARING)
    
    def update_reappearing(self, elapsed, player_rect, player):
        self.current_anim = "demon_idle"
        self.velocity.x = 0

        progression = int((elapsed / 800) * 255)
        self.intensity = min(255, progression)

        if elapsed > 800:
            self.intensity = 255
            self.face_player(player_rect)
            self.enter_state(self.IDLE)
    
    def appliquer_phase(self, nouvelle_phase):
        self.phase = nouvelle_phase
        self.teleport_random()
        self.current_tp_index = 0 # Permet à teleport_random de choisir n'importe quel point, y compris celui actuel
        
        if nouvelle_phase == 2:
            self.scale_all_anims_speed(1.2)
        elif nouvelle_phase == 3:
            self.scale_all_anims_speed(1.15)
            #Plus ajouter lave si possible

    #attaques
    def attack_cleave(self, elapsed):
        self.current_anim = "demon_cleave"
        charge = self.speed(350)

        if elapsed < charge: #Avance avant le coup
            self.velocity.x = self.vitesse_deplacement / 2 * self.direction

        elif not self.atk_spawned:
            self.velocity.x = 0
            self.spawn_attack_zone(
                x=self.rect.centerx + 30 * self.direction,
                y=self.rect.bottom - 30,
                width=100,
                height=100,
                attack_data={"damage": 2, "knockback_x": 150, "knockback_y": -10},
                image=None,
                duration=300
            )
            self.atk_spawned = True
        
        #Double cleave pour la phase 3 ???

    def attack_smash(self, elapsed, player_rect):
        self.current_anim = "demon_smash"
        charge = self.speed(400)

        if elapsed >= charge and not self.smash_jumped and not self.atk_spawned:
            self.target = player_rect.centerx
            self.velocity.y = -20
            dx = self.target - self.rect.centerx
            self.velocity.x = dx * 0.05
            self.smash_jumped = True

        if self.smash_jumped and self.on_ground and not self.atk_spawned:
            self.velocity.x = 0
            self.spawn_attack_zone( #A remplacer avec Circular Zone
                x=self.rect.centerx - 100,
                y=self.rect.bottom - 20,
                width=200,
                height=50,
                attack_data={"damage": 2, "knockback_x": 110, "knockback_y": -10},
                image=None,
                duration=300
            )
            if self.phase == 3: #Onde de choc pour phase 3
                for direction in (-1, 1):
                    self.spawn_projectile(
                        target_x=self.rect.centerx + direction * 2000,
                        target_y=self.rect.bottom - 20,
                        width=60,
                        height=30,
                        speed=10,
                        damage=1,
                        offset_x=30 * self.direction,
                        offset_y=0
                    )
            self.atk_spawned = True
            
        if elapsed >= self.speed(1500):
            self.smash_jumped = False
            self.enter_state(self.IDLE)

    def attack_fire_breath(self, elapsed, player_rect):
        pass

    def attack_cast_spell(self, elapsed, player_rect):
        pass

    def draw(self, fenetre, camera): #Override de la méthode de Boss
        if not self.alive:
            return
        
        #Gestion des hitboxs, variant car les dimensions des sprites ne sont pas homogènes
        actual_hitbox = self.hitbox if self.transformed else self.slime_hitbox
        actual_hitbox.midbottom = self.rect.midbottom

        dx, dy = self.sprite_offset[self.current_anim]
        sprite_rect = self.image.get_rect(topleft=(self.rect.left + dx, self.rect.top + dy))

        #Gestion du fade lors des transitions de phase
        image = self.image.copy()
        image.set_alpha(self.intensity)
        fenetre.blit(image, camera.apply(self.rect))

        for elem in self.hitboxs:
            elem.draw(fenetre, camera)
            pygame.draw.rect(fenetre, (255, 0, 0), camera.apply(elem.rect), 2)

        pygame.draw.rect(fenetre, (0, 255, 0), camera.apply(sprite_rect), 2)
        pygame.draw.rect(fenetre, (0, 0, 255), camera.apply(actual_hitbox), 2)
                