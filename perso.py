import pygame 
pygame.init()
from player_abilities import Dash

# PARAMETRES MONDE
GRAVITY = 0.4
FRICTION = -0.5
ACCELERATION = 2.5

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, fenetre):
        super().__init__()
        self.window = fenetre
        self.window.fill((200, 200, 200))

        # STATS DU JOUEUR
        self.health = 5
        self.max_health = 5
        self.attack = 8
        self.jump_strength = -14

        # PHYSIQUE DU JOUEUR
        self.direction = 1 # 1 pour droite, -1 pour gauche
        self.position = pygame.math.Vector2(x, y) 
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)

        # VARIABLES DE GESTION DU SAUT A INITIALISER
        self.on_ground = False
        self.is_jumping = False
        self.jump_button_pressed = False
        self.coyote_timer = -1000
        self.jump_buffer_timer = -1000

        # VARIABLES DE GESTION DE L'ATTAQUE A INITIALISER
        self.is_attacking = False
        self.attack_duration = 100
        self.attack_timer = 0
        self.attack_cooldown = 350
        self.last_attack_time = -1000
        self.attack_direction = None #"UP", "DOWN", "RIGHT" ou "LEFT"
        self.hitstop_timer = 0
        self.screen_shake_timer = 0

        # HITBOX ET IMAGE DU JOUEUR
        self.rect = pygame.Rect(x, y, 60, 90)
        original_image = pygame.image.load('player.png').convert_alpha()
        self.image = pygame.transform.scale(original_image, (75, 90))
        self.attack_rect = pygame.Rect(0, 0, 0, 0) # Hitbox de l'attaque initialisée vide

        # invincibilité après avoir été touché
        self.invincible = False
        self.invincibility_duration = 2000 # Durée de l'invincibilité 
        self.invincibility_timer = 0

        # blocage des touches pendant recul apres avoir été touché
        self.stun_timer = 0
        self.stun_duration = 100 # Durée pendant laquelle les touches sont bloquées

        #abilités du personnage
        self.dash = Dash()


    def update(self, platforms):
        self.acceleration = pygame.math.Vector2(0, GRAVITY)
        time = pygame.time.get_ticks()

        istunned = time - self.stun_timer < self.stun_duration # Vérifier si le joueur est encore en état de stun
   
        if not istunned:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_q]and not keys[pygame.K_d]:
                self.acceleration.x = -ACCELERATION
                self.direction = -1
            elif keys[pygame.K_d] and not keys[pygame.K_q]:
                self.acceleration.x = ACCELERATION
                self.direction = 1

            self.acceleration.x += self.velocity.x * FRICTION
            self.velocity += self.acceleration

            if self.velocity.y > 15: # Limiter la vitesse de chute du joueur
                self.velocity.y = 15

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
                    if self.velocity.y > 0: # Se déplace vers le bas
                        self.rect.bottom = platform.rect.top
                        self.on_ground = True
                        self.is_jumping = False
                        self.velocity.y = 0
                    elif self.velocity.y < 0: # Se déplace vers le haut
                        self.rect.top = platform.rect.bottom
                        self.velocity.y = 0
                    self.position.y = self.rect.bottom

            # GESTION DES TIMERS (COYOTE TIME ET JUMP BUFFER)
            now = pygame.time.get_ticks()

            if self.on_ground:
                self.coyote_timer = now # Réinitialiser le timer de coyote lorsque le joueur est au sol
            can_jump = now - self.coyote_timer <= 150
            want_to_jump = now - self.jump_buffer_timer <= 150
            if can_jump and want_to_jump:
                self.execute_jump() # Exécuter le saut si le jump buffer est actif (c-à-d que le joeur a préssé le bouton de saut) et que le joueur peut sauter (c-à-d que le joueur est dans la fenêtre de coyote time)
                if not self.jump_button_pressed:
                    self.stop_jump()

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
                time = pygame.time.get_ticks()
                if time - self.invincibility_timer >= self.invincibility_duration: # Si la durée d'invincibilité est écoulée
                    self.invincible = False

            self.dash.update(self) # Mettre à jour l'état du dash et appliquer les effets de dash sur le joueur
            
        else:
            self.acceleration.x = 0 # Ne pas permettre au joueur de se déplacer pendant le stun

    def press_jump(self):
        self.jump_button_pressed = True
        self.jump_buffer_timer = pygame.time.get_ticks() # Enregistrer le moment où le bouton de saut est préssé

    def execute_jump(self):
            self.on_ground = False
            self.is_jumping = True
            self.velocity.y = self.jump_strength # Appliquer du saut

            self.coyote_timer = -1000 # Réinitialisation des timers pour ne pas sauter 2 fois
            self.jump_buffer_timer = -1000

    def release_jump(self):
        self.jump_button_pressed = False
        self.stop_jump() # Appeler la fonction pour arrêter le saut lorsque le bouton de saut est relâché

    def stop_jump(self):
        if self.is_jumping and self.velocity.y < 0:
            self.velocity.y = 0
            self.is_jumping = False

    def press_dash(self):
        self.dash.start_dash(self)
    
    #GESTION DE L'ATTAQUE
    def press_attack(self):
        now = pygame.time.get_ticks()
        if not self.is_attacking and now - self.last_attack_time >= self.attack_cooldown:
            keys = pygame.key.get_pressed()
            self.is_attacking = True
            self.attack_timer = now
            self.last_attack_time = now
            self.ennemis_touches = [] # On vide la liste dpour ne pas toucher plusieurs fois le même ennemi avec une seule attaque
            print ("SLASH !") # A remplacer par le son de l'attaque et l'animation d'attaque

            if keys[pygame.K_z]: # Attaque vers le haut
                self.attack_direction = "UP"
            elif keys[pygame.K_s] and not self.on_ground: # Attaque vers le bas uniquement si le joueur est en l'air
                self.attack_direction = "DOWN"
            else:
                if self.direction == 1:
                    self.attack_direction = "RIGHT"
                else:
                    self.attack_direction = "LEFT"
    
    def toucher(self, player_rect, ennemi_rect):
        if not self.invincible:
            time = pygame.time.get_ticks()
            self.invincible = True
            self.invincibility_timer = time
            self.stun_timer = time
            self.health -= 1 # Réduire la santé du joueur lorsqu'il est touché

            if player_rect.centerx > ennemi_rect.centerx:
                recul_direction = 1 # Reculer vers la gauche si le joueur est à droite de l'ennemi
            else:
                recul_direction = -1
            self.velocity.x = 90 * recul_direction # Reculer le joueur dans la direction opposée à laquelle il fait face lorsqu'il est touché
            self.velocity.y = -4 # faire sauter légerement le joueur si touché




