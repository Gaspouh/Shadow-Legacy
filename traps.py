import pygame

#Images toutes mises a insecte_sheet2.png pour éviter les problemes de chemin d'acces impossible

class Spike :
    def __init__(self, x, y, side):
        super().__init__()
    # Charger une image de spike
        self.sheet = pygame.image.load("insecte_sheet2.png").convert_alpha()
        self.image = pygame.transform.scale(self.sheet, (side, side))
        self.rect = self.image.get_rect(topleft=(x,y))

        self.attack_data = {
            "damage" : 1,
            "knockback_x" : 0,
            "knockback_y" : 0
        }

class Lava :
    def __init__(self, x, y, lenght, height)
        super().__init__()
        self.image = pygame.Surface(lenght, height)
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.attack_data = {
            "damage" : 2,
            "knockback_x" : 0,
            "knockback_y" : 0
        }

class Acid :
    def __init__(self, x, y, lenght, height)
        super().__init__()
        self.image = pygame.Surface(lenght, height)
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.attack_data = {
            "damage" : 1,
            "knockback_x" : 0,
            "knockback_y" : 0
        }

class Thorns :
        def __init__(self, x, y):
        super().__init__()
    # Charger une image de ronce
        self.sheet = pygame.image.load("insecte_sheet2.png").convert_alpha()
        self.image = pygame.transform.scale(self.sheet, (40, 40))
        self.rect = self.image.get_rect(topleft=(x,y))

        self.attack_data = {
            "damage" : 1,
            "knockback_x" : 0,
            "knockback_y" : 0
        }

class Saw :
    def __init__(self, x, y, radius):
        super().__init__()
    # Charger une image de scie circulaire
        self.sheet = pygame.image.load("insecte_sheet2.png").convert_alpha()
        self.image = pygame.transform.scale(self.sheet, (radius*2, radius*2))
        self.

        self.attack_data = {
            "damage" : 1,
            "knockback_x" : 0,
            "knockback_y" : 0
        }