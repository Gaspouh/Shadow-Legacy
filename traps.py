import pygame

class Spike :
    def __init__(self, x, y):
        super().__init__()
    # Charger une image de spike
        self.sheet = pygame.image.load("coeur.png").convert_alpha()
        self.image = pygame.transform.scale(self.sheet, (40, 40))
        self.rect = self.image.get_rect(topleft=(x,y))

    def handle_collision(self, player):
        now = pygame.time.get_ticks()
        player.invincible = True
        player.invincibility_timer = now
        player.health -= 1 # Réduire la santé du joueur lorsqu'il est touché
        player.stun_timer = now
        player.stun_duration = 500

        if player.health > 0:
            player.position = pygame.math.Vector2(player.last_safe_position.x, player.last_safe_position.y)
            player.velocity = pygame.math.Vector2(0, 0)
            player.rect.midbottom = player.position
