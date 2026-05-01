import pygame
from Entities.boss_logic import Boss
from Visual.sprite_sheet import Animation
import random

class Black_Wolf(Boss):
    def __init__(self, fenetre, x, y, arene_rect=None):
        tp_points = [(x, y)] # Points de téléportation par défaut
        path = "Assets/Boss/Loups/Black_Wolf"
        self.fenetre = fenetre
        vitesse_initiale = 3
        
        super().__init__(
            fenetre, x, y,
            f"{path}/Idle.png", 
            6, 128, 128, 0, 0, 
            pv_max=200,
            vitesse=vitesse_initiale,
            attack_data={"damage": 10, "knockback_x": 120, "knockback_y": -5},
            tp_points=tp_points,
            stagger_threshold=20,
            scale=1
        )
        self.vitesse = vitesse_initiale # sans ça ça bug

        # arene du boss
        self.arene_rect = arene_rect if arene_rect is not None else pygame.Rect(x - 1000, y - 1000, 2000, 2000)
        
        self.attack_cooldown = 1000
        self.last_attack_time = 0

        # Animations
        w, h = 120, 120 # Dimensions
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

        # Vitesse d'animation globale à ajuster
        for anim in self.anims.values():
            anim.vitesse_animation = 1

        self.current_anim = "idle"
        self.image = self.anims["idle"].frames_droite[0]
        
        # Hitbox de l'ia
        self.trigger_range = 400
        self.attack_range_x = 80
        self.attack_range_y = 100
        
        self.enter_state(self.NOT_TRIGGERED)

    def zone_attaque(self):
        if self.direction == 1:
            return pygame.Rect(self.rect.right, self.rect.centery - self.attack_range_y // 2,   # droite
                               self.attack_range_x, self.attack_range_y)
        return pygame.Rect(self.rect.left - self.attack_range_x, self.rect.centery - self.attack_range_y // 2,  # gauche
                           self.attack_range_x, self.attack_range_y)

    def joueur_dans_attack(self, player_rect):
        return self.zone_attaque().colliderect(player_rect)

    def update(self, player_rect, player, platforms=[]):
        now = pygame.time.get_ticks()
        elapsed = now - self.state_timer

        if not self.alive:
            return
        # Gestion des états (animations/transitions)
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
        
        # Physique du boss
        if self.state == self.IDLE and abs(self.velocity.x)<self.vitesse: # physique de transition
            self.velocity.x = self.vitesse *self.direction
        elif self.state == self.ATTACKING:
            self.velocity.x*= 0.8 # le fait ralentir vite

        self.physics_update(platforms)
        self.update_hitbox(platforms, self.arene_rect)

    def update_idle(self, elapsed, player_rect):
        self.face_player(player_rect)

        # Sélection d'une attaque
        if self.joueur_dans_attack(player_rect):
            now = pygame.time.get_ticks()
            if now - self.state_timer >= self.attack_cooldown:
                # choisi une attaque random
                self.current_attack = random.choice(["attack1", "attack2", "attack3"])
                self.enter_state(self.ATTACKING)
                return

        # poursuite
        d_x = player_rect.centerx - self.rect.centerx
        if abs(d_x) > 5: 
            # si le boss est loin il run, sinon il marche
            if abs(d_x) > 100:
                self.current_anim = "run"
            else:
                self.current_anim = "walk"
        else:
            self.current_anim = "idle"

        self.update_anim() # logique d'anim

    def update_attack(self, elapsed, player_rect, player):
        self.current_anim = self.current_attack
        self.update_anim()
        
        # créer la hitbox de l'attaque a un moment dans l'animation
        if elapsed >= 200 and not self.atk_spawned:
            atk = self.spawn_attack_zone(
                x = self.zone_attaque().x,
                y = self.zone_attaque().y,
                width=self.attack_range_x,
                height=self.attack_range_y,
                attack_data=self.attack_data,
                image=None,
                duration=200
            )
            self.atk_spawned = True

        # fin attaque
        if elapsed >= 1000:
            self.enter_state(self.IDLE)