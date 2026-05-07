import os
import pygame
import pytmx
from Entities.boss_wolf_black import Black_Wolf
from World.traps import *
from Entities.ennemi import Araignee, Volant, Fighter, Chargeur, Tourelle
from Entities.boss_logic import Golem
from World.objets import Receptacle
from Entities.boss_wolf_red import Red_Wolf
from Entities.boss_gravelion import Gravelion
from Core.save import get_chunks_params
from Entities.npc_logic import Gordon_NPC, Forgeron

TILE_SIZE = 32
RENDU_CHUNCK = get_chunks_params() # pareil, mais pour les collisions et autres, la valeur c'est la taille d'un coté du carré (en tile) qui sont calculé

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

class Special_Platform(Platform):
    def __init__(self, x, y, image, effect=None, slow_factor=1, jump_factor=1):
        super().__init__(x, y, image)
        self.effect = effect
        self.slow_factor = slow_factor
        self.jump_factor = jump_factor    
        
        width = image.get_width()

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

class SpawnPoint: #L'endroit ou le joeur spawn apres un changement de salle
    def __init__(self, x, y, name):
        self.position = pygame.math.Vector2(x, y)
        self.name = name #Pour différencier les spawn point d'une meme salle
    
class Door:
    def __init__(self, x, y, width, height, target_map, target_spawn):
        self.rect = pygame.Rect(x, y, width, height)
        self.target_map = target_map
        self.target_spawn = target_spawn

# Arène de Gravelion (après les plateformes existantes)

"""arene_platforms = [
    Platform(5000,    600,  1000,    20,  (80, 80, 80)),   # sol
    Platform(6000,      0,    20,   600,  (80, 80, 80)),   # mur droit
    Platform(5000,      0,  1000,    20,  (80, 80, 80)),   # plafond
]"""

arene_rect = pygame.Rect(5000, 0, 1000, 600)  # délimitation de l'arène

class Map_Manager:
    def __init__(self):
        self.current_map = None

    def load_map(self, path):
        tmx_data = pytmx.load_pygame((path), pixelalpha=True)

        self.map_width = tmx_data.width * TILE_SIZE
        self.map_height = tmx_data.height * TILE_SIZE
        
        self.platforms, self.special_platforms, self.traps, self.decorations, \
            self.checkpoints, self.spawnpoints, self.doors, self.entities_to_spawn, self.objets, = create_map(tmx_data)
        
        background_folder = os.path.join(os.path.dirname(path), "Background") 
        
        self.nb_parallax_layers = len([fichier for fichier in os.listdir(background_folder) if fichier != "0.png"])
    def spawn_entities(self, fenetre):
        araignee, volant, golem, chargeur, tourelle, fighter, blackwolf, redwolf, gravelion, gordon, forgeron = [], [], [], [], [], [], [], [], [], [], []

        for e in self.entities_to_spawn:
            if e["type"] == "mob":
                if e["name"] == "araignee":
                    araignee.append(Araignee(fenetre, e["x"], e["y"]))
                elif e["name"] == "volant":
                    volant.append(Volant(fenetre, e["x"], e["y"]))
                elif e["name"] == "golem":
                    golem.append(Golem(fenetre, e["x"], e["y"]))
                elif e["name"] == "chargeur":
                    chargeur.append(Chargeur(fenetre, e["x"], e["y"]))
                elif e["name"] == "tourelle":
                    tourelle.append(Tourelle(fenetre, e["x"], e["y"]))
                elif e["name"] == "fighter":
                    fighter.append(Fighter(fenetre, e["x"], e["y"]))
                elif e["name"] == "blackwolf":
                    blackwolf.append(Black_Wolf(fenetre, e["x"], e["y"]))
                elif e["name"] == "redwolf":
                    redwolf.append(Red_Wolf(fenetre, e["x"], e["y"]))
                elif e["name"] == "gravelion":
                    gravelion.append(Gravelion(fenetre, e["x"], e["y"], arene_rect))

            elif e["type"] == "npc":
                if e["name"] == "gordon":
                    gordon.append(Gordon_NPC(fenetre, e["x"], e["y"]))
                elif e["name"] == "forgeron":
                    forgeron.append(Forgeron(fenetre, e["x"], e["y"]))
                    
        liste_entites = araignee + volant + golem + chargeur + tourelle + fighter + blackwolf + redwolf + gravelion + gordon + forgeron
        return liste_entites
    
    def get_spawn(self, name):
        return self.spawnpoints.get(name)
    

def create_map(tmx_data):
    platforms = []
    special_platforms = []
    traps = []

    objets = []
    decorations = []
    checkpoints = []
    doors = []
    entities_to_spawn = []

    spawnpoints = {}

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
            
            elif tile_type == "decor":
                decorations.append(Map_Object(pos_x, pos_y, image))

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
        image = getattr(obj, "image", None)

        x = int(obj.x)
        y = int(obj.y)

        if obj_type == "decor":
            decorations.append(Map_Object(x, y, image))
        
        elif obj_type == "banc":
            y = int (y - obj.height)
            checkpoints.append(Checkpoint(x, y))
        
        elif obj_type == "receptacle":
            y = int(y - obj.height)
            objets.append(Receptacle(x, y))
        
        elif obj_type == "spawnpoint":
            name = obj.name
            spawnpoints[name] = (SpawnPoint(x, y, name))

        elif obj_type == "door":
            target_map = obj.properties.get("target_map")
            target_spawn = obj.properties.get("target_spawn")
            doors.append(Door(x, y, obj.width, obj.height, target_map, target_spawn))

        elif obj_type == "mob":
            name = obj.name
            entities_to_spawn.append({
                "type": "mob",
                "name": name,
                "x": x,
                "y": y
            })

        elif obj_type == "npc":
            name = obj.name
            entities_to_spawn.append({
                "type": "npc",
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

    return platforms, special_platforms, traps, decorations, checkpoints, spawnpoints, doors, entities_to_spawn, objets

def chunck_zone(platforms):
    zone = {}
    for i in platforms:
        x = i.rect.x // (TILE_SIZE*RENDU_CHUNCK)
        y = i.rect.y// (TILE_SIZE*RENDU_CHUNCK)
        if (x,y) not in zone: # si pas de platforme ds le chunck on créer une liste (pour apres ajouter les platsformes)
            zone[(x,y)] = []
        zone[(x,y)].append(i)
    return zone

def platforme_la_plus_proche(zone, rect):
    x = rect.centerx // (TILE_SIZE*RENDU_CHUNCK)
    y = rect.centery // (TILE_SIZE*RENDU_CHUNCK)
    proche = []
    # check les 9 chunks autour du joueur et avoir les platformes les plus proche
    for i in (-1,0,1):
        for j in (-1,0,1):
            if (x+i,y+j) in zone:
                proche.extend(zone[(x+i,y+j)])
    return proche