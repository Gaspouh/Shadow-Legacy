import pygame
from Entities.ennemi import Ennemi, Projectile, AttackZone
from Visual.sprite_sheet import VerticalAnimation
import random
from World.objets import Monnaie


class Boss(Ennemi):
    # Etats généraiques à tous les boss
    NOT_TRIGGERED = "NOT_TRIGGERED"  # avant que le joueur soit détecté
    IDLE = "IDLE"
    ATTACKING = "ATTACKING"
    STAGGER = "STAGGER"  # temps de repos après X dégâts
    TRANSITION = "TRANSITION"  # changement de phase
    DYING = "DYING"

    def __init__(
        self,
        fenetre,
        x,
        y,
        sprite_sheet,
        nb_frames,
        width,
        height,
        marge,
        ligne,
        pv_max,
        vitesse,
        attack_data,
        tp_points,
        stagger_threshold=150,
        scale=1,
    ):
        super().__init__(
            fenetre,
            x,
            y,
            sprite_sheet,
            nb_frames,
            width,
            height,
            marge,
            ligne,
            pv_max,
            vitesse,
            attack_data,
            scale=1,
        )

        self.can_receive_knockback = False  # Pas de recul pour les boss
        self.sprite_inverted = False
        self.combat_lance = False
        self.dead = False  # pour l'animation de mort

        self.phase = 1
        self.state = self.IDLE
        self.state_timer = pygame.time.get_ticks()
        self.current_attack = None
        self.is_attacking = False
        self.attack_rect = pygame.Rect(0, 0, 0, 0)

        self.tp_points = tp_points
        self.current_tp_index = 0

        self.stagger_threshold = stagger_threshold
        self.pv_last_stagger = pv_max
        self.stagger_duration = 3000  # 3 secondes de pause après le seuil de dégâts
        self.touch_ground = False

        self.hitboxs = []
        self.anims = {}
        self.current_anim = "idle"

    def receive_hit(self, attack_data, source_rect, source):

        """Gère la réception des dégâts d'un boss en appliquant les effets selon les attributs de la source (dégâts, type, recul, invincibilité, etc.).
        Entrées: attack_data, source_rect, source.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        if not self.alive:
            return

        if self.is_shielded:
            self.hit_while_shielded()
            return

        super().receive_hit(attack_data, source_rect, source)
        self.alive = True  # Overwrite pour jouer l'anim de mort

        # Stagger
        if self.pv_last_stagger - self.pv_ennemi >= self.stagger_threshold:
            self.enter_state(self.STAGGER)
            self.pv_last_stagger = self.pv_ennemi

        # Changement de phase
        if self.pv_ennemi < self.pv_max // 2 and self.phase == 1:
            self.enter_state(self.TRANSITION)

        # Mort
        if self.pv_ennemi <= 0 and self.state != self.DYING:
            self.enter_state(self.DYING)

    def hit_while_shielded(self):
        # Comportement spécifique lorsqu'il est touché avec un bouclier actif propre a chaque boss donc à redéfinir dans chaque classe de boss
        """ gere le comportement spécifique lorsqu'un boss est touché avec un bouclier actif, modifiant potentiellement l'état du boss ou produisant une action spécifique.
        Entrées: aucune.
        Sortie: Aucune valeur renvoyée (None).
        """
        pass

    # Gestion des états

    def enter_state(self, new_state):
        """ Change l'état d'un boss et réinitialise les timers et flags associés à ce nouvel état.
        Entrées: new_state.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.state = new_state
        self.state_timer = pygame.time.get_ticks()
        self.atk_spawned = False
        if self.current_anim in self.anims:
            self.anims[self.current_anim].index_image = 0.0  # Réinitialiser l'animation à chaque changement d'état
            self.anims[self.current_anim].fin = False  # Réinitialiser le flag de fin d'animation

    def face_player(self, player_rect):
        """Calcule et retourne la frame correcte suivant la direction et l'état d'un boss pour l'affichage.
        Entrées: player_rect.
        Sortie: Aucune valeur renvoyée (None).
        """
        if player_rect.centerx > self.rect.centerx:
            self.direction = 1
        else:
            self.direction = -1

    def teleport(self, index):
        """Téléporte d'un boss à une position cible et ajuste sa hitbox / état si nécessaire.
        Entrées: index.
        Sortie: Aucune valeur renvoyée (None).
        """
        x, y = self.tp_points[index]
        self.rect.midbottom = (x, y)
        self.position = pygame.math.Vector2(self.rect.centerx, self.rect.bottom)
        self.current_tp_index = index
        self.velocity = pygame.math.Vector2(0, 0)

    def teleport_random(self):
        """Téléporte d'un boss à une position cible et ajuste sa hitbox / état si nécessaire.
        Entrées: aucune.
        Sortie: Aucune valeur renvoyée (None).
        """
        indices = list(range(len(self.tp_points)))
        if self.current_tp_index in indices:
            indices.remove(self.current_tp_index)  # éviter de se téléporter au même endroit
        self.teleport(random.choice(indices))

    # Animation

    def update_anim(self, once=False):
        """Met à jour les animations d'un boss, avance les frames et gère les transitions entre animations.
        Entrées: once.
        Sortie: Aucune valeur renvoyée (None).
        """
        anim = self.anims[self.current_anim]

        if once:
            anim.gestion_animation_once()
        else:
            anim.gestion_animation()

        index = int(anim.index_image)

        if self.direction == 1 and not self.sprite_inverted or self.direction != 1 and self.sprite_inverted:
            self.image = anim.frames_droite[index]
        else:
            self.image = anim.frames_gauche[index]

    def anim_over(self):
        """Vérifie si l'animation actuelle d'un boss est terminée, ce qui peut être utilisé pour déclencher des transitions d'état ou des actions spécifiques à la fin de l'animation.
        Entrées: aucune.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        anim = self.anims[self.current_anim]
        return anim.fin

    def speed(self, valeur_base, is_proj=False):
        # Augmente la vitesse de déplacement et d'animation en fonction de la phase
        """Ajuste la vitesse de déplacement et d'animation d'un boss en fonction de sa phase actuelle, avec des multiplicateurs spécifiques pour les projectiles si nécessaire.
        Entrées: valeur_base, is_proj.
        Sortie: Retourne une valeur si applicable
        """
        if self.phase == 1:
            return valeur_base
        else:
            if is_proj:
                return valeur_base * 1.5
            return valeur_base / 1.3

    def scale_all_anims_speed(self, factor):
        """Ajuste la vitesse d'animation d'un boss en fonction de sa phase actuelle
        Entrées: factor.
        Sortie: Aucune valeur renvoyée
        """
        for anims in self.anims.values():
            anims.vitesse_animation *= factor

    # Spawn et gestion des hitboxs

    def spawn_attack_zone(self, x, y, width, height, attack_data, image, duration):
        """Fait apparaître une hitbox d'attaque pour un boss avec des propriétés spécifiques (dégâts, durée, etc.) et l'ajoute à la liste des hitboxs actives.
        Entrées: x, y, width, height, attack_data, image, duration.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        zone = AttackZone(x, y, width, height, attack_data, image, duration)
        self.hitboxs.append(zone)
        return zone

    def spawn_projectile(
        self,
        target_x,
        target_y,
        speed,
        width,
        height,
        damage,
        offset_x,
        offset_y,
        image=None,
        gravity=0.4,
        lifetime=3000,
        should_disappear_on_contact=True,
    ):
        """Gère la réception des dégâts d'un boss en appliquant les effets selon les attributs de la source (dégâts, type, recul, invincibilité, etc.).
        Entrées: target_x, target_y, speed, width, height, damage, offset_x, offset_y, image, gravity, lifetime, should_disappear_on_contact.
        Sortie: Aucune valeur renvoyée (None).
        """
        projectile = Projectile(
            self.rect.centerx + offset_x,
            self.rect.centery + offset_y,
            target_x,
            target_y,
            speed,
            width,
            height,
            damage,
            image,
            gravity,
            lifetime,
            should_disappear_on_contact,
        )
        self.hitboxs.append(projectile)

    def update_hitbox(self, platforms, limite_rect):
        """Met à jour les hitboxs actives d'un boss, en gérant les collisions avec les plateformes et les limites de l'arène, et en supprimant les hitboxs expirées ou détruites.
        Entrées: platforms, limite_rect.
        Sortie: Aucune valeur renvoyée (None).
        """
        for elem in self.hitboxs[:]:
            if hasattr(elem, "update"):
                delete = elem.update(platforms, limite_rect)
            else:
                delete = elem.lifetime_expired()
            if delete:
                self.hitboxs.remove(elem)

    # Etats génériques

    def update_stagger(self, elapsed, platforms):
        """Met à jour les animations d'un boss, avance les frames et gère les transitions entre animations.
        Entrées: elapsed, platforms.
        Sortie: Aucune valeur renvoyée (None).
        """
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                self.touch_ground = True
                self.rect.bottom = platform.rect.top
        if not self.touch_ground:
            self.position.y += 3
            self.rect.y = self.position.y
        self.current_anim = "idle"
        self.velocity = pygame.math.Vector2(0, 0)
        if elapsed >= self.stagger_duration:
            self.enter_state(self.TELEPORTING)
            self.touch_ground = False

    def update_teleport(self, elapsed, player_rect):
        """Met à jour l'état d'un boss en appliquant la logique temporelle, collisions et transitions d'état.
        Entrées: elapsed, player_rect.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.current_anim = "glowing"
        if elapsed >= 600:
            self.teleport_random()
            self.face_player(player_rect)
            self.enter_state(self.IDLE)


class Golem(Boss):
    ATK_SMASH = "smash"

    def __init__(self, fenetre, x, y):
        tp_points = [(x, y)]
        super().__init__(
            fenetre,
            x,
            y,
            "Assets/Boss/golem/golem_idle_sheet.png",
            40 * 2,
            240 * 2,
            240 * 2,
            0,
            0,
            pv_max=10,
            vitesse=1,
            attack_data={
                "damage": 1,
                "knockback_x": 100,
                "knockback_y": -5,
            },  # Dégat au contact
            tp_points=tp_points,
            stagger_threshold=3,
            scale=1,
        )

        # Variables principales
        self.use_gravity = True
        self.can_receive_knockback = True  # gestion du recul
        self.recul_intensite = 0.1
        self.orbs_value = 30
        self.vitesse_deplacement = 2

        self.arene_rect = pygame.Rect(-99999, -99999, 999999, 999999)

        self.orbs_value = 15

        self.scale = 0.5

        # Gestion hitbox
        self.rect = pygame.Rect(x, y, 70, 80)
        self.position = pygame.math.Vector2(self.rect.centerx, self.rect.bottom)
        self.sprite_offset_y = 500

        # Triggerbox
        self.trigger_range = 250

        # Attack range
        self.attack_range_x = 57
        self.attack_range_y = 125

        # Cooldown d'attaque
        self.attack_cooldown = 2000

        # Spriteheets, animations :
        v = 200
        self.anims = {
            "idle": VerticalAnimation(
                fenetre,
                x,
                y,
                "Assets/Boss/golem/golem_idle_sheet.png",
                40,
                240,
                240,
                0,
                0,
            ),
            "walk_right": VerticalAnimation(
                fenetre,
                x,
                y,
                "Assets/Boss/golem/golem_walk_right_sheet.png",
                32,
                240,
                240,
                0,
                0,
            ),
            "walk_left": VerticalAnimation(
                fenetre,
                x,
                y,
                "Assets/Boss/golem/golem_walk_left_sheet.png",
                32,
                240,
                240,
                0,
                0,
            ),
            "smash_right": VerticalAnimation(
                fenetre,
                x,
                y,
                "Assets/Boss/golem/golem_smash_right_sheet.png",
                12,
                240,
                240,
                0,
                0,
            ),
            "smash_left": VerticalAnimation(
                fenetre,
                x,
                y,
                "Assets/Boss/golem/golem_smash_left_sheet.png",
                12,
                240,
                240,
                0,
                0,
            ),
        }

        for anim in self.anims.values():
            anim.frames_droite = [
                pygame.transform.scale(f, (int(240 * self.scale), int(240 * self.scale))) for f in anim.frames_droite
            ]
            anim.frames_gauche = [
                pygame.transform.scale(f, (int(240 * self.scale), int(240 * self.scale))) for f in anim.frames_gauche
            ]

        # Vitesses d'animation (divisé par 60 pour chaque frame)
        self.anims["idle"].vitesse_animation = 40 / v / 2
        self.anims["walk_right"].vitesse_animation = 32 / v / 1.5
        self.anims["walk_left"].vitesse_animation = 32 / v / 1.5
        self.anims["smash_right"].vitesse_animation = 12 / v * 2
        self.anims["smash_left"].vitesse_animation = 12 / v * 2

        # Affichage de base
        self.current_anim = "idle"
        self.image = self.anims["idle"].frames_droite[0]

        # Sons
        self.smash_sounds = [
            pygame.mixer.Sound("Assets/Sounds/golem_smash_sound1.MP3"),
            pygame.mixer.Sound("Assets/Sounds/golem_smash_sound2.MP3"),
        ]
        self.death_sound = pygame.mixer.Sound("Assets/Sounds/golem_death.MP3")
        self.smash_played_sound = False
        self.death_sound_played = False

        self.combat_lance = False
        self.enter_state(self.NOT_TRIGGERED)

    def receive_hit(self, attack_data, source_rect, source):
        """Gère la réception des dégâts d'un boss en appliquant les effets selon les attributs de la source (dégâts, type, recul, invincibilité, etc.).
        Entrées: attack_data, source_rect, source.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        if not self.alive:
            return

        self.pv_ennemi -= attack_data["damage"]

        # petit knockback
        if source_rect.centerx < self.rect.centerx:
            self.velocity.x = 3
        else:
            self.velocity.x = -3

        if self.pv_ennemi <= 0:
            self.alive = False
            Monnaie.orbs += self.orbs_value

            if not self.death_sound_played:
                self.death_sound.play()
                self.death_sound_played = True

    def _zone_smash(self):
        """Calcule et retourne la frame correcte suivant la direction et l'état d'un boss pour l'affichage.
        Entrées: aucune.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        if self.direction == 1:
            return pygame.Rect(
                self.rect.right,
                self.rect.centery - self.attack_range_y // 2,
                self.attack_range_x,
                self.attack_range_y,
            )
        return pygame.Rect(
            self.rect.left - self.attack_range_x,
            self.rect.centery - self.attack_range_y // 2,
            self.attack_range_x,
            self.attack_range_y,
        )

    def _joueur_dans_attack(self, player_rect):
        """Vérifie si le joueur est dans la zone d'attaque d'un boss.
        Entrées: player_rect.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        return self._zone_smash().colliderect(player_rect)

    def _update_anim(self, key):
        """Met à jour les animations d'un boss, avance les frames et gère les transitions entre animations.
        Entrées: key.
        Sortie: Aucune valeur renvoyée (None).
        """
        anim = self.anims[key]
        idx = int(anim.gestion_animation())

        if "left" in key:
            self.image = anim.frames_droite[idx]
        elif "right" in key:
            self.image = anim.frames_droite[idx]
        else:
            self.image = anim.frames_droite[idx] if self.direction == 1 else anim.frames_gauche[idx]

    def update(self, player_rect, player, platforms=[]):
        """Met à jour l'état d'un boss en appliquant la logique temporelle, collisions et transitions d'état.
        Entrées: player_rect, player, platforms.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        now = pygame.time.get_ticks()
        elapsed = now - self.state_timer

        if not self.alive:
            return

        # IA du golem
        if self.state == self.NOT_TRIGGERED:
            if self.dans_trigger(player_rect, self.trigger_range):
                self.combat_lance = True
                self.enter_state(self.IDLE)

        elif self.state == self.IDLE:
            self.update_idle(elapsed, player_rect)

        elif self.state == self.ATTACKING:
            self.update_attack(elapsed, player_rect, player)

        elif self.state == self.DYING:
            self.update_dying(elapsed)

        # Gravité et physique
        if self.state == self.IDLE and abs(self.velocity.x) < self.vitesse_deplacement:
            self.velocity.x = self.vitesse_deplacement * self.direction
        elif self.state == self.ATTACKING:
            # On laisse le recul agir un peu même pendant l'attaque, mais on freine fort
            self.velocity.x *= 0.9

        # Collion avec les plateformes
        self.physics_update(platforms)

        self.update_hitbox(platforms, self.arene_rect)

    def update_idle(self, elapsed, player_rect):
        # Idle
        """ la logique de l'état d'idle d'un boss, où il peut se déplacer ou attaquer en fonction de la position du joueur et des timers d'attaque.
        Entrées: elapsed, player_rect.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        self.face_player(player_rect)

        if self._joueur_dans_attack(player_rect):
            now = pygame.time.get_ticks()
            if now - self.state_timer >= self.attack_cooldown:
                self.current_attack = self.ATK_SMASH
                self.enter_state(self.ATTACKING)
                return

        # Poursuite
        dx = player_rect.centerx - self.rect.centerx
        if abs(dx) > 5:
            key = "walk_right" if self.direction == 1 else "walk_left"
        else:
            key = "idle"

        self._update_anim(key)

    def update_attack(self, elapsed, player_rect, player):
        """Met à jour l'état d'attaque d'un boss en appliquant la logique temporelle, collisions et transitions d'état, ainsi que les effets de l'attaque sur le joueur si celui-ci est touché.
        Entrées: elapsed, player_rect, player.
        Sortie: Aucune valeur renvoyée (None).
        """
        key = "smash_right" if self.direction == 1 else "smash_left"
        self._update_anim(key)

        if not self.smash_played_sound:
            import random

            random.choice(self.smash_sounds).play()
            self.smash_played_sound = True

        if elapsed >= 350 and not self.atk_spawned:
            atk = AttackZone(
                x=self._zone_smash().x,
                y=self._zone_smash().y,
                width=self.attack_range_x,
                height=self.attack_range_y,
                attack_data=self.attack_data,
                image=None,
                duration=200,
            )
            self.hitboxs.append(atk)
            self.atk_spawned = True

        if elapsed >= 1200:
            self.smash_played_sound = False
            self.enter_state(self.IDLE)

    def update_dying(self, elapsed):
        # meurt
        """Exécute la logique de l'état de mort d'un boss, en jouant l'animation de mort et en gérant les effets de la mort (disparition du sprite, récompenses pour le joueur, etc.).
        Entrées: elapsed.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.alive = False  # fait disparaitre le sprite
        Monnaie.add_orbs(self.orbs_value)
        if not self.death_sound_played:
            self.death_sound.play()
            self.death_sound_played = True

    def mort(self):
        """Exécute la logique de la fonction mort liée à d'un boss, modifiant l'état 
        Entrées: aucune.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        self.alive = False
        return True

    def draw(self, fenetre, camera):
        """Dessine d'un boss à l'écran en tenant compte de la caméra, de la position et de l'animation.
        Entrées: fenetre, camera.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        if not self.alive:
            return

        # Technique pour aligner le sprite avec la hitbox
        visual_rect = self.image.get_rect(midbottom=(self.rect.centerx, self.rect.bottom + 25))
        fenetre.blit(self.image, camera.apply(visual_rect))
