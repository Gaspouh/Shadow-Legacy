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

MAP_NAME = ["swamp", "terre_aride", "cave", "cave", "forest"]

MAP_PATHS = {
    MAP_NAME[0]: "map_swamp.tmx",
    MAP_NAME[1]: "ascension.tmx",
    MAP_NAME[2]: "cave.tmx",
    MAP_NAME[3]: "boss_arene.tmx",
    MAP_NAME[4]: "Parcours.tmx"
}

# spawns
DEFAULT_SPAWNS = {
    MAP_NAME[0]: {"x": 100, "y": 100},
    MAP_NAME[1]: {"x": 10, "y": 1200},
    MAP_NAME[2]: {"x": 100, "y": 100},
    MAP_NAME[3]: {"x": 1000, "y": 1000},
    MAP_NAME[4]: {"x": 200, "y": 700}
}   # Position de spawn par défaut selon la map (si aucun checkpoint activé)

def load_config():
    """Charge les stats de base depuis config.json"""
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)
    
def get_saved_map():
    """prend juste la map sauvegardée et son nom pour apres charger la bonne map """
    if not os.path.exists(SAVE_FILE):
        return MAP_NAME[0] # fallback si pas de save (map du début)
    
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)

    return data.get("current_map_name"), data.get("current_map")


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

    data = {    # on modifiera perso.py, abilities.py, et autres fichiers pour qu'ils dependent du json et pas l'inverse
        # player
        "current_map_name": map_name,
        "current_map": MAP_PATHS.get(map_name, "map_swamp.tmx"), # fallback avec la map swamp au cas ou
        "player": {
            "health": player.health,      
            "max_health": player.max_health,
            "orbs": Monnaie.orbs,
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



"""
class joueur_assis():
    is_sitting = False
    # Pour gérer l'état du joueur quand il est sur un banc
    def __init__(self):
        self.current_checkpoint = None
        # Animation :
        self.seated_idle = 'Assets/Player/seated1.png'

    def sit_on_bench(self, player, checkpoint):
        # Déclence l'animation assise et save
        is_sitting = True
        self.current_checkpoint = checkpoint
        checkpoint.activated = True
        sauvegarder(player, checkpoint, map)

"""