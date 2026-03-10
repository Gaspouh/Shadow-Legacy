class Spike :
    def __init__(self):
    # Charger une image de spike
        """self.sheet = pygame.image.load(sprite_sheet).convert_alpha()"""
        self.is_spike = True

    def last_ground(self, player):
        if player.on_ground():
            self.direction = player.direction
            self.last_pos = player.position 

    def reset (self, player):
        player.position.y = self.position.y 
        player.position.x = self.position.x - 20 * self.direction 
        player.health -= 1
