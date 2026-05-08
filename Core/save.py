import json
import os
import pygame
from World.objets import Monnaie

# Path
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(CORE_DIR, "save.json")
CONFIG_FILE = os.path.join(CORE_DIR, "config.json")
DEFAULT_SAVE = os.path.join(CORE_DIR, "default_save.json")

# Dico des maps à mettre à jour

MAP_NAME = ["swamp", "terre_aride", "cave", "forest", "hollow_earth"]

MAP_PATHS = {
    "swamp": "map_swamp.tmx",
    "terre_aride": "ascension.tmx",
    "cave": "cave.tmx",
    "forest":"forest.tmx",
    "hollow_earth": "hollow_earth.tmx",
    "parcours": "Parcours.tmx"
}

TMX_TO_FOLDER = {
    "map_swamp.tmx": "swamp",
    "ascension.tmx": "terre_aride",
    "cave.tmx": "cave",
    "boss_arene.tmx": "cave",
    "Parcours.tmx": "forest",
    "forest.tmx": "forest",
    "gravelion_arene.tmx": "cave",
    "hollow_earth.tmx": "hollow_earth"
}

# facilite l'utilisationn du parallax
MAP_PARALLAX_LAYERS = {
    "swamp": 5,
    "terre_aride": 5,
    "cave": 3,
    "boss_arene":0,
    "forest":5,
    "hollow_earth": 2
}

# spawns
DEFAULT_SPAWNS = {
    "swamp":{"x": 100, "y": 100},
    "terre_aride": {"x": 10,  "y": 1200},
    "cave": {"x": 100, "y": 100},
    "forest": {"x": 100, "y": 100},
    "parcours": {"x": 500, "y": 1000},
    "hollow_earth": {"x": 500, "y": 2450}
}
# Position de spawn par défaut selon la map (si aucun checkpoint activé)

def load_config():
    """Charge les stats de base depuis config.json"""
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)
    
def get_saved_map():
    """prend juste la map sauvegardée et son nom pour apres charger la bonne map """
    if not os.path.exists(SAVE_FILE):
        return MAP_NAME[0], MAP_PATHS[MAP_NAME[0]]  # fallback swamp
    
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)

    name = data.get("current_map_name")
    tmx = data.get("current_map")
    # a cause de certains pb de save, on met en minuscule
    if name:
        name = name.lower()

    #swamp par defaut
    if name not in MAP_PATHS:
        name = MAP_NAME[0]
        tmx = MAP_PATHS[name]

    return name, tmx


def get_spawn_from_checkpoints(checkpoints, map_path):
    dernier_checkpoint_actif = None
    for cp in checkpoints:
        if cp.activated:
            dernier_checkpoint_actif = cp   # dernier checkpoint acivé trouvé

    if dernier_checkpoint_actif:
        return pygame.math.Vector2(dernier_checkpoint_actif.rect.x, dernier_checkpoint_actif.rect.y)
    else:
        spawn = DEFAULT_SPAWNS.get(map_path, {"x": 100, "y": 100})
        return pygame.math.Vector2(spawn["x"], spawn["y"])
    
def get_player_equipped_charms():
    """Retourne les charms équipés du joueur"""
    if not os.path.exists(SAVE_FILE):
        return None

    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    
    return data.get("player", {}).get("equipped_charms", None)

def get_player_found_charms():
    """Retourne les charms équipés du joueur"""
    if not os.path.exists(SAVE_FILE):
        return None

    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    
    return data.get("player", {}).get("found_charms", None)


def sauvegarder(player, checkpoints, map_name, index_last_checkpoint=None):
    # Sauvegarder l'état du jeu dans un fichier json
    spawn = get_spawn_from_checkpoints(checkpoints, map_name)
    safe_map_name = map_name.lower() if map_name else "swamp"
    tmx_file = MAP_PATHS.get(safe_map_name, MAP_PATHS["swamp"])

    data = {    # on modifiera perso.py, abilities.py, et autres fichiers pour qu'ils dependent du json et pas l'inverse
        # player
        "current_map_name": map_name,
        "current_map_name": map_name.lower() if map_name else "swamp", # fallback avec la map swamp au cas ou
        "current_map": tmx_file,
        "player": {
            "health": player.health,      
            "max_health": player.max_health,
            "orbs": Monnaie.orbs,
            "minerais": player.minerais,
            "réceptacles": player.receptacles,
            "receptacles_total": player.receptacles_total,
            "found_charms" : get_player_found_charms(),
            "equipped_charms": get_player_equipped_charms()
        },
    
        # spawn
        "spawn_point": {
            "x": spawn.x,
            "y": spawn.y
        },

        # abilities
        "abilities": {
            # *
        },

        # bancs
        "checkpoints": [
            {
                "activated": cp.activated,
                "x": cp.rect.x,   # on sauvegarde aussi la position
                "y": cp.rect.y
            }
            for cp in checkpoints
        ],
        "last_checkpoint": index_last_checkpoint
        
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)
    print("saved")

    
def charger(player, checkpoints, map):
    """Pour load le json et mettre à jour les données du joueur"""

    if not os.path.exists(SAVE_FILE):
        return pygame.math.Vector2(DEFAULT_SPAWNS[map]["x"], DEFAULT_SPAWNS[map]["y"]) # si y'a pas de save : spawn par défaut

    with open(SAVE_FILE, "r") as f:
        data = json.load(f)

    # Player
    player.health = data["player"]["health"]
    player.max_health = data["player"]["max_health"]

    if "orbs" in data["player"]:
        Monnaie.orbs = data["player"]["orbs"]
    else:
        data["player"]["orbs"] = Monnaie.orbs
    
    if "minerais" in data["player"]:
        player.minerais = data["player"]["minerais"]
    else:
        data["player"]["minerais"] = player.minerais

    if "réceptacles" in data["player"]:
        player.receptacles = data["player"]["réceptacles"]
    else:
        data["player"]["réceptacles"] = player.receptacles
    
    if "receptacles_total" in data["player"]:
        player.receptacles_total = data["player"]["receptacles_total"]
    else:        
        data["player"]["receptacles_total"] = player.receptacles_total

    # Abilities
        # quand y'aura d'autres abilities

    # Checkpoints
    for i, cp in enumerate(checkpoints):
        if i < len(data["checkpoints"]):
            cp.activated = data["checkpoints"][i]["activated"]

    last_checkpoint_index = data.get("last_checkpoint")
    if last_checkpoint_index is not None and last_checkpoint_index < len(checkpoints):
        # Renvoie le dernier banc avec la pos des coordonnées
        return pygame.math.Vector2(checkpoints[last_checkpoint_index].rect.x, checkpoints[last_checkpoint_index].rect.y)

    # On recalcule depuis les checkpoints rechargés (pour etre sur)
    spawn_point = get_spawn_from_checkpoints(checkpoints, map)
    return spawn_point


def supprimer_sauvegarde():
    """Supprime la sauvegarde pour une nouvelle game par exemple"""
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
        print("save deleted")

def save_backup():
    """ Permet de créer un save.json si le fichier n'existe pas """
    if not os.path.exists(SAVE_FILE):
        try:
            with open(DEFAULT_SAVE, "r") as f_default:
                default_data = json.load(f_default)
            
            with open(SAVE_FILE, "w") as f_save:
                json.dump(default_data, f_save, indent=4)
            
            print("New save")
            return True
        except Exception as e:
            print("error")
            return False


def charms_images():
    """ Image associée à chaque charme """
    
    path = "Assets/charms"
    charms_assets = {
        "attack_long_range" : path + "/attack_long_range.png",
        "attack_speed" : path + "/attack_speed.png",
        "jump_boost" : path + "/jump_boost.png"
    }

    """
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    chrm = data.get("player", {}).get("found_charms", {})
    """
    
    return charms_assets

def get_chunks_params():
    """ prend les parametres de chunk """
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    return data.get("chunks", 5)


def buy_charm(charm_name, price):
    """ gestion de charms, dans save pour gestion plus facile du json """

    buy_sound = pygame.mixer.Sound("Assets/sounds/buy_item.mp3")
    buy_sound.set_volume(0.5)

    error_sound = pygame.mixer.Sound("Assets/sounds/error.mp3")
    error_sound.set_volume(0.3)

    if Monnaie.orbs >= price and charm_name:
        Monnaie.orbs -= price            
        found_charms = get_player_found_charms() or {charm_name: False}
        if found_charms.get(charm_name) != True:  # True = trouvé
            # MAJ du json
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            data["player"]["found_charms"][charm_name] = True   # charms est trouvé et ajouté
        
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f, indent=4)
            
            buy_sound.play()
            return " Charm acheté "

        else:
            error_sound.play()
            Monnaie.orbs += price  # faut bien rembourser si le joueur achete un charm qu'il a deja
            print("Vous possédez déjà ce charme.")
            return "Vous possédez déjà ce charme."

    else:
        error_sound.play()
        print("Pas assez d'Orbs ....")
        return "Pas assez d'Orbs ...."
