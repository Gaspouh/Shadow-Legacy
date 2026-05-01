import pygame
import random
from Entities.boss_logic import Boss
from Visual.sprite_sheet import Animation

class Gravelion(Boss):

    #Indices points de téléportation
    SOL_GAUCHE = 0
    SOL_DROIT = 1
    AIR_GAUCHE = 2
    AIR_DROIT = 3

    #Noms des attaques :
    ATK_MELEE       = "melee"
    ATK_ARM         = "arm"
    ATK_LASER       = "laser"
    ATK_COCON       = "cocon"

    def __init__(self, fenetre,x, y, arene_rect):
        marge_x = 150
        hauteur_air = arene_rect.top + 150
        tp_points = [
            (arene_rect.left + marge_x, arene_rect.bottom),
            (arene_rect.right - marge_x, arene_rect.bottom),
            (arene_rect.left + marge_x, hauteur_air),
            (arene_rect.right - marge_x, hauteur_air)
        ]
        super().__init__(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 4, 400, 100, 0, 0, 500, 1,\
                        {"damage": 1, "knockback_x": 80, "knockback_y": -5}, tp_points, stagger_threshold=150, scale=1)

        self.arene_rect = arene_rect
        self.use_gravity = False # Pas de gravité pour ce boss lévitant

        # Animations 
        self.anims = {
            "idle":         Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 4, 100, 100, 0, 0, 1),
            "glowing":      Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 8, 100, 100, 0, 1, 1),
            "arm":          Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 9, 100, 100, 0, 2, 1),
            "cocon":        Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 8, 100, 100, 0, 3, 1),
            "melee":        Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 7, 100, 100, 0, 4, 1),
            "laser_charge": Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 7, 100, 100, 0, 5, 1),
            "transition":   Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 10, 100, 100, 0, 6, 1),
            "death":        Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 10, 1000, 100, 0, 7, 1) #Probleme avec la classe a regler pour fonctionner sur deux lignes
        }

        #Vitesse d'animation 
        v = 60
        speeds = {
            "idle": 4 / v / 2,
            "glowing": 8 / v,
            "arm": 9 / v * 1.5,
            "cocon": 8 / v,
            "melee": 7 / v * 1.5,
            "laser_charge": 7 / v,
            "transition": 10 / v / 2,
            "death": 14 / v / 3
        }
        
        for state, speed in speeds.items():
            self.anims[state].vitesse_animation = speed

        for anim in self.anims.values():
            anim.frames_droite = [
                pygame.transform.scale(frame, (160, 160)) for frame in anim.frames_droite
            ]

            anim.frames_gauche = [
                pygame.transform.flip(frame, True, False) for frame in anim.frames_droite # Flip les frames droites en x, mais pas en y
            ]
        
        self.current_anim = "idle"
        self.image = self.anims["idle"].frames_droite[0]
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.hitbox = self.rect.inflate(-40, -40)

        # Timers et variables d'attaque
        self.idle_duration = 1500
        self.cocon_punish = False
        self.cocon_chance = 1/6
        self.laser = None

        #Spawn 
        self.enter_state(self.NOT_TRIGGERED)
        self.teleport(self.SOL_DROIT)

    def is_on_ground(self):
        return self.current_tp_index in [self.SOL_GAUCHE, self.SOL_DROIT]
    
    def choose_attack(self, player_rect):
        distance = abs(player_rect.centerx - self.rect.centerx)

        cocon_chance = 1/4 if self.phase == 2 else self.cocon_chance
        if random.random() < cocon_chance:
            return self.ATK_COCON
        
        if not self.is_on_ground():
            return random.choice([self.ATK_LASER, self.ATK_ARM])
        
        if distance < 200:
            return self.ATK_MELEE
        return random.choice([self.ATK_MELEE, self.ATK_ARM])
    
    #Contre-attaque cocon
    def hit_while_shielded(self):
        self.cocon_punish = True

    #Update principal du boss
    def update(self, player_rect, player, platforms):
        now = pygame.time.get_ticks()
        elapsed = now - self.state_timer

        if self.state == self.NOT_TRIGGERED:
            pass

        elif self.state == self.IDLE:
            self.update_idle(elapsed, player_rect)

        elif self.state == self.ATTACKING:
            self.update_attack(elapsed, player_rect)

        elif self.state == self.TELEPORTING:
            self.update_teleport(elapsed, player_rect)

        elif self.state == self.SHIELDED:
            self.update_cocon(elapsed, player_rect, player)

        elif self.state == self.STAGGER:
            self.update_stagger(elapsed)

        elif self.state == self.TRANSITION:
            self.update_transition(elapsed)

        elif self.state == self.DYING:
            self.update_dying(elapsed)

        self.update_hitbox(platforms, self.arene_rect)
        self.hitbox.topleft = self.rect.center
                
        once_states = ["melee", "arm", "cocon", "laser_charge", "transition", "death"]
        self.update_anim(self.current_anim in once_states)

    # ETATS

    def update_idle(self, elapsed, player_rect):
        self.current_anim ="idle"
        if elapsed >= self.speed(self.idle_duration):
            self.face_player(player_rect)
            self.current_attack = self.choose_attack(player_rect)
            if self.current_attack == self.ATK_COCON:
                self.enter_state(self.SHIELDED)
            else:
                self.enter_state(self.ATTACKING)
        
    def update_attack(self, elapsed, player_rect):
        if self.current_attack == self.ATK_MELEE:
            self.attack_melee(elapsed)
        elif self.current_attack == self.ATK_ARM:
            self.attack_arm(elapsed, player_rect)
        elif self.current_attack == self.ATK_LASER:
            head = self.rect.midtop + pygame.math.Vector2(0, 20)
            self.attack_laser(elapsed, head)

    def update_cocon(self, elapsed, player_rect, player):
        self.current_anim = "cocon"
        self.is_shielded = True # Pour ne pas prendre de dégats pendant le cocon

        if self.cocon_punish:
            # Si le joueur touche le cocon, il subit une contre-attaque
            self.cocon_punish = False 
            self.is_shielded = False
            self.position.x = player.position.x - 100 * player.direction # Se téléporte dans le dos du joeur
            self.position.y = player.position.y
            self.rect.midbottom = (self.position.x, self.position.y)
            self.face_player(player_rect)
            self.current_attack = self.ATK_MELEE
            self.enter_state(self.ATTACKING)
            return
        
        if elapsed >= 1500:
            #Fin du cocon sans etre frappé
            self.is_shielded = False
            self.enter_state(self.TELEPORTING)

    #ATTAQUES
    def attack_melee(self, elapsed):
        self.current_anim = "melee"
        charge = self.speed(600)
        if elapsed >= charge and not self.atk_spawned:

            self.spawn_attack_zone(
                x=self.rect.centerx + 20 * self.direction,
                y=self.rect.bottom - 100,
                width=70,
                height=100,
                attack_data={"damage": 1, "knockback_x": 40, "knockback_y": -10},
                image=None,
                duration=300
            )

            self.spawn_projectile(
                target_x=self.arene_rect.right if self.direction == 1 else self.arene_rect.left,
                target_y=self.rect.bottom -30,
                speed=self.speed(10, is_proj=True),
                width=50,
                height=30,
                damage=1,
                offset_x=self.direction * 50,
                offset_y=30,
                lifetime=9999,
                should_disappear_on_contact=False
            )
            self.atk_spawned = True
        
        if elapsed >= charge + 800:
            self.enter_state(self.TELEPORTING)

    def attack_arm(self, elapsed, player_rect):
        self.current_anim = "arm"
        charge = self.speed(500)
        if elapsed >= charge and not self.atk_spawned:  
            self.spawn_projectile(
                target_x=player_rect.centerx,
                target_y=player_rect.centery,
                speed=self.speed(8, is_proj=True),
                width=30,
                height=15,
                damage=1,
                offset_x=self.direction * 60,
                offset_y=-30
            )
            self.atk_spawned = True
        
        if elapsed >= charge + 800:
            self.enter_state(self.TELEPORTING)

    def attack_laser(self, elapsed, head):
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
                    image=None,
                    duration=9999
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