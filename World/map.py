import pygame
import pytmx
from World.traps import *

TILE_SIZE = 32

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

class Special_Platform(Platform):
    def __init__(self, x, y, image, effect=None, slow_factor = 1, jump_factor = 1):
        super().__init__(x, y, image)
        self.effect = effect
        self.slow_factor = slow_factor
        self.jump_factor = jump_factor    
        
        width = image.get_width()
        height = image.get_height()

        if effect == "mud":
            self.surface = Platform(x, y + 5, pygame.Surface((width, 5)))
            
        elif effect =="ice" :
           self.surface = Platform(x, y + 1, pygame.Surface((width, 5)))

        else :
            self.surface = None

class Map_Object(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x,y))

class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        scale_x = scale_y = 85
        self.image = pygame.image.load('Assets/Images/banc.png')  # sans fill
        self.image = pygame.transform.scale(self.image, (scale_x, scale_y))  # adapter la taille
        self.rect = self.image.get_rect(topleft=(x, y))
        self.activated = False  # devient True quand le joueur passe dessus

        #pygame.draw.rect(self.image, (0, 255, 0), self.image.get_rect(), 2) # hitbox pour test du gameplay

class SpawnPoint: #L'endoit ou le joeur spawn apres un changement de salle
    def __init__(self, x, y, name):
        self.position = pygame.math.Vector2(x, y)
        self.name = name #Pour différencier les spawn ponit d'une meme salle
    
# Arène de Gravelion (après les plateformes existantes)

"""arene_platforms = [
    Platform(5000,    600,  1000,    20,  (80, 80, 80)),   # sol
    Platform(6000,      0,    20,   600,  (80, 80, 80)),   # mur droit
    Platform(5000,      0,  1000,    20,  (80, 80, 80)),   # plafond
]"""

arene_rect = pygame.Rect(5000, 0, 1000, 600)  # délimitation de l'arène

def load_map(path):
    tmx_data = pytmx.load_pygame(path, pixelalpha=True)
    return tmx_data

def create_map(tmx_data):
    platforms = []
    special_platforms = []
    traps = []

    decorations = []
    checkpoints = []
    spawnpoints = []
    entities_to_spawn = []

    for layer in tmx_data.visible_layers:
        if not hasattr(layer, 'data'):
             continue

        for x, y, gid in layer: 
            if gid == 0: #Si la tuile est vide
                continue

            props = tmx_data.get_tile_properties_by_gid(gid)
            image = tmx_data.get_tile_image_by_gid(gid)

            if image is None or props is None:
                continue

            tile_type = props.get("type")

            pos_x = x * TILE_SIZE
            pos_y = y * TILE_SIZE

            #Platformes classiques
            if tile_type == "ground":
                platforms.append(Platform(pos_x, pos_y, image))

            #Platformes spéciales
            elif tile_type == "quicksand":
                sp = Special_Platform(pos_x, pos_y, image, effect="quicksand")
                special_platforms.append(sp)

            elif tile_type == "mud":
                sp = Special_Platform(pos_x, pos_y, image, effect="mud", slow_factor=0.5, jump_factor=0.6)
                special_platforms.append(sp)

            elif tile_type == "ice":
                special_platforms.append(
                    Special_Platform(pos_x, pos_y, image, effect="ice")
                )

            #Pièges
            elif tile_type == "lava": #'198, 69, 36) - 1
                traps.append(Lava(pos_x, pos_y, TILE_SIZE))
                    
            elif tile_type == "acid": #(30, 110, 80) - 2
                traps.append(Acid(pos_x, pos_y, TILE_SIZE))
                    
            elif tile_type == "thorns":
                direction = props.get("direction")
                traps.append(Thorns(pos_x, pos_y, TILE_SIZE, direction))

            elif tile_type == "spike":
                direction = props.get("direction")
                traps.append(Spike(pos_x, pos_y, TILE_SIZE, direction))

            elif tile_type == "wind":
                pass

            elif tile_type == "saw":
                traps.append(Saw(pos_x, pos_y, TILE_SIZE//2))

    for obj in tmx_data.objects:
        obj_type = obj.properties.get("obj_type")
        image = getattr(obj, "image")

        x = int(obj.x)
        y = int(obj.y)

        if obj_type == "decor":
            decorations.append(Map_Object(x, y, image))
        
        else:
            y = int (y - obj.height*2)
            if obj_type == "banc":
                checkpoints.append(Checkpoint(x, y))

            elif obj_type == "spawnpoint":
                name = obj.name
                spawnpoints.append(SpawnPoint(x, y, name))

            elif obj_type == "mob":
                name = obj.name
                entities_to_spawn.append({
                    "type": "mob",
                    "name": name,
                    "x": x,
                    "y": y
                })

            elif obj_type == "boss":
                name = obj.name
                entities_to_spawn.append({
                    "type": "boss",
                    "name": name,
                    "x": x,
                    "y": y
                })


    return platforms, special_platforms, traps, decorations, checkpoints, spawnpoints, entities_to_spawn

