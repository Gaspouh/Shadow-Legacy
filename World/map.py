import pygame

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Special_Platform(Platform):
    def __init__(self, x, y, width, height, color, effect=None, slow_factor = 1, jump_factor = 1):
        super().__init__(x, y, width, height, color)
        self.effect = effect
        self.slow_factor = slow_factor
        self.jump_factor = jump_factor    

        if effect == "mud":
            marge = 10
        elif effect == "ice":
            marge = 1
        else :
            marge = 30
        
        if effect != "quicksand":
            self.surface = Platform(x,y, width, 5, color)
            self.rect = pygame.Rect(x, y - marge, width, height + marge)
        else :
            self.surface = None

platforms = [
    Platform(0, 500, 8000, 100, (100, 100, 100)),
    Platform(300, 350, 200, 20, (100, 100, 100)),
    Platform(500, 200, 200, 20, (100, 100, 100)),
    Platform(800, 0, 20, 350, (100, 100, 100)),
    Platform(1100, 300, 200, 20, (100, 100, 100))
]

special_platforms = [
    Special_Platform(2000, 400, 470, 150, (194, 178, 128), effect="quicksand"),  # même hauteur que le sol
    Special_Platform(3000, 400, 1500, 150, (200, 230, 255), effect="ice"),
    Special_Platform(2500, 400, 470, 150, (100, 80, 40),  effect="mud", slow_factor=0.5, jump_factor = 0.6)
]

class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        scale_x = scale_y = 85
        self.image = pygame.image.load('Assets/Images/banc.png')  # sans fill
        self.image = pygame.transform.scale(self.image, (scale_x, scale_y))  # adapter la taille
        self.rect = self.image.get_rect(topleft=(x, y))
        self.activated = False  # devient True quand le joueur passe dessus

        #pygame.draw.rect(self.image, (0, 255, 0), self.image.get_rect(), 2) # hitbox pour test du gameplay

checkpoints = [
    Checkpoint(600, 417),
    Checkpoint(1155, 217)
]

# Arène de Gravelion (après les plateformes existantes)
ARENE_X = 4000  # loin sur la map

arene_platforms = [
    Platform(ARENE_X,        400, 1200, 20,  (80, 80, 80)),   # sol
    #Platform(ARENE_X,        0,   20,   420, (80, 80, 80)),   # mur gauche
    Platform(ARENE_X + 1180, 0,   20,   420, (80, 80, 80)),   # mur droit
    Platform(ARENE_X,        0,   1200, 20,  (80, 80, 80)),   # plafond
]

arene_rect = pygame.Rect(ARENE_X, 0, 1200, 420)  # délimitation de l'arène

platforms += arene_platforms