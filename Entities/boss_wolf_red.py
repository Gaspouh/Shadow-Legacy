import pygame
import random
from Entities.boss_logic import Boss
from Visual.sprite_sheet import Animation
from World.objets import Monnaie


class Red_Wolf(Boss):

    def __init__(self, fenetre, x, y):
        path = "Assets/Boss/Loups/Red_Wolf"
        self.fenetre = fenetre
        vitesse_initiale = 3
        offset_y = 30
        self.run_start_time = None  # quand il a commencé à courir
        self.run_min_duration = 2000  # 2s minimum de course


        super().__init__(
            fenetre, x, y,
            path+"/Idle.png", 8, 128, 128, 0, 0,
            pv_max=18,
            vitesse=vitesse_initiale,
            attack_data={"damage": 1, "knockback_x": 50, "knockback_y": -5},
            tp_points=[(x, y)],
            stagger_threshold=50,
            scale=1
        )
        self.vitesse = vitesse_initiale
        self.can_receive_knockback = True
        self.arene_rect = pygame.Rect(-99999, -99999, 999999, 999999)  # pas d'arene (arene infinieà

        # reward à la mort
        self.orbs_value = 50
        self.orbs_added = False

        # cooldowns
        self.attack_cooldown = 200
        self.last_attack_time = 0
        self.jump_cooldown = 4800
        self.last_jump_time = 0
        self.pursuit_start_time = None  # qd la poursuite a commencé

        # trigger "dynamique", pour un comportement plus réalisste, le loup peut perdre de vu le joueur
        self.trigger_small = 300
        self.trigger_large = 400
        self.trigger_actif = self.trigger_small
        self.last_seen_time = None  # derniere fois que le joueur etait dans le grand trigger

        # il patrouille quand pas déclenché
        self.patrol_dir = 1
        self.patrol_timer = pygame.time.get_ticks()
        self.patrol_duration = 2800  # change de direction toutes les 2.8s

        # Animations
        w, h = 128, 128
        scale = self.scale
        self.anims = {
            "idle": Animation(fenetre, x, y, path+"/Idle.png", 8, w, h, 0, 0, scale),
            "walk": Animation(fenetre, x, y, path+"/walk.png", 11, w, h, 0, 0, scale),
            "run": Animation(fenetre, x, y, path+"/Run.png", 9, w, h, 0, 0, scale),
            "jump": Animation(fenetre, x, y, path+"/Jump.png", 11, w, h, 0, 0, scale),
            "hurt": Animation(fenetre, x, y, path+"/Hurt.png", 2, w, h, 0, 0, scale),
            "death": Animation(fenetre, x, y, path+"/Dead.png", 2, w, h, 0, 0, scale),
            "attack1": Animation(fenetre, x, y, path+"/Attack_1.png", 6, w, h, 0, 0, scale),
            "attack2": Animation(fenetre, x, y, path+"/Attack_2.png", 4, w, h, 0, 0, scale),
            "attack3": Animation(fenetre, x, y, path+"/Attack_3.png", 5, w, h, 0, 0, scale),
            "run_attack": Animation(fenetre, x, y, path+"/Run+Attack.png", 7, w, h, 0, 0, scale)
        }
        for anim in self.anims.values():
            anim.vitesse_animation = 0.08
            for anim in self.anims.values():
                anim.vitesse_animation = 0.08
                anim.frames_droite = [pygame.transform.scale(f, (int(128 * 1.4), int(128 * 1.4))) for f in anim.frames_droite]
                anim.frames_gauche = [pygame.transform.scale(f, (int(128 * 1.4), int(128 * 1.4))) for f in anim.frames_gauche]

        self.current_anim = "idle"  # anim de base
        self.image = self.anims["idle"].frames_droite[0]

        # gestion hitbox
        w_scaled = int(w * 1.4)
        self.hitbox_offset_x =  w_scaled // 3   # valeur ajustée visuellement
        hitbox_w = w_scaled -self.hitbox_offset_x * 2
        self.offset_y = 70
        self.rect = pygame.Rect(x + self.hitbox_offset_x, y + offset_y, hitbox_w, int((72) * 1.5))
        self.position = pygame.math.Vector2(self.rect.centerx, self.rect.bottom)

        # attack range
        self.attack_range_x = 75
        self.attack_range_y = 92

        self.enter_state(self.NOT_TRIGGERED)

    def enter_state(self, new_state):
        if new_state == self.ATTACKING:
            self.sprint_start_time = None  # attaque reset le sprint
        super().enter_state(new_state)

    """ partie de gestion de la detection """
    def joueur_detecte(self, player_rect):
        # zone moins large sur x
        dx = abs(player_rect.centerx - self.rect.centerx) * 1.35
        dy = abs(player_rect.centery - self.rect.centery)
        r = self.trigger_actif
        return (dx * dx + dy * dy) <= r * r

    def update_trigger(self, player_rect, now):
        # savoir si le joueur est dans le trigger
        if self.trigger_actif == self.trigger_large:
            if self.joueur_detecte(player_rect):
                self.last_seen_time = now
            else:
                # 5s de reset pour que le trigger soit petit
                if self.last_seen_time and now - self.last_seen_time >= 5000:
                    self.trigger_actif = self.trigger_small
                    self.pursuit_start_time = None
                    self.last_seen_time = None
                    self.enter_state(self.NOT_TRIGGERED)


    def zone_attaque(self):
        if self.direction == 1:
            return pygame.Rect(self.rect.right, self.rect.centery - self.attack_range_y // 2,
                               self.attack_range_x, self.attack_range_y)
        
        return pygame.Rect(self.rect.left - self.attack_range_x, self.rect.centery - self.attack_range_y // 2,
                           self.attack_range_x, self.attack_range_y)

    def joueur_dans_attack(self, player_rect):
        return self.zone_attaque().colliderect(player_rect)
    
    def receive_hit(self, attack_data, source_rect, source):
        if not self.alive or self.is_shielded:
            return
        self.pv_ennemi -= attack_data["damage"]

        # gestion knockback
        direction = 1 if source_rect.centerx< self.rect.centerx else -1
        self.velocity.x = attack_data.get("knockback_x", 0) * direction * 0.3
        self.velocity.y = attack_data.get("knockback_y", 0)

        if self.pv_ennemi <= 0:
            self.pv_ennemi = 0
            # gere la mort, update_dying ne suffit pas car il faut changer state
            if self.state != self.DYING:
                self.enter_state(self.DYING)


    def update(self, player_rect, player, platforms=[]):
        """ fonction update main du blackwolf """
        now = pygame.time.get_ticks()
        elapsed = now - self.state_timer

        if not self.alive:
            return

        self.update_trigger(player_rect, now)

        if self.state == self.NOT_TRIGGERED:
            self.update_patrol(now)
            if self.joueur_detecte(player_rect):
                # 1ere détection
                self.trigger_actif = self.trigger_large
                self.last_seen_time = now
                self.pursuit_start_time = now
                self.last_jump_time = now  # jump possible au bout de 7s
                self.enter_state(self.IDLE)

        elif self.state == self.IDLE:
            self.update_idle(elapsed, player_rect, now)

        elif self.state == self.ATTACKING:
            self.update_attack(elapsed, player_rect, player)

        elif self.state == self.STAGGER:
            self.update_stagger(elapsed)

        elif self.state == self.DYING:
            self.update_dying(elapsed)
        self.physics_update(platforms)
        self.update_hitbox(platforms, self.arene_rect)

    def update_patrol(self, now):
        # simuler des "rondes"
        self.current_anim = "walk"
        self.velocity.x = 1 * self.patrol_dir
        self.direction = self.patrol_dir

        if now - self.patrol_timer >= self.patrol_duration:
            self.patrol_dir *= -1  # change de dir
            self.patrol_timer = now

        self.update_anim()

    def update_idle(self, elapsed, player_rect, now):
        self.face_player(player_rect)
        d_x = abs(player_rect.centerx - self.rect.centerx)

        # jump attack
        jump_dispo = (
            self.pursuit_start_time is not None and
            now - self.last_jump_time >= self.jump_cooldown
        )

        # gestion attaque
        if self.joueur_dans_attack(player_rect):
            if now - self.last_attack_time >= self.attack_cooldown:
                self.current_attack = random.choice(["attack1", "attack2", "attack3"])
                self.last_attack_time = now
                self.enter_state(self.ATTACKING)
                return

        # bond si cooldown est reset et le joueur est a portée
        if jump_dispo and d_x < 380:
            self.current_attack = "run_attack"
            self.last_jump_time = now
            self.enter_state(self.ATTACKING)
            return

        # poursuite normale
        if d_x > 5:
            if d_x > 300: # il run si il est loin
                if self.run_start_time is None:
                    self.run_start_time = now
                self.current_anim = "run"
                self.velocity.x = self.vitesse * 4.5 * self.direction
            else: # sinon marche
                run_end = self.run_start_time is None or now - self.run_start_time >= self.run_min_duration # verifie si le run est fini
                if run_end:
                    self.run_start_time = None  # reset
                    self.current_anim = "walk"
                    self.velocity.x = self.vitesse * self.direction
                else:
                    #continue de sprint
                    self.current_anim = "run"
                    self.velocity.x = self.vitesse * 4.5 * self.direction

        else:
            self.run_start_time = None
            self.current_anim = "idle"
            self.velocity.x = 0

        self.update_anim()

    def update_attack(self, elapsed, player_rect, player):
        self.current_anim = self.current_attack

        if self.current_attack == "run_attack":
            # gestion de l'attaque en sautant
            if elapsed < 150:
                self.velocity.y = -5  # saut
                self.velocity.x = self.vitesse * 1.5 * self.direction

            if elapsed >= 250 and not self.atk_spawned:
                self.spawn_attack_zone(
                    x=self.zone_attaque().x,
                    y=self.zone_attaque().y,
                    width=self.attack_range_x + 20,  # un peu plus grande pendant le bond
                    height=self.attack_range_y + 20,
                    attack_data=self.attack_data,
                    image=None,
                    duration=250
                )
                self.atk_spawned = True

            if elapsed >= 900:
                self.enter_state(self.IDLE)

        else:
            # attaques de base
            self.velocity.x *= 0.8  # ralentit qd il attaque

            if elapsed >= 200 and not self.atk_spawned:
                self.spawn_attack_zone(
                    x=self.zone_attaque().x,
                    y=self.zone_attaque().y,
                    width=self.attack_range_x,
                    height=self.attack_range_y,
                    attack_data=self.attack_data,
                    image=None,
                    duration=200
                )
                self.atk_spawned = True

            if elapsed >= 800:
                self.enter_state(self.IDLE)

        self.update_anim()

   # gesiton de mort (et la reward)
    def mort(self):
        if not self.alive:
            if not self.orbs_added:
                Monnaie.add_orbs(self.orbs_value)
                self.orbs_added = True
            return True
        return False
    
    def update_dying(self, elapsed):
        self.current_anim = "death"
        self.update_anim(once=True)

        anim = self.anims["death"]
        # once=True bloque sur la dernière frame, anim_over() ne marchera jamais
        # donc on check directement si on est à la fin
        if anim.index_image >= len(anim.frames_droite) - 1 and elapsed > 500:
            self.alive = False


    # affichage
    def draw(self, fenetre, camera):
        if not self.alive:
            return
        cam_rect = camera.apply(self.rect)
        # le sprite est plus large que la hitbox, on le recentre
        fenetre.blit(self.image, (cam_rect.x - self.hitbox_offset_x, cam_rect.y - self.offset_y))
        for elem in self.hitboxs:
            elem.draw(fenetre, camera)  