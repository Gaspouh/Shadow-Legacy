import pygame

#Images toutes mises a insecte_sheet2.png pour éviter les problemes de chemin d'acces impossible
class Rectangular_Obstacle():
    def __init__(self, x, y, width, height, damage, image_path):

        # Image du piège
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))

        # Hitbox du piège
        self.rect = self.image.get_rect(topleft=(x, y))

        # Dégats des pièges
        self.attack_data = {
            "damage" : damage,
            "knockback_x" : 0,
            "knockback_y" : 0
        }

        # Caractéristiques générales des pièges
        self.ignore_invincibility = True
        self.respawn_on_touch = False
        self.apply_knockback = False

        # Caractéristique spécifique au piège
        self.special_effect = None

        # Cooldown des dégats périodiques (pour l'eau glacée)
        self.damage_cooldown = 0
        self.last_damage_time = 0

        # Ralentissement (pour la boue et le sable mouvant)
        self.slow_factor = 1
        self.jump_factor = 1

        # Forces externes (pour le vent)
        self.force_x = 0
        self.force_y = 0

class Spike(Rectangular_Obstacle):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, 1, "Assets/Images/insecte_sheet2.png")

        self.respawn_on_touch = True
        self.apply_knockback = True

class Thorns(Rectangular_Obstacle):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, 1, "Assets/Images/insecte_sheet2.png")

        self.respawn_on_touch = True

class Lava(Rectangular_Obstacle):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, 2, "Assets/Images/insecte_sheet2.png")

        self.respawn_on_touch = True

class Acid(Rectangular_Obstacle):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, 1, "Assets/Images/insecte_sheet2.png")

        self.respawn_on_touch = True

class Wind_Horizontal(Rectangular_Obstacle):
    def __init__(self, x, y, width, height, force):
        super().__init__(x, y, width, height, 0, "Assets/Images/insecte_sheet2.png")

        self.special_effect = "wind"

        self.force_x = force

class Wind_Vertical(Rectangular_Obstacle):
    def __init__(self, x, y, width, height, force):
        super().__init__(x, y, width, height, 0, "Assets/Images/insecte_sheet2.png")

        self.special_effect = "wind"
        self.force_y = force

class Saw :
    def __init__(self, x, y, radius):
        super().__init__()
    # Charger une image de scie circulaire
        self.sheet = pygame.image.load("Assets/Images/insecte_sheet2.png").convert_alpha()
        self.image = pygame.transform.scale(self.sheet, (radius*2, radius*2))
        

        self.attack_data = {
            "damage" : 1,
            "knockback_x" : 0,
            "knockback_y" : 0
        }

class Retractable_spike :
    pass

class Falling_rock :
    pass