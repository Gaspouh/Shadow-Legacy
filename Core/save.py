import json
import os
import pygame
from World.objets import Monnaie

# Path constants : use relative paths from Core directory
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(CORE_DIR, "save.json")
CONFIG_FILE = os.path.join(CORE_DIR, "config.json")

# Spawn
DEFAULT_SPAWNS = {
    "terre_aride": {"x": 10, "y": 1200},
    "swamp": {"x": 100, "y": 100}
} # Position de spawn par défaut selon la map (si aucun checkpoint activé)

def load_config():
    """Charge les stats de base depuis config.json"""
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)
    
def get_spawn_from_checkpoints(checkpoints, map):
    """
    Retourne la position du dernier checkpoint activé dans checkpoints[]
    """
    dernier_checkpoint_actif = None
    for cp in checkpoints:
        if cp.activated:
            dernier_checkpoint_actif = cp  # on prend le dernier de la liste activé

    if dernier_checkpoint_actif:
        return pygame.math.Vector2(dernier_checkpoint_actif.rect.x, dernier_checkpoint_actif.rect.y)
    else:
        return pygame.math.Vector2(DEFAULT_SPAWNS[map]["x"], DEFAULT_SPAWNS[map]["y"])
    
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


def sauvegarder(player, checkpoints, map):
    # Sauvegarder l'état du jeu dans un fichier json
    spawn = get_spawn_from_checkpoints(checkpoints, map)

    data = {    # on modifiera perso.py, abilities.py, et autres fichiers pour qu'ils dependent du json et pas l'inverse
        # player
        "player": {
            "health": player.health,      
            "max_health": player.max_health,
            "orbs": Monnaie.orbs,
            "found_charms"   : get_player_found_charms(),
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
        ]
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)
    print(f"[SAVE] Sauvegarde effectuée, spawn : ({spawn.x}, {spawn.y})")

    
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

    # On recalcule depuis les checkpoints rechargés (pour etre sur)
    spawn_point = get_spawn_from_checkpoints(checkpoints, map)
    return spawn_point


def supprimer_sauvegarde():
    """Supprime la sauvegarde pour une nouvelle game par exemple"""
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
        print("save deleted")



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