import pygame 
pygame.init()

# PARAMETRES MONDE
GRAVITY = 0.4
FRICTION = -0.15
ACCELERATION = 0.7

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, fenetre):
        super().__init__()
        self.window = fenetre
        self.window.fill((200, 200, 200))

        # STATS DU JOUEUR
        self.health = 5
        self.max_health = 5
        self.attack = 8

        self.position = pygame.math.Vector2(x, y) 
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)

        self.jump_strength = -10
        self.on_ground = False
        self.is_jumping = True

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

        # GESTION DES HITBOXS

        self.position.x += self.velocity.x + 0.5 * self.acceleration.x
        self.rect.centerx = self.position.x

        self.position.y += self.velocity.y + 0.5 * self.acceleration.y
        self.rect.bottom = self.position.y

        if self.velocity.y > 0:
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.rect.bottom <= platform.rect.top + self.velocity.y+2:
                        self.rect.bottom = platform.rect.top
                        self.position.y = self.rect.bottom
                        self.velocity.y = 0
                        self.on_ground = True
                        self.is_jumping = False

    def jump(self):
        if self.on_ground:
            self.on_ground = False
            self.is_jumping = True
            self.velocity.y = self.jump_strength
            self.rect.bottom = self.position.y

    def stop_jump(self):
        if self.is_jumping and self.velocity.y < 0:
            self.velocity.y *= 0.5
            self.is_jumping = False
        
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
    

