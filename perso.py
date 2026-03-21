import pygame 
from player_abilities import Dash, Double_jump
from save import load_config

# PARAMETRES MONDE
GRAVITY = 0.4
FRICTION = -0.5
ACCELERATION = 2.5

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, fenetre):
        super().__init__()
        self.window = fenetre

        
        p = load_config().get("player", {}) if load_config() else {}
        
        # STATS DU JOUEUR
        self.health = p.get("health", 5) # Le 2eme argument est un fallback au cas ou la clé n'existe pas dans le json
        self.max_health = p.get("max_health", 5)
        self.attack = p.get("attack", 1)
        self.jump_strength = p.get("jump_strength", -14)

        # PHYSIQUE DU JOUEUR
        self.direction = 1 # 1 pour droite, -1 pour gauche
        self.position = pygame.math.Vector2(x, y) 
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)

        # VARIABLES DE GESTION DU SAUT A INITIALISER
        self.on_ground = False
        self.is_jumping = False
        self.coyote_timer = -1000
        self.jump_buffer_timer = -1000

        # VARIABLES DE GESTION DE L'ATTAQUE A INITIALISER
        self.is_attacking = False
        self.attack_duration = p.get("attack_duration", 100)
        self.attack_timer = 0
        self.attack_cooldown = p.get("attack_cooldown", 350)
        self.last_attack_time = -1000
        self.attack_direction = None #"UP", "DOWN", "RIGHT" ou "LEFT"

        # HITBOX ET IMAGE DU JOUEUR
        self.rect = pygame.Rect(x, y, 60, 90)
        original_image = pygame.image.load('player.png').convert_alpha()
        self.image = pygame.transform.scale(original_image, (75, 90))
        self.attack_rect = pygame.Rect(0, 0, 0, 0) # Hitbox de l'attaque initialisée vide

        # invincibilité après avoir été touché
        self.invincible = False
        self.invincibility_duration = p.get("invincibility_duration", 2000) # Durée de l'invincibilité 
        self.invincibility_timer = 0

        # blocage des touches pendant recul apres avoir été touché
        self.stun_timer = 0
        self.stun_duration = p.get("stun_duration", 100) # Durée pendant laquelle les touches sont bloquées

        #abilités du personnage
        self.dash = Dash()
        self.double_jump = Double_jump()

        #dernier sol si collision avec pique
        self.last_safe_position = pygame.math.Vector2(x,y)
        self.safe_position_timer = 0

        # Variables sable mouvant
        self.quicksand_timer = 0
        self.quicksand_sink = 0

    def update(self, platforms):
        self.acceleration = pygame.math.Vector2(0, GRAVITY)
        now = pygame.time.get_ticks()

        # Variables de ralentissement
        self.current_slow_factor = 1
        self.current_jump_factor = 1

        # Variables de vent
        self.wind_force_x = 0
        self.wind_force_y = 0

        # Variable de sable mouvant
        self.in_quicksand = False

        if self.on_ground and not self.in_quicksand and now - self.safe_position_timer > 500:  # enregistrement du dernier sol safe (toutes les 500ms pour éviter les surcharge de données)
            self.last_safe_position = pygame.math.Vector2(self.position.x, self.position.y)
            self.safe_position_timer = now

        is_stunned = now - self.stun_timer < self.stun_duration # Vérifier si le joueur est encore en état de stun
        if not is_stunned:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_q]and not keys[pygame.K_d]:
                self.acceleration.x = -ACCELERATION
                self.direction = -1
            elif keys[pygame.K_d] and not keys[pygame.K_q]:
                self.acceleration.x = ACCELERATION
                self.direction = 1

            self.acceleration.x += self.velocity.x * FRICTION 
            self.velocity.x += self.acceleration.x * self.current_slow_factor
            self.velocity.y += self.acceleration.y

            # Gestion du vent
            if not self.on_ground :
                self.velocity.x += self.wind_force_x
            else :
                self.velocity.x += self.wind_force_x * 0.2
            self.velocity.y += self.wind_force_y

            # Limiter la vitesse de chute du joueur sauf en cas de dash vers le bas
            if self.velocity.y > 20 and not self.dash.in_use: 
                self.velocity.y = 20

            # Gestion sable mouvant (ATTENTION NE FOCNTIONNE PAS)

            if self.in_quicksand :
                self.quicksand_timer += 1

                if self.quicksand_timer > 30 :

                    self.quicksand_sink = min(40, self.quicksand_sink + 0.2)

                    self.current_slow_factor *= 0.97

                if self.quicksand_sink >=  40:
                    self.health -= 1
                    self.position = self.last_safe_position.copy()
                    self.velocity = pygame.math.Vector2(0,0)
                    self.rect.midbottom = self.position
                    self.in_quicksand = False

            else:
                self.quicksand_timer = 0
                self.quicksand_sink = 0

            # COLLISION HORIZONTALE (AXE X)

            self.position.x += self.velocity.x + 0.5 * self.acceleration.x
            self.rect.centerx = self.position.x

            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.velocity.x > 0: # Se déplace vers la droite
                        self.rect.right = platform.rect.left
                    elif self.velocity.x < 0: # Se déplace vers la gauche
                        self.rect.left = platform.rect.right
                    self.position.x = self.rect.centerx
                    self.velocity.x = 0 # Arrêter le mouvement horizontal en cas de collision

            # COLLISION VERTICALE (AXE Y)

            self.position.y += self.velocity.y + 0.5 * self.acceleration.y
            self.rect.bottom = self.position.y

            self.on_ground = False
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.velocity.y > 0:  # Se déplace vers le bas
                        self.rect.bottom = platform.rect.top
                        self.on_ground = True
                        self.is_jumping = False
                        self.velocity.y = 0
                        self.double_jump.reset()  # Recharger le double saut
                    elif self.velocity.y < 0:  # Se déplace vers le haut
                        self.rect.top = platform.rect.bottom
                        self.velocity.y = 0
                    self.position.y = self.rect.bottom

            # GESTION DES TIMERS (COYOTE TIME ET JUMP BUFFER)
            now = pygame.time.get_ticks()

            if self.on_ground:
                self.coyote_timer = now # Réinitialiser le timer de coyote lorsque le joueur est au sol

            can_jump = now - self.coyote_timer <= 150
            want_to_jump = now - self.jump_buffer_timer <= 150

            if want_to_jump and self.quicksand_sink < 5:
                if can_jump:
                    self.execute_jump(jump_type="simple") # Exécuter le saut si le jump buffer est actif (c-à-d que le joeur a préssé le bouton de saut) et que le joueur peut sauter (c-à-d que le joueur est dans la fenêtre de coyote time)
                elif self.double_jump.can_execute(self):
                    self.execute_jump(jump_type="double")

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
            
            if self.invincible:
                now = pygame.time.get_ticks()
                if now - self.invincibility_timer >= self.invincibility_duration: # Si la durée d'invincibilité est écoulée
                    self.invincible = False

            self.dash.update(self) # Mettre à jour l'état du dash et appliquer les effets de dash sur le joueur
            
        else:
            self.acceleration.x = 0 # Ne pas permettre au joueur de se déplacer pendant le stun

    def press_jump(self):

        self.jump_buffer_timer = pygame.time.get_ticks() # Enregistrer le moment où le bouton de saut est préssé

        if self.in_quicksand:
            self.position.y -= 5
            self.quicksand_sink = max(0, self.quicksand_sink - 5)

    def execute_jump(self, jump_type="simple"):
            self.on_ground = False
            self.is_jumping = True
            
            if jump_type == "simple" :
                self.velocity.y = self.jump_strength * self.current_jump_factor
            elif jump_type == "double" :
                self.velocity.y = self.double_jump.strength
                self.double_jump.used =True

            self.coyote_timer = -1000 # Réinitialisation des timers pour ne pas sauter 2 fois
            self.jump_buffer_timer = -1000

    def stop_jump(self):
        if self.is_jumping and self.velocity.y < 0:
            self.velocity.y = 0
            self.is_jumping = False
    
    #GESTION DE L'ATTAQUE
    def press_attack(self):
        now = pygame.time.get_ticks()
        if not self.is_attacking and now - self.last_attack_time >= self.attack_cooldown:
            keys = pygame.key.get_pressed()
            self.is_attacking = True
            self.attack_timer = now
            self.last_attack_time = now
            self.ennemis_touches = [] # On vide la liste dpour ne pas toucher plusieurs fois le même ennemi avec une seule attaque

            if keys[pygame.K_z]: # Attaque vers le haut
                self.attack_direction = "UP"
            elif keys[pygame.K_s] and not self.on_ground: # Attaque vers le bas uniquement si le joueur est en l'air
                self.attack_direction = "DOWN"
            else:
                if self.direction == 1:
                    self.attack_direction = "RIGHT"
                else:
                    self.attack_direction = "LEFT"
    
    def take_damage(self, attack_data, source_rect, source):
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
        else : #si c'est un ennemi
            if source_rect.centerx > self.rect.centerx:
                knockback_direction = -1
            else :
                knockback_direction = 1
            self.velocity.x = attack_data["knockback_x"] * knockback_direction # Reculer le joueur dans la direction opposée à laquelle il fait face lorsqu'il est touché
            self.velocity.y = attack_data["knockback_y"]  # faire sauter légerement le joueur si touché

        return hitstop_duration, shake_amount



