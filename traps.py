import pygame

class Spike :
    def __init__(self, x, y):
        super().__init__()
    # Charger une image de spike
        self.sheet = pygame.image.load("insecte_sheet2.png").convert_alpha()
        self.image = pygame.transform.scale(self.sheet, (40, 40))
        self.rect = self.image.get_rect(topleft=(x,y))

        self.attack_data = {
            "damage" : 1,
            "knockback_x" : 0,
            "knockback_y" : 0
        }
