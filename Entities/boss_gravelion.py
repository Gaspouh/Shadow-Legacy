import pygame
import random
from Entities.boss_logic import Boss
from Visual.sprite_sheet import Animation


class Gravelion(Boss):
    # Indices points de téléportation
    SOL_GAUCHE = 0
    SOL_DROIT = 1
    AIR_GAUCHE = 2
    AIR_DROIT = 3

    # Etats specifiques à ce boss
    TELEPORTING = "TELEPORTING"
    SHIELDED = "SHIELDED"

    # Noms des attaques :
    ATK_MELEE = "melee"
    ATK_ARM = "arm"
    ATK_LASER = "laser"
    ATK_COCON = "cocon"

    def __init__(self, fenetre, x, y, arene_rect):
        marge_x = 300
        hauteur_air = arene_rect.top + 300
        hauteur_sol = arene_rect.bottom - 250

        tp_points = [
            (arene_rect.left + marge_x, hauteur_sol),
            (arene_rect.right - marge_x, hauteur_sol),
            (arene_rect.left + marge_x, hauteur_air),
            (arene_rect.right - marge_x, hauteur_air),
        ]
        self.arene_rect = arene_rect
        super().__init__(
            fenetre,
            x,
            y,
            "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png",
            4,
            400,
            100,
            0,
            0,
            300,
            1,
            {"damage": 1, "knockback_x": 80, "knockback_y": -5},
            tp_points,
            stagger_threshold=80,
            scale=1,
        )

        self.arene_rect = arene_rect
        self.use_gravity = False  # Pas de gravité pour ce boss lévitant

        # Animations
        self.anims = {
            "idle": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png",
                4,
                100,
                100,
                0,
                0,
                1,
            ),
            "glowing": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png",
                8,
                100,
                100,
                0,
                1,
                1,
            ),
            "arm": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png",
                9,
                100,
                100,
                0,
                2,
                1,
            ),
            "cocon": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png",
                8,
                100,
                100,
                0,
                3,
                1,
            ),
            "melee": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png",
                7,
                100,
                100,
                0,
                4,
                1,
            ),
            "laser_charge": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png",
                7,
                100,
                100,
                0,
                5,
                1,
            ),
            "transition": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png",
                10,
                100,
                100,
                0,
                6,
                1,
            ),
            "death": Animation(
                fenetre,
                x,
                y,
                "Assets/Boss/Gravelion/Gravelion_death.png",
                14,
                100,
                100,
                0,
                0,
                1,
            ),
        }

        # Vitesse d'animation
        v = 60
        speeds = {
            "idle": 4 / v / 2,
            "glowing": 8 / v,
            "arm": 9 / v * 1.5,
            "cocon": 8 / v,
            "melee": 7 / v * 1.5,
            "laser_charge": 7 / v,
            "transition": 10 / v / 2,
            "death": 14 / v / 2,
        }

        for state, speed in speeds.items():
            self.anims[state].vitesse_animation = speed

        for anim in self.anims.values():
            anim.frames_droite = [pygame.transform.scale(frame, (160, 160)) for frame in anim.frames_droite]

            anim.frames_gauche = [
                pygame.transform.flip(frame, True, False)
                for frame in anim.frames_droite  # Flip les frames droites en x, mais pas en y
            ]

        self.current_anim = "idle"
        self.rect = pygame.Rect(0, 0, 80, 80)
        self.rect.center = (x, y)
        self.image = self.anims["idle"].frames_droite[0]

        # Timers et variables d'attaque
        self.idle_duration = 1500
        self.cocon_punish = False
        self.cocon_chance = 1 / 6
        self.laser = None

        # Spawn (direct pour le trailer)
        self.enter_state(self.IDLE)
        self.rect.center = (x, y)  # spawn position ds tiled
        self.position = pygame.math.Vector2(self.rect.centerx, self.rect.bottom)

    def is_on_ground(self):
        """Exécute la logique de la fonction is_on_ground liée à d'un boss, modifiant l'état ou produisant une action spécifique.
        Entrées: aucune.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        return self.current_tp_index in [self.SOL_GAUCHE, self.SOL_DROIT]

    def choose_attack(self, player_rect):
        """Exécute la logique de la fonction choose_attack liée à d'un boss, modifiant l'état ou produisant une action spécifique.
        Entrées: player_rect.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        distance = abs(player_rect.centerx - self.rect.centerx)

        if random.random() < self.cocon_chance:
            return self.ATK_COCON

        if not self.is_on_ground():
            return random.choice([self.ATK_LASER, self.ATK_ARM])

        if distance < 200 and self.phase == 1:
            return self.ATK_MELEE
        return random.choice([self.ATK_MELEE, self.ATK_ARM])

    # Contre-attaque cocon
    def hit_while_shielded(self):
        """Exécute la logique de la fonction hit_while_shielded liée à d'un boss, modifiant l'état ou produisant une action spécifique.
        Entrées: aucune.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.cocon_punish = True

    # Update principal du boss
    def update(self, player_rect, player, platforms):
        """Met à jour l'état du joueur (position, santé, capacités) en fonction des entrées, des collisions et du temps.
        Entrées: player_rect, player, platforms.
        Sortie: Aucune valeur renvoyée (None).
        """
        now = pygame.time.get_ticks()
        elapsed = now - self.state_timer

        # if self.state == self.NOT_TRIGGERED:
        # pass

        if self.state == self.IDLE:
            self.update_idle(elapsed, player_rect)

        elif self.state == self.ATTACKING:
            self.update_attack(elapsed, player_rect)

        elif self.state == self.TELEPORTING:
            self.update_teleport(elapsed, player_rect)

        elif self.state == self.SHIELDED:
            self.update_cocon(elapsed, player_rect, player)

        elif self.state == self.STAGGER:
            self.update_stagger(elapsed, platforms)

        elif self.state == self.TRANSITION:
            self.update_transition()

        elif self.state == self.DYING:
            self.update_dying(elapsed)

        self.update_hitbox(platforms, self.arene_rect)

        once_states = ["melee", "arm", "cocon", "laser_charge", "transition", "death"]
        self.update_anim(self.current_anim in once_states)

    # ETATS

    def update_idle(self, elapsed, player_rect):
        """Met à jour l'état du joueur (position, santé, capacités) en fonction des entrées, des collisions et du temps.
        Entrées: elapsed, player_rect.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.current_anim = "idle"
        if elapsed >= self.speed(self.idle_duration):
            self.face_player(player_rect)
            self.current_attack = self.choose_attack(player_rect)
            if self.current_attack == self.ATK_COCON:
                self.enter_state(self.SHIELDED)
            else:
                self.enter_state(self.ATTACKING)

    def update_dying(self, elapsed):
        """Met à jour les animations d'un boss, avance les frames et gère les transitions entre animations.
        Entrées: elapsed.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.current_anim = "death"
        if self.anim_over() and elapsed > 500:
            self.alive = False

    def update_transition(self):
        """Met à jour les animations d'un boss, avance les frames et gère les transitions entre animations.
        Entrées: aucune.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.current_anim = "transition"
        self.velocity = pygame.math.Vector2(0, 0)
        self.update_anim(once=True)
        if self.anim_over():
            self.phase = 2
            self.scale_all_anims_speed(1.3)
            self.idle_duration = 1000
            self.cocon_chance = 1 / 4
            self.enter_state(self.TELEPORTING)

    def update_attack(self, elapsed, player_rect):
        """Met à jour l'état du joueur (position, santé, capacités) en fonction des entrées, des collisions et du temps.
        Entrées: elapsed, player_rect.
        Sortie: Aucune valeur renvoyée (None).
        """
        if self.current_attack == self.ATK_MELEE:
            self.attack_melee(elapsed)
        elif self.current_attack == self.ATK_ARM:
            self.attack_arm(elapsed, player_rect)
        elif self.current_attack == self.ATK_LASER:
            head = self.rect.midtop + pygame.math.Vector2(0, 20)
            self.attack_laser(elapsed, head)

    def update_cocon(self, elapsed, player_rect, player):
        """Gère la réception des dégâts d'un boss en appliquant les effets selon les attributs de la source (dégâts, type, recul, invincibilité, etc.).
        Entrées: elapsed, player_rect, player.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        self.current_anim = "cocon"
        self.is_shielded = True  # Pour ne pas prendre de dégats pendant le cocon

        if self.cocon_punish:
            # Si le joueur touche le cocon, il subit une contre-attaque
            self.cocon_punish = False
            self.is_shielded = False
            self.position.x = player.position.x - 100 * player.direction  # Se téléporte dans le dos du joeur
            self.position.y = player.position.y
            self.rect.center = (self.position.x, self.position.y)
            self.face_player(player_rect)
            self.current_attack = self.ATK_MELEE
            self.enter_state(self.ATTACKING)
            return

        if elapsed >= 1500:
            # Fin du cocon sans etre frappé
            self.is_shielded = False
            self.enter_state(self.TELEPORTING)

    # ATTAQUES
    def attack_melee(self, elapsed):
        """Gère la réception des dégâts d'un boss en appliquant les effets selon les attributs de la source (dégâts, type, recul, invincibilité, etc.).
        Entrées: elapsed.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.current_anim = "melee"
        charge = self.speed(600)
        if elapsed >= charge and not self.atk_spawned:
            self.spawn_attack_zone(
                x=self.rect.centerx + (20 if self.direction == 1 else -120),
                y=self.rect.bottom - 100,
                width=100,
                height=100,
                attack_data={"damage": 1, "knockback_x": 40, "knockback_y": -10},
                image=None,
                duration=300,
            )

            self.spawn_projectile(
                target_x=self.arene_rect.right if self.direction == 1 else self.arene_rect.left,
                target_y=self.rect.bottom,
                speed=self.speed(10, is_proj=True),
                width=70,
                height=50,
                damage=1,
                offset_x=-70 if self.direction != 1 else 0,
                offset_y=0,
                image=pygame.image.load("Assets\Boss\Gravelion\shockwave.png").convert_alpha(),
            )
            self.atk_spawned = True

        if elapsed >= charge + self.speed(800):
            self.enter_state(self.TELEPORTING)

    def attack_arm(self, elapsed, player_rect):
        """Gère la réception des dégâts d'un boss en appliquant les effets selon les attributs de la source (dégâts, type, recul, invincibilité, etc.).
        Entrées: elapsed, player_rect.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.current_anim = "arm"
        charge = self.speed(500)
        if elapsed >= charge and not self.atk_spawned:
            self.spawn_projectile(
                target_x=player_rect.centerx,
                target_y=player_rect.centery,
                speed=self.speed(8, is_proj=True),
                width=60,
                height=25,
                damage=1,
                offset_x=self.direction * 60,
                offset_y=-20,
                image=pygame.image.load("Assets\Boss\Gravelion\Arm_projectile.png").convert_alpha(),
            )
            self.atk_spawned = True

        if elapsed >= charge + 800:
            self.enter_state(self.TELEPORTING)

    def attack_laser(self, elapsed, head):
        """Gère la réception des dégâts d'un boss en appliquant les effets selon les attributs de la source (dégâts, type, recul, invincibilité, etc.).
        Entrées: elapsed, head.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.current_anim = "laser_charge"
        charge = self.speed(1000)

        if elapsed >= charge:
            if self.laser is None:
                self.laser = self.spawn_attack_zone(
                    x=head.x,
                    y=head.y,
                    width=10,
                    height=800,
                    attack_data={"damage": 2, "knockback_x": 80, "knockback_y": -2},
                    image=pygame.image.load("Assets\Boss\Gravelion\Laser_sheet.png"),
                    duration=9999,
                )
            move_speed = self.speed(7, is_proj=True)

            if self.current_tp_index == self.AIR_GAUCHE:
                self.rect.x += move_speed
            else:
                self.rect.x -= move_speed
            head = self.rect.midtop + pygame.math.Vector2(0, 20)
            self.laser.rect.midtop = (head.x, head.y)

            if elapsed >= charge + 900:
                if self.laser in self.hitboxs:
                    self.hitboxs.remove(self.laser)
                self.laser = None
                self.enter_state(self.TELEPORTING)

    def draw(self, fenetre, camera):
        """Dessine d'un boss à l'écran en tenant compte de la caméra, de la position et de l'animation.
        Entrées: fenetre, camera.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        if not self.alive:
            return

        sprite_rect = self.image.get_rect(center=self.rect.center)

        fenetre.blit(self.image, camera.apply(sprite_rect))

        for elem in self.hitboxs:
            elem.draw(fenetre, camera)
