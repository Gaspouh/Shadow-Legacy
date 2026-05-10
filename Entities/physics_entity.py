import pygame


class PhysicsEntity:
    def __init__(self, x, y, width, height, gravity=0.4, friction=-0.5, use_gravity=True):

        # Création hitbox de l'entité
        self.rect = pygame.Rect(x, y, width, height)

        # Initilisation vecteurs pour la physique
        self.position = pygame.math.Vector2(self.rect.centerx, self.rect.bottom)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)

        # Initialisation variables pour la physique
        self.gravity = gravity
        self.friction = friction
        self.use_gravity = use_gravity
        self.on_ground = False

    def apply_physics(self):

        """Applique la physique et met à jour la position et la vitesse de l'entité, en gérant collisions et frottements.
        Entrées: aucune.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.acceleration.x = 0
        self.acceleration.y = 0

        if self.use_gravity:  # Gravité
            self.acceleration.y = self.gravity
        else:
            self.acceleration.y += self.velocity.y * self.friction

        self.acceleration.x += self.velocity.x * self.friction
        self.velocity += self.acceleration

        # Seuil d'arrêt horizontal
        if abs(self.velocity.x) < 0.1:
            self.velocity.x = 0

        if self.velocity.y > 20:  # Limite vitesse de chute
            self.velocity.y = 20

    def move_horizontal(self, platforms):

        # Déplacement entité
        """Applique la physique et met à jour la position et la vitesse de l'entité, en gérant collisions et frottements.
        Entrées: platforms.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.position.x += self.velocity.x + 0.5 * self.acceleration.x
        self.rect.centerx = self.position.x

        # Collision entité
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity.x > 0:  # Se déplace vers la droite
                    self.rect.right = platform.rect.left

                elif self.velocity.x < 0:  # Se déplace vers la gauche
                    self.rect.left = platform.rect.right

                self.position.x = self.rect.centerx
                self.velocity.x = 0  # Arrêter le mouvement horizontal en cas de collision

    def move_vertical(self, platforms):

        # Déplacement entité
        """Applique la physique et met à jour la position et la vitesse de l'entité, en gérant collisions et frottements.
        Entrées: platforms.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.position.y += self.velocity.y + 0.5 * self.acceleration.y
        self.rect.bottom = self.position.y

        # Collision entité
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity.y > 0:  # Se déplace vers le bas
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True

                elif self.velocity.y < 0:  # Se déplace vers le haut
                    self.rect.top = platform.rect.bottom

                self.position.y = self.rect.bottom
                self.velocity.y = 0  # Arreter le mouvement vertical en cas de

    def physics_update(self, platforms):

        """Met à jour l'état de l'entité en appliquant la logique temporelle, collisions et transitions d'état.
        Entrées: platforms.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.apply_physics()
        self.move_horizontal(platforms)
        self.move_vertical(platforms)
