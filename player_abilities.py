import pygame

class Dash:
    def __init__(self):
        self.vitesse_dash = 100
        self.duree = 100
        self.cooldown = 1000

        self.in_use = False
        self.dash_timer = 0
        self.last_dash = -1000

    def start_dash(self, player):
        now = pygame.time.get_ticks()
        if not self.in_use and now - self.last_dash >= self.cooldown:
            self.in_use = True
            self.dash_timer = now
            self.last_dash = now
            return True
        return False
    
    def update(self, player):
        if self.in_use:
            now = pygame.time.get_ticks()
            if now - self.dash_timer > self.duree:
                self.in_use = False
                player.velocity.x *= 0.5 # Ralentir le joueur après le dash
            else:
                player.velocity.x = self.vitesse_dash * player.direction # Appliquer la vitesse de dash dans la direction du joueur
                player.velocity.y = 0 # Ne pas permettre au joueur de monter ou descendre pendant le dash
                player.position.y = player.rect.bottom
    
    