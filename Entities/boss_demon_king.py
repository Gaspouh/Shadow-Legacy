import math

import pygame
import random
from Entities.ennemi import Ennemi
from Entities.boss_logic import Boss
from Visual.sprite_sheet import Animation


class Demon_King(Boss):
    # Indices points de téléportation
    SOL_GAUCHE = 0
    SOL_MILIEU = 1
    SOL_DROIT = 2

    # Noms des attaques :
    ATK_CLEAVE = "cleave"
    ATK_SMASH = "smash"
    ATK_FIRE_BREATH = "fire_breath"
    ATK_CAST_SPELL = "cast_spell"

    # Etats spécifiques à ce boss
    TRANSFORMING = "TRANSFORMING"
    DISAPPEARING = "DISAPPEARING"
    REAPPEARING = "REAPPEARING"

    def __init__(self, fenetre, x, y, arene_rect):
        marge_x = 300
        tp_points = [
            (arene_rect.left + marge_x, arene_rect.bottom - 150),
            (arene_rect.right - marge_x, arene_rect.bottom - 150),
            (arene_rect.centerx, arene_rect.bottom),
        ]
        super().__init__(
            fenetre,
            x,
            y,
            "Assets/Boss/Demon_King/slime_idle.png",
            6,
            64,
            64,
            0,
            0,
            80,
            2,
            {"damage": 1, "knockback_x": 60, "knockback_y": -5},
            tp_points,
            stagger_threshold=9999,
            scale=1,
        )

        self.arene_rect = arene_rect
        self.use_gravity = True  # Gravité pour ce boss
        self.sprite_inverted = True
        self.friction = -0.4

        self.pv_demon = 500
        self.pv_demon_max = 500
        self.transformed = False
        self.phase_en_attente = None

        self.intensity = 255  # Pour les effets de fade lors des transitions de phase
        self.smash_jumped = False  # Pour gérer le saut de l'attaque Smash
        self.fire_breath = None  # Pour garder une référence à la hitbox du souffle de feu
        self.last_spell_spawn = 0  # Pour gérer l'intervalle d'apparition des projectiles de l'attaque de sortilège
        self.is_ghost = False

        self.last_sound = -1000
        self.once = True

        # Animations
        self.anims = {
            # animations slime
            "idle": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Demon_King/slime_idle.png",
                6,
                64,
                64,
                0,
                0,
                1,
            ),
            "move": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Demon_King/slime_move.png",
                8,
                64,
                128,
                0,
                0,
                1,
            ),
            "transform": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Demon_King/demon_king_transform.png",
                32,
                256,
                253,
                0,
                0,
                1,
            ),
            # Animations roi démon
            "demon_idle": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Demon_King/demon_king_general.png",
                6,
                288,
                160,
                0,
                0,
                2,
            ),
            "demon_walk": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Demon_King/demon_king_general.png",
                12,
                288,
                160,
                0,
                1,
                2,
            ),
            "demon_cleave": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Demon_King/demon_king_general.png",
                15,
                288,
                160,
                0,
                2,
                2,
            ),
            "demon_smash": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Demon_King/demon_king_smash.png",
                18,
                448,
                292,
                0,
                0,
                1,
            ),
            "demon_fire_breath": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Demon_King/demon_king_fire_breath.png",
                21,
                536,
                313,
                0,
                0,
                1,
            ),
            "demon_cast_spell": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Demon_King/demon_king_cast_spell.png",
                6,
                368,
                252,
                0,
                0,
                1,
            ),
            "death": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Demon_King/demon_king_general.png",
                22,
                288,
                160,
                0,
                4,
                2,
            ),
        }

        v = 60
        speeds = {
            "idle": 6 / v,
            "move": 8 / v,
            "transform": 32 / v / 3,
            "demon_idle": 8 / v,
            "demon_walk": 12 / v / 1.5,
            "demon_cleave": 15 / v,
            "demon_smash": 18 / v / 2,
            "demon_fire_breath": 7 / v,
            "demon_cast_spell": 6 / v,
            "death": v,  # peu importe vu qu'on l'écrase après
        }

        for state, speed in speeds.items():
            self.anims[state].vitesse_animation = speed

        # Sons
        self.slime_sound = pygame.mixer.Sound("Assets\Boss\Demon_King\Sons\slime_3.MP3")
        self.slime_sounds = [
            pygame.mixer.Sound("Assets\Boss\Demon_King\Sons\slime_1.MP3"),
            pygame.mixer.Sound("Assets\Boss\Demon_King\Sons\slime_2.MP3"),
        ]
        self.transformation_sound = pygame.mixer.Sound("Assets\Boss\Demon_King\Sons\_transformation.MP3")
        self.cleave_sounds = [
            pygame.mixer.Sound("Assets\Boss\Demon_King\Sons\epee_1.MP3"),
            pygame.mixer.Sound("Assets\Boss\Demon_King\Sons\epee_2.MP3"),
            pygame.mixer.Sound("Assets\Boss\Demon_King\Sons\epee_3.MP3"),
        ]
        self.smash_sounds = [
            pygame.mixer.Sound("Assets\Boss\Demon_King\Sons\smash_1.MP3"),
            pygame.mixer.Sound("Assets\Boss\Demon_King\Sons\smash_2.MP3"),
        ]
        self.smash_landing_sound = pygame.mixer.Sound("Assets\Boss\Demon_King\Sons\smash_3.MP3")
        self.cast_spell_sound = pygame.mixer.Sound("Assets\Boss\Demon_King\Sons\cast_spell.MP3")
        self.transition_sound = pygame.mixer.Sound("Assets\Boss\Demon_King\Sons\phase_transition.MP3")
        self.death_sound = pygame.mixer.Sound("Assets\Boss\Demon_King\Sons\mort.MP3")

        self.sounds_cooldown = {
            "slime": 0.3,
            "cleave": 0.5,
            "cast_spell": 1.5,
        }

        self.current_anim = "idle"
        self.image = self.anims["idle"].frames_droite[0]
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.enter_state(self.NOT_TRIGGERED)

    def can_play_sound(self, name):
        """Vérifie si un son peut être joué selon le cooldown et le temps écoulé pour éviter les répétitions.
        Entrées: name.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        now = pygame.time.get_ticks()
        if now - self.last_sound > self.sounds_cooldown[name] * 1000:
            self.last_sound = now
            return True
        return False

    # Override de speed() et receive_hit pour le boss final ayant 3 et non 2 phases
    def speed(self, valeur, is_proj=False):
        # Augmente la vitesse de déplacement et d'animation en fonction de la phase
        """Exécute la logique de la fonction speed liée à d'un boss, modifiant l'état ou produisant une action spécifique.
        Entrées: valeur, is_proj.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        if self.phase == 1:
            return valeur
        elif self.phase == 2:
            facteur = 1.25
        else:  # Phase 3
            facteur = 1.5
        if is_proj:
            return valeur * facteur
        else:
            return valeur / facteur

    def receive_hit(self, attack_data, source_rect, source):
        """Gère la réception des dégâts d'un boss en appliquant les effets selon les attributs de la source (dégâts, type, recul, invincibilité, etc.).
        Entrées: attack_data, source_rect, source.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        if not self.alive:
            return

        if source.respawn_on_touch:  # Pour ne pas mourir des piques de l'arene
            return

        if self.state in (
            self.TRANSFORMING,
            self.DISAPPEARING,
            self.REAPPEARING,
            self.DYING,
        ):
            return

        if not self.transformed:  # Forme slime
            self.pv_ennemi -= attack_data["damage"]
            self.velocity.x = attack_data["knockback_x"] * source.direction * 3
            self.velocity.y = attack_data["knockback_y"]
            if self.can_play_sound("slime"):
                self.slime_sound.play()

            if self.pv_ennemi <= 0:
                self.enter_state(self.TRANSFORMING)
                self.transformation_sound.play()

        else:  # Forme roi démon
            self.pv_demon -= attack_data["damage"]
            # Changement de phase
            if self.pv_demon <= self.pv_demon_max // 3 and self.phase == 2:
                self.phase_en_attente = 3
                self.enter_state(self.DISAPPEARING)
            elif self.pv_demon <= self.pv_demon_max * 2 // 3 and self.phase == 1:
                self.phase_en_attente = 2
                self.enter_state(self.DISAPPEARING)
            elif self.pv_demon <= 0 and self.state != self.DYING:
                self.enter_state(self.DYING)

    # Attaques
    def choose_attack(self, player_rect):
        """Exécute la logique de la fonction choose_attack liée à d'un boss, modifiant l'état ou produisant une action spécifique.
        Entrées: player_rect.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        distance = abs(player_rect.centerx - self.rect.centerx)

        if self.phase == 1:
            if distance <= 200:
                return self.ATK_CLEAVE
            else:
                return random.choice([self.ATK_CLEAVE, self.ATK_SMASH, self.ATK_CAST_SPELL])
        else:  # Phase 2 et 3
            return random.choice(
                [
                    self.ATK_CLEAVE,
                    self.ATK_SMASH,
                    self.ATK_CAST_SPELL,
                    self.ATK_FIRE_BREATH,
                ]
            )

    # Update général
    def update(self, player_rect, player, platforms):
        """Met à jour l'état du joueur (position, santé, capacités) en fonction des entrées, des collisions et du temps.
        Entrées: player_rect, player, platforms.
        Sortie: Aucune valeur renvoyée (None).
        """
        now = pygame.time.get_ticks()
        elapsed = now - self.state_timer

        if not self.transformed:
            self.update_slime(player_rect, platforms)
        else:
            self.update_demon(elapsed, player_rect, platforms)

        self.update_hitbox(platforms, self.arene_rect)

        once_states = [
            "transform",
            "demon_cleave",
            "demon_smash",
            "demon_fire_breath",
            "death",
        ]
        self.update_anim(self.current_anim in once_states)

    # Update slime
    def update_slime(self, player_rect, platforms):
        """Met à jour l'état du joueur (position, santé, capacités) en fonction des entrées, des collisions et du temps.
        Entrées: player_rect, platforms.
        Sortie: Aucune valeur renvoyée (None).
        """
        if self.state == self.NOT_TRIGGERED:
            if self.dans_trigger(player_rect, 500):
                self.combat_lance = True
                self.enter_state(self.IDLE)

        elif self.state == self.IDLE:
            self.current_anim = "move"
            self.face_player(player_rect)
            self.velocity.x += self.speed(self.vitesse_deplacement * self.direction)
            if int(self.anims["move"].index_image) == 1 and self.can_play_sound("slime"):
                random.choice(self.slime_sounds).play()

        elif self.state == self.TRANSFORMING:
            self.current_anim = "transform"
            self.velocity.x = 0
            if self.anim_over():
                self.transformed = True
                # Changement de hitbox
                old_midbottom = self.rect.midbottom

                self.rect = pygame.Rect(0, 0, 128, 128)
                self.rect.midbottom = old_midbottom

                self.position.x = self.rect.centerx
                self.position.y = self.rect.bottom
                self.velocity = pygame.math.Vector2(0, 0)

                self.current_anim = "demon_idle"
                self.enter_state(self.IDLE)

        self.physics_update(platforms)

    def update_demon(self, elapsed, player_rect, platforms):
        """Met à jour l'état du joueur (position, santé, capacités) en fonction des entrées, des collisions et du temps.
        Entrées: elapsed, player_rect, platforms.
        Sortie: Aucune valeur renvoyée (None).
        """
        if self.state == self.IDLE:
            self.update_idle(elapsed, player_rect)

        elif self.state == self.ATTACKING:
            self.update_attack(elapsed, player_rect)

        elif self.state == self.DISAPPEARING:
            self.is_ghost = True
            if self.fire_breath is not None:  # Pour eviter un bug de hitbox resté en l'air
                if self.fire_breath in self.hitboxs:
                    self.hitboxs.remove(self.fire_breath)
                self.fire_breath = None
                self.fire_breath_pos = None
            self.update_disappearing(elapsed)

        elif self.state == self.REAPPEARING:
            self.update_reappearing(elapsed, player_rect)

        elif self.state == self.DYING:
            if self.fire_breath is not None:
                if self.fire_breath in self.hitboxs:
                    self.hitboxs.remove(self.fire_breath)
                self.fire_breath = None
                self.fire_breath_pos = None
            self.update_dying(elapsed)

        if self.state != self.DYING:
            self.physics_update(platforms)

        # ETATS

    def update_idle(self, elapsed, player_rect):
        """Met à jour l'état du joueur (position, santé, capacités) en fonction des entrées, des collisions et du temps.
        Entrées: elapsed, player_rect.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.current_anim = "demon_walk"
        self.face_player(player_rect)
        distance = abs(self.rect.centerx - player_rect.centerx)

        self.velocity.x = self.speed(self.vitesse_deplacement * self.direction, True)
        idle_max = self.speed(2000)
        if distance <= 150 or elapsed >= idle_max:
            self.face_player(player_rect)
            self.current_attack = self.choose_attack(player_rect)
            self.enter_state(self.ATTACKING)

    def update_dying(self, elapsed):
        """Met à jour les animations d'un boss, avance les frames et gère les transitions entre animations.
        Entrées: elapsed.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.anims["death"].vitesse_animation = 0.1
        self.current_anim = "death"
        if self.once:
            self.death_sound.play()
            self.once = False
        self.update_anim(once=True)
        if self.anim_over() and elapsed > 500:
            self.alive = False

    def update_attack(self, elapsed, player_rect):
        """Met à jour l'état du joueur (position, santé, capacités) en fonction des entrées, des collisions et du temps.
        Entrées: elapsed, player_rect.
        Sortie: Aucune valeur renvoyée (None).
        """
        if self.current_attack == self.ATK_CLEAVE:
            self.attack_cleave(elapsed)
        elif self.current_attack == self.ATK_SMASH:
            self.attack_smash(elapsed, player_rect)
        elif self.current_attack == self.ATK_FIRE_BREATH:
            self.attack_fire_breath(elapsed)
        elif self.current_attack == self.ATK_CAST_SPELL:
            self.attack_cast_spell(elapsed)

    # transitions avec Fade
    def update_disappearing(self, elapsed):
        """Met à jour les animations d'un boss, avance les frames et gère les transitions entre animations.
        Entrées: elapsed.
        Sortie: Aucune valeur renvoyée (None).
        """
        if self.once:
            self.transition_sound.play()
            self.once = False
        self.current_anim = "demon_idle"
        self.velocity.x = 0

        progression = int((elapsed / 800) * 255)
        self.intensity = max(0, 255 - progression)

        if elapsed > 2500:
            self.intensity = 0
            self.appliquer_phase(self.phase_en_attente)
            self.enter_state(self.REAPPEARING)
            self.once = True

    def update_reappearing(self, elapsed, player_rect):
        """Met à jour l'état du joueur (position, santé, capacités) en fonction des entrées, des collisions et du temps.
        Entrées: elapsed, player_rect.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.current_anim = "demon_idle"
        self.velocity.x = 0

        progression = int((elapsed / 800) * 255)
        self.intensity = min(255, progression)

        if elapsed > 800:
            self.intensity = 255
            self.face_player(player_rect)
            self.is_ghost = False
            self.enter_state(self.IDLE)

    def appliquer_phase(self, nouvelle_phase):
        """Exécute la logique de la fonction appliquer_phase liée à d'un boss, modifiant l'état ou produisant une action spécifique.
        Entrées: nouvelle_phase.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.phase = nouvelle_phase
        self.teleport_random()
        self.current_tp_index = 0  # Permet à teleport_random de choisir n'importe quel point, y compris celui actuel

        if nouvelle_phase == 2:
            self.scale_all_anims_speed(1.25)
        elif nouvelle_phase == 3:
            self.scale_all_anims_speed(1.2)

    # attaques
    def attack_cleave(self, elapsed):
        """Gère la réception des dégâts d'un boss en appliquant les effets selon les attributs de la source (dégâts, type, recul, invincibilité, etc.).
        Entrées: elapsed.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.current_anim = "demon_cleave"
        charge = self.speed(530)

        if elapsed < charge:  # Avance avant le coup
            self.velocity.x = self.speed(self.vitesse_deplacement / 2 * self.direction, True)
            if elapsed > self.speed(220):
                if self.can_play_sound("cleave"):
                    random.choice(self.cleave_sounds).play()

        elif not self.atk_spawned:
            self.velocity.x = 0
            self.spawn_attack_zone(
                x=self.rect.centerx - 30 if self.direction == 1 else self.rect.centerx - 220,
                y=self.rect.bottom - 200,
                width=250,
                height=200,
                attack_data={"damage": 2, "knockback_x": 150, "knockback_y": -10},
                image=None,
                duration=200,
            )
            self.atk_spawned = True

        if elapsed >= charge + self.speed(500):
            self.enter_state(self.IDLE)

    def attack_smash(self, elapsed, player_rect):
        """Gère la réception des dégâts d'un boss en appliquant les effets selon les attributs de la source (dégâts, type, recul, invincibilité, etc.).
        Entrées: elapsed, player_rect.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.current_anim = "demon_smash"
        charge = self.speed(400)
        mid_smash_frame = 9

        if elapsed >= charge and not self.smash_jumped and not self.atk_spawned:
            self.velocity.y = self.speed(-18)
            self.target = player_rect.centerx
            self.smash_jumped = True
            self.has_left_ground = (
                False  # Pour s'assurer que l'attaque ne se déclenche qu'après que le boss ait quitté le sol
            )
            random.choice(self.smash_sounds).play()

        if self.smash_jumped and not self.atk_spawned:
            dx = self.target - self.rect.centerx
            self.smash_vx = dx * self.speed(0.07, True)
            self.velocity.x = self.smash_vx

            if not (self.has_left_ground and self.on_ground):
                self.anims["demon_smash"].index_image = min(self.anims["demon_smash"].index_image, mid_smash_frame)

            if not self.has_left_ground and not self.on_ground:
                self.has_left_ground = True

            if self.has_left_ground and self.on_ground:
                self.smash_landing_sound.play()
                self.velocity.x = 0
                self.spawn_attack_zone(
                    x=self.rect.centerx - 150,
                    y=self.rect.bottom - 70,
                    width=300,
                    height=70,
                    attack_data={"damage": 2, "knockback_x": 110, "knockback_y": -10},
                    image=None,
                    duration=150,
                )
                if self.phase == 3:  # Onde de choc pour phase 3
                    for direction in (-1, 1):
                        self.spawn_projectile(
                            target_x=self.rect.centerx + direction * 2000,
                            target_y=self.rect.bottom - 20,
                            width=70,
                            height=50,
                            speed=7,
                            damage=1,
                            offset_x=30 * self.direction,
                            offset_y=10,
                            image=pygame.image.load("Assets\Boss\Demon_King\shockwave.png").convert_alpha(),
                        )
                self.atk_spawned = True

        if elapsed >= self.speed(3000):
            self.smash_jumped = False
            self.enter_state(self.IDLE)

    def attack_fire_breath(self, elapsed):
        """Gère la réception des dégâts d'un boss en appliquant les effets selon les attributs de la source (dégâts, type, recul, invincibilité, etc.).
        Entrées: elapsed.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.current_anim = "demon_fire_breath"
        charge = self.speed(800)

        if elapsed >= charge:
            if self.fire_breath is None:
                self.fire_breath_pos = pygame.math.Vector2(
                    self.rect.centerx + (30 if self.direction == 1 else -260),
                    self.rect.top - 130,
                )

                self.fire_breath = self.spawn_attack_zone(
                    x=self.fire_breath_pos.x,
                    y=self.fire_breath_pos.y,
                    width=230,
                    height=50,
                    attack_data={"damage": 1, "knockback_x": 80, "knockback_y": -2},
                    image=None,
                    duration=9999,
                )

            move_speed = self.speed(2.1, is_proj=True)
            self.fire_breath_pos.y += move_speed

            self.fire_breath.rect.topleft = (
                self.fire_breath_pos.x,
                self.fire_breath_pos.y,
            )

            if elapsed >= charge + self.speed(1700):
                if self.fire_breath in self.hitboxs:
                    self.hitboxs.remove(self.fire_breath)
                self.fire_breath = None  # Reset variable
                self.fire_breath_pos = None
                self.enter_state(self.IDLE)

    def attack_cast_spell(self, elapsed):
        """Gère la réception des dégâts d'un boss en appliquant les effets selon les attributs de la source (dégâts, type, recul, invincibilité, etc.).
        Entrées: elapsed.
        Sortie: Aucune valeur renvoyée (None).
        """
        charge = self.speed(1000)
        self.current_anim = "demon_cast_spell"
        self.velocity.x = 0
        interval = self.speed(800)
        now = pygame.time.get_ticks()
        if self.can_play_sound("cast_spell") and elapsed <= charge:
            self.cast_spell_sound.play()

        if elapsed >= charge:
            if now - self.last_spell_spawn >= interval:
                self.last_spell_spawn = now

                if self.phase == 1:
                    list_angle = [0]

                elif self.phase == 2:
                    list_angle = [0, 30, -30]

                else:  # Phase 3
                    list_angle = [random.randint(-60, 60) for _ in range(5)]

                offset_y = random.randint(-100, 20)
                for angle in list_angle:
                    radians = math.radians(angle)
                    target_x = self.rect.centerx + math.cos(radians) * 3000 * self.direction
                    target_y = self.rect.centery + math.sin(radians) * 3000
                    self.spawn_projectile(
                        target_x=target_x,
                        target_y=target_y,
                        speed=self.speed(4, is_proj=True),
                        width=30,
                        height=30,
                        damage=1,
                        offset_x=150 * self.direction,
                        offset_y=offset_y,
                        image=pygame.image.load("Assets\Boss\Demon_King\Fireball.png").convert_alpha(),
                    )

            if elapsed >= charge + self.speed(1200):
                self.enter_state(self.IDLE)

    def draw(self, fenetre, camera):  # Override de la méthode de Boss
        """Dessine d'un boss à l'écran en tenant compte de la caméra, de la position et de l'animation.
        Entrées: fenetre, camera.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        if not self.alive:
            return

        sprite_rect = self.image.get_rect(midbottom=(self.rect.centerx, self.rect.bottom))

        # Gestion du fade lors des transitions de phase
        image = self.image.copy()
        image.set_alpha(self.intensity)
        fenetre.blit(image, camera.apply(sprite_rect))

        for elem in self.hitboxs:
            elem.draw(fenetre, camera)
