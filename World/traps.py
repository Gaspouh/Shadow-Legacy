import pygame
from Visual.sprite_sheet import Animation


class Rectangular_Obstacle:
    def __init__(
        self,
        x,
        y,
        size,
        damage,
        image_path,
        hitbox_size_mult=(1, 1),
        hitbox_offset=(0, 0),
        direction="up",
        animation=False,
    ):

        # Image du piège
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        self.image_rect = self.image.get_rect(topleft=(x, y))

        # Rotation asset pour piques et ronces
        if direction != "up":
            if direction == "down":
                self.image = pygame.transform.rotate(self.image, 180)

            if direction == "left":
                self.image = pygame.transform.rotate(self.image, 90)

            if direction == "right":
                self.image = pygame.transform.rotate(self.image, -90)

        # Animation de l'image #Pour liquides
        if animation:
            self.animation = Animation(None, x, y, image_path, 16, 16, 16, 0, 0, scale=2)
        else:
            self.animation = None

        # Hitbox du piège
        cx, cy = hitbox_size_mult
        dx, dy = hitbox_offset

        self.rect = pygame.Rect(x + dx, y + dy, size * cx, size * cy)

        # Dégats des pièges
        self.attack_data = {"damage": damage, "knockback_x": 0, "knockback_y": 0}

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

    def update(self):
        """Met à jour les animations de la carte, avance les frames et gère les transitions entre animations.
        Entrées: aucune.
        Sortie: Aucune valeur renvoyée (None).
        """
        if self.animation:
            self.image = self.animation.gestion_animation()


class Spike(Rectangular_Obstacle):
    def __init__(self, x, y, size, direction="up"):

        if direction == "up":
            hitbox_offset = (0, size // 2)
            hitbox_size_mult = (1, 0.5)

        elif direction == "down":
            hitbox_offset = (0, 0)
            hitbox_size_mult = (1, 0.5)

        elif direction == "left":
            hitbox_offset = (size // 2, 0)
            hitbox_size_mult = (0.5, 1)

        elif direction == "right":
            hitbox_offset = (0, 0)
            hitbox_size_mult = (0.5, 1)

        else:
            hitbox_offset = (0, size // 2)
            hitbox_size_mult = (1, 0.5)
            direction = "up"

        super().__init__(
            x,
            y,
            size,
            1,
            "Assets/Traps/spike.png",
            hitbox_size_mult,
            hitbox_offset,
            direction,
        )

        self.respawn_on_touch = True
        self.apply_knockback = True


class Thorns(Rectangular_Obstacle):
    def __init__(self, x, y, size, direction="up"):
        if direction == "up":
            hitbox_offset = (0, size // 2)
            hitbox_size_mult = (1, 0.5)

        elif direction == "down":
            hitbox_offset = (0, 0)
            hitbox_size_mult = (1, 0.5)

        elif direction == "left":
            hitbox_offset = (size // 2, 0)
            hitbox_size_mult = (0.5, 1)

        elif direction == "right":
            hitbox_offset = (0, 0)
            hitbox_size_mult = (0.5, 1)

        super().__init__(
            x,
            y,
            size,
            1,
            "Assets/Traps/thorns.png",
            hitbox_size_mult,
            hitbox_offset,
            direction,
        )

        self.respawn_on_touch = True


class Lava(Rectangular_Obstacle):
    def __init__(self, x, y, size):
        super().__init__(
            x,
            y,
            size,
            2,
            "Assets/Traps/lava.png",
            hitbox_size_mult=(1, 0.7),
            hitbox_offset=(0, size * 0.3),
            direction="up",
            animation=True,
        )

        self.respawn_on_touch = True


class Acid(Rectangular_Obstacle):
    def __init__(self, x, y, size):
        super().__init__(
            x,
            y,
            size,
            1,
            "Assets/Traps/acid.png",
            hitbox_size_mult=(1, 0.7),
            hitbox_offset=(0, size * 0.3),
            direction="up",
            animation=True,
        )

        self.respawn_on_touch = True


class Wind_Horizontal(Rectangular_Obstacle):
    def __init__(self, x, y, size, force):
        super().__init__(x, y, size, 0, "Assets/Images/insecte_sheet2.png")

        self.special_effect = "wind"

        self.force_x = force


class Wind_Vertical(Rectangular_Obstacle):
    def __init__(self, x, y, size, force):
        super().__init__(x, y, size, 0, "Assets/Images/insecte_sheet2.png")

        self.special_effect = "wind"
        self.force_y = force


class Saw(Rectangular_Obstacle):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius * 2, 1, "Assets/Images/scie.png")
        self.respawn_on_touch = True
        self.apply_knockback = True
