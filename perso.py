import pygame 
pygame.init()

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

        self.position = pygame.math.Vector2(x, y) 
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)

        self.on_ground = False
        self.is_jumping = False
        self.jump_button_pressed = False
        self.coyote_timer = -1000
        self.jump_buffer_timer = -1000

        # HITBOX
        self.rect = pygame.Rect(x, y, 60, 90)
        original_image = pygame.image.load('player.png').convert_alpha()
        self.image = pygame.transform.scale(original_image, (75, 90))

    def update(self, platforms):
        self.acceleration = pygame.math.Vector2(0, GRAVITY)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]and not keys[pygame.K_RIGHT]:
            self.acceleration.x = -ACCELERATION
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            self.acceleration.x = ACCELERATION

        self.acceleration.x += self.velocity.x * FRICTION
        self.velocity += self.acceleration

        if self.velocity.y > 10:
            self.velocity.y = 10

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
        
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
    

