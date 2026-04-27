import pygame 
import random
from Entities.player_abilities import Dash, Double_jump, sort
from Core.save import load_config
from Entities.physics_entity import PhysicsEntity
from Visual.sprite_sheet import VerticalAnimation
from Visual.vfx import Fade

class Player(PhysicsEntity):
    def __init__(self, x, y, fenetre):
        super().__init__(x, y, 25, 60, gravity=0.4 , friction=-0.5, use_gravity=True)
        self.window = fenetre

        p = load_config().get("player", {}) if load_config() else {}
        
        # STATS DU JOUEUR
        self.health = p.get("health", 5) # Le 2eme argument est un fallback au cas ou la clé n'existe pas dans le json
        self.max_health = p.get("max_health", 5)
        self.attack = p.get("attack", 1)
        self.jump_strength = p.get("jump_strength", -14)
        self.pogo_strength = p.get("pogo_strength", -10)
        self.max_speed = p.get("max_speed", 10)
        self.speed = p.get("speed", 3)
        self.sang = 0
        self.sang_max = 99
        self.is_sitting = False

        # PHYSIQUE DU JOUEUR
        self.direction = 1 # 1 pour droite, -1 pour gauche

        # VARIABLES DE GESTION DU SAUT A INITIALISER
        self.is_jumping = False
        self.coyote_timer = -1000
        self.jump_buffer_timer = -1000

        # VARIABLES DE GESTION DE L'ATTAQUE A INITIALISER
        self.is_attacking = False
        self.attack_duration = p.get("attack_duration", 100)
        self.attack_timer = 0
        self.attack_cooldown = p.get("attack_cooldown", 350)
        self.last_attack_time = -1000
        self.attack_knockback_x = p.get("attack_knockback_x", 80)
        self.attack_knockback_y = p.get("attack_knockback_y", -5)
        self.attack_direction = None #"UP", "DOWN", "RIGHT" ou "LEFT"
        self.attack_rect = pygame.Rect(0, 0, 0, 0) # Hitbox de l'attaque initialisée vide
        self.crit_chance = p.get("crit_chance", 0.02)
        self.entite_touches = []
        self.attack_data = {}
        self.tir_touches = [] # Liste des entités déjà touchées par ce sort pour éviter de les toucher plusieurs fois

        # INVINCIBILITE
        self.invincible = False
        self.invincibility_duration = p.get("invincibility_duration", 2000) # Durée de l'invincibilité 
        self.invincibility_timer = 0

        # STUN
        self.stun_timer = 0
        self.stun_duration = 150 # Durée pendant laquelle les touches sont bloquées

        # ABILITIES
        self.dash = Dash()
        self.double_jump = Double_jump()
        self.sort = sort()

        # SAFE POSITION
        self.last_safe_position = pygame.math.Vector2(x,y)
        self.safe_position_timer = 0

        # EFFETS SURFACE
        self.quicksand_timer = 0
        self.quicksand_sink = 0
        self.in_quicksand = False
        self.current_slow_factor = 1
        self.current_jump_factor = 1
        self.wind_force_x = 0
        self.wind_force_y = 0
        self.on_ice = False

        self.respawn_on_touch = False

        # Spriteheets animations :

        # idle
        self.anim_idle = VerticalAnimation(fenetre, x, y, 'Assets/Player/idle.png',        57, 500, 500, 0, 0)
        self.anim_jump_air_right = VerticalAnimation(fenetre, x, y, 'Assets/Player/jump_air_right.png', 12, 500, 500, 0, 0)
        self.anim_jump_air_left = VerticalAnimation(fenetre, x, y, 'Assets/Player/jump_air_left.png', 12, 500, 500, 0, 0)

        # déplacement
        self.anim_run_right = VerticalAnimation(fenetre, x, y, 'Assets/Player/run_right.png',  16, 500, 500, 0, 0)
        self.anim_run_left = VerticalAnimation(fenetre, x, y, 'Assets/Player/run_left.png',   16, 500, 500, 0, 0)

        # jump
        self.anim_jump_front = VerticalAnimation(fenetre, x, y, 'Assets/Player/jump.png', 12, 500, 500, 0, 0)
        self.anim_jump_right = VerticalAnimation(fenetre, x, y, 'Assets/Player/jump_right.png', 12, 500, 500, 0, 0)
        self.anim_jump_left = VerticalAnimation(fenetre, x, y, 'Assets/Player/jump_left.png', 12, 500, 500, 0, 0)
        
        # attaque
        self.anim_basic_attack1_right = VerticalAnimation(fenetre, x, y, 'Assets/Player/basic_attack1_right.png', 10, 500, 500, 0, 0)
        self.anim_basic_attack2_right = VerticalAnimation(fenetre, x, y, 'Assets/Player/basic_attack2_right.png', 10, 500, 500, 0, 0)
        self.anim_basic_attack1_left = VerticalAnimation(fenetre, x, y, 'Assets/Player/basic_attack1_left.png', 10, 500, 500, 0, 0)
        self.anim_basic_attack2_left = VerticalAnimation(fenetre, x, y, 'Assets/Player/basic_attack2_left.png', 10, 500, 500, 0, 0)

        # Banc (pas une anim)
        self.seated_idle = VerticalAnimation(fenetre, x, y, 'Assets/Player/seated1.png', 1, 345, 345, 0, 0)


        self.basic_attacks_right = [
        self.anim_basic_attack1_right,
        self.anim_basic_attack2_right
        ]

        self.basic_attacks_left = [
        self.anim_basic_attack1_left,
        self.anim_basic_attack2_left
        ]

        """
        self.anim_basic_attack3 = VerticalAnimation(fenetre, x, y, 'Assets/Player/basic_attack3.png', 10, 500, 500, 0, 0)
        """
        # dash
        self.anim_dash_right = VerticalAnimation(fenetre, x, y, 'Assets/Player/dash_right.png', 15, 500, 500, 0, 0)
        self.anim_dash_left = VerticalAnimation(fenetre, x, y, 'Assets/Player/dash_left.png', 15, 500, 500, 0, 0)

        v = 60  # Vitesse par défaut pour chaque anim

        self.anim_idle.vitesse_animation = 57 / v / 3 # Plus lent
        self.anim_run_right.vitesse_animation = 16 / v * 1.9 # Plus rapide
        self.anim_run_left.vitesse_animation = 16 / v * 1.9
        self.anim_jump_front.vitesse_animation = 12 / v * 3
        self.anim_jump_right.vitesse_animation = 20 / v
        self.anim_jump_left.vitesse_animation = 20 / v
        self.anim_dash_right.vitesse_animation = 12 / v * 4
        self.anim_dash_left.vitesse_animation = 12 / v * 4
        self.anim_basic_attack1_right.vitesse_animation = 10 / v * 3.2
        self.anim_basic_attack1_left.vitesse_animation = 10 / v * 3.2
        self.anim_basic_attack2_right.vitesse_animation = 10 / v * 3.2
        self.anim_basic_attack2_left.vitesse_animation = 10 / v * 3.2
        self.seated_idle.vitesse_animation = 1 # image
        self.sprite_offset_y = 25

    # foret de if pour chaque anims
    def animate(self):
        # dash
        if self.is_stunned:
            self.current_animation = self.anim_idle
        elif self.dash.in_use and self.direction == 1:
            self.current_animation = self.anim_dash_right
        elif self.dash.in_use and self.direction == -1:
            self.current_animation = self.anim_dash_left
        # attack (direction deja gérée dans press_attack)
        elif self.is_attacking:
            self.current_animation = self.current_attack_anim
        # jump / air idle (ai_jump)
        elif self.is_jumping and self.velocity.x == 0:
            self.current_animation = self.anim_jump_front
        elif self.is_jumping and self.direction == 1:
            self.current_animation = self.anim_jump_right
        elif self.is_jumping and self.direction == -1:
            self.current_animation = self.anim_jump_left
        elif not self.on_ground and self.velocity.y > 0 and self.direction == 1:
            self.current_animation = self.anim_jump_air_right
        elif not self.on_ground and self.velocity.y > 0 and self.direction == -1:
            self.current_animation = self.anim_jump_air_left
        elif self.is_sitting:
            self.current_animation = self.seated_idle
        
        elif abs(self.velocity.x) > 4: # Seuil de vitesse pour declencher l'anim
            if self.direction == 1: #droite
                self.current_animation = self.anim_run_right # l'animation en cours
            else:
                self.current_animation = self.anim_run_left
        else:
            self.current_animation = self.anim_idle # Si le joueur bouge pas il est en idle
        
        self.current_animation.gestion_animation() # De sprite_sheet.py pour faire l'animation
        
        frame_index = int(self.current_animation.index_image)
        frame_surface = self.current_animation.frames_droite[frame_index]
        
        # image du joueur redimmensionnée
        if self.current_animation in (self.anim_run_right, self.anim_run_left):
            self.image = pygame.transform.scale(frame_surface, (110, 110)) # Perso plus petit lors du run (à cause du pb de "pading" de chaque tiles du spritesheet)
        
        else:
            self.image = pygame.transform.scale(frame_surface, (115, 115))

    def update(self, platforms):
        now = pygame.time.get_ticks()

        if self.on_ground and not self.in_quicksand and now - self.safe_position_timer > 500:  # enregistrement du dernier sol safe (toutes les 500ms pour éviter les surcharge de données)
            self.last_safe_position = pygame.math.Vector2(self.position.x, self.position.y)
            self.safe_position_timer = now

        self.is_stunned = now - self.stun_timer < self.stun_duration # Vérifier si le joueur est encore en état de stun
        if not self.is_stunned:
            keys = pygame.key.get_pressed()

            if self.on_ice and self.on_ground :
                friction = self.friction / 30
                acceleration = self.speed / 6

            else :
                acceleration = self.speed
                friction = self.friction

            self.acceleration.x = 0
            self.acceleration.y = 0
            
            if self.is_sitting:
                if keys[pygame.K_q] or keys[pygame.K_d]:
                    self.is_sitting = False  # se lève en bougeant
            else:
                if keys[pygame.K_q] and not keys[pygame.K_d]:
                    self.acceleration.x -= acceleration
                    self.direction = -1

                elif keys[pygame.K_d] and not keys[pygame.K_q]:
                    self.acceleration.x += acceleration
                    self.direction = 1

            self.acceleration.x += self.velocity.x * friction

            self.acceleration.y = self.gravity

            self.velocity.x += self.acceleration.x
            self.velocity.y += self.acceleration.y

            # Caps de vitesse appliqué hors dash
            if not self.dash.in_use:
                # Limiter vitesse hozitontal du joueur
                if self.velocity.x < -self.max_speed:
                    self.velocity.x += (-self.max_speed - self.velocity.x) / 15
                elif self.velocity.x > self.max_speed:
                    self.velocity.x += (self.max_speed - self.velocity.x) / 15
                # Limiter la vitesse de chute du joueur     
                if self.velocity.y > 20:
                    self.velocity.y = 20
                # Seuil d'arrêt horizontal
                if abs(self.velocity.x) < 0.01:
                    self.velocity.x = 0
                if self.velocity.y > 0:
                    self.is_jumping = False

            # Gestion du vent
            if not self.on_ground :
                self.velocity.x += self.wind_force_x
            else :
                self.velocity.x += self.wind_force_x * 0.2
            self.velocity.y += self.wind_force_y

            # Gestion sable mouvant
            if self.in_quicksand:

                self.quicksand_sink = min(80, self.quicksand_sink + 0.5)

                # Vitesse de chute limitée à l'enfoncement (le joueur descend lentement)
                self.velocity.y = min(self.velocity.y, 0.3)  # tombe très lentement

                # Ralentissement lié à la profondeur
                self.current_slow_factor = 1 - self.quicksand_sink / 65
                self.velocity.x *= self.current_slow_factor  # ralentissement horizontal progressif

                if self.quicksand_sink >= 62:
                    self.health -= 1
                    self.position = self.last_safe_position.copy()
                    self.velocity = pygame.math.Vector2(0, 0)
                    self.rect.midbottom = self.position
                    self.in_quicksand = False
                    self.quicksand_sink = 0
                    self.quicksand_timer = 0
            else:
                self.quicksand_timer = 0
                self.quicksand_sink = 0
                self.velocity.x *= self.current_slow_factor

            # Déplacements et collisions
            self.move_horizontal(platforms)
            self.move_vertical(platforms)

            # GESTION DES TIMERS (COYOTE TIME ET JUMP BUFFER)
            now = pygame.time.get_ticks()

            if self.on_ground or self.in_quicksand:
                self.coyote_timer = now # Réinitialiser le timer de coyote lorsque le joueur est au sol
                self.double_jump.reset()

            can_jump = now - self.coyote_timer <= 150
            want_to_jump = now - self.jump_buffer_timer <= 150

            if want_to_jump and self.quicksand_sink < 3:
                if can_jump:
                    self.execute_jump(jump_type="simple") # Exécuter le saut si le jump buffer est actif (c-à-d que le joeur a préssé le bouton de saut) et que le joueur peut sauter (c-à-d que le joueur est dans la fenêtre de coyote time)
                elif self.double_jump.can_execute(self):
                    self.execute_jump(jump_type="double")

            # ATTAQUE
            now = pygame.time.get_ticks()
    
            if self.is_attacking:
                if now - self.attack_timer >= self.attack_duration: # Si la durée de l'attaque est écoulée
                    self.is_attacking = False
                    self.attack_rect = pygame.Rect(0, 0, 0, 0) # Réinitialiser la hitbox de l'attaque lorsque l'attaque est terminée
                
                else :
                    if self.attack_direction == "UP":
                        self.attack_rect = pygame.Rect(self.rect.centerx - 20, self.rect.top - 70, 50, 70)
                    elif self.attack_direction == "DOWN":
                        self.attack_rect = pygame.Rect(self.rect.centerx - 20, self.rect.bottom, 50, 70)
                    else : #direction "RIGHT" ou "LEFT"
                        if self.attack_direction == "RIGHT": # Attaque vers la droite
                            self.attack_rect = pygame.Rect(self.rect.right, self.rect.centery - 20, 70, 50)
                        else: # Attaque vers la gauche
                            self.attack_rect = pygame.Rect(self.rect.left - 70, self.rect.centery - 20, 70, 50)
            
            # INVINCIBILITE
            if self.invincible:
                now = pygame.time.get_ticks()
                if now - self.invincibility_timer >= self.invincibility_duration: # Si la durée d'invincibilité est écoulée
                    self.invincible = False

            self.dash.update(self) # Mettre à jour l'état du dash et appliquer les effets de dash sur le joueur
            self.animate() # Joueur
            
        else:
            self.acceleration.x = 0 # Ne pas permettre au joueur de se déplacer pendant le stun
            self.animate() # Forcer l'idle

    def press_jump(self):
        self.is_sitting = False # Si joueur assis et saute il se leve
        now = pygame.time.get_ticks()
        
        self.jump_buffer_timer = pygame.time.get_ticks() # Enregistrer le moment où le bouton de saut est préssé

        if self.in_quicksand:
            self.position.y -= 10
            self.quicksand_sink = max(0, self.quicksand_sink - 10)

    def execute_jump(self, jump_type="simple"):
            self.on_ground = False
            self.is_jumping = True
            
            if jump_type == "simple" :
                self.velocity.y = self.jump_strength * self.current_jump_factor
            elif jump_type == "double" :
                self.velocity.y = self.double_jump.strength
                self.double_jump.used =True # Flag

            self.coyote_timer = -1000 # Réinitialisation des timers pour ne pas sauter 2 fois
            self.jump_buffer_timer = -1000

    def stop_jump(self):
        if self.is_jumping and self.velocity.y < 0:
            self.velocity.y = 0
            self.is_jumping = False
    
    #GESTION DE L'ATTAQUE
    def press_attack(self):
        self.is_sitting = False # Si joueur assis et attaque il se leve
        now = pygame.time.get_ticks()
        if not self.is_attacking and now - self.last_attack_time >= self.attack_cooldown:
            keys = pygame.key.get_pressed()
            self.is_attacking = True
            self.attack_timer = now
            self.last_attack_time = now
            self.entite_touches = [] # On vide la liste pour ne pas toucher plusieurs fois le même ennemi avec une seule attaque
            # Choix d'animation d'attaque
            if self.direction == 1:
                self.current_attack_anim = random.choice(self.basic_attacks_right)
            else:
                self.current_attack_anim = random.choice(self.basic_attacks_left)

            self.anim_basic_attack1_right.index_image = 0 # Reset l'anim a chaque attaques

            if keys[pygame.K_z]: # Attaque vers le haut
                self.attack_direction = "UP"
            elif keys[pygame.K_s] and not self.on_ground: # Attaque vers le bas uniquement si le joueur est en l'air
                self.attack_direction = "DOWN"
            else:
                if self.direction == 1:
                    self.attack_direction = "RIGHT"
                else:
                    self.attack_direction = "LEFT"
        
        self.attack_data = {
            "damage" : self.attack,
            "knockback_x" : self.attack_knockback_x,
            "knockback_y" : self.attack_knockback_y,
            "critical": random.random() < self.crit_chance
        }

    def attack_feedback(self, target):
        
        if not target.apply_knockback:
            return
        
        if self.attack_direction == "DOWN": 
            self.velocity.y = self.pogo_strength # Rebondir vers le haut après une attaque vers le bas
            self.double_jump.reset()
        
        elif self.attack_direction == "UP": # Pour avoir un léger ressenti sans écraser le joeur au sol
            if self.velocity.y < 0:
                self.velocity.y *= 0.5
        else :
            if self.direction == 1: # Reculer vers la droite
                self.velocity.x = -self.attack_knockback_x
            else: # Reculer vers la gauche
                self.velocity.x = self.attack_knockback_x

            self.velocity.y = self.attack_knockback_y

    
    def take_damage(self, attack_data, source_rect, source, fade=None):
        now = pygame.time.get_ticks()

        if self.invincible and not source.ignore_invincibility:
            return 0, 0
        
        damage_amount = attack_data["damage"]

        self.health -= damage_amount # Réduire la santé du joueur lorsqu'il est touché

        self.invincible = True
        self.invincibility_timer = now
        self.stun_timer = now

        if damage_amount == 2:
            hitstop_duration = 200
            shake_amount = 10
        elif damage_amount == 1:
            hitstop_duration = 100
            shake_amount = 5

        if source.respawn_on_touch:
            if self.health > 0:
                self.position = self.last_safe_position.copy()
                self.velocity = pygame.math.Vector2(0, 0)
                self.rect.midbottom = self.position
                self.stun_duration = 1200
                fade.start("wait", 3, 300)

        else : #si c'est un ennemi
            self.stun_duration = 100
            if source_rect.centerx > self.rect.centerx:
                knockback_direction = -1
            else :
                knockback_direction = 1
            self.velocity.x = attack_data["knockback_x"] * knockback_direction # Reculer le joueur dans la direction opposée à laquelle il fait face lorsqu'il est touché
            self.velocity.y = attack_data["knockback_y"]  # faire sauter légerement le joueur si touché

        return hitstop_duration, shake_amount
    
