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

MAP_NAME = ["swamp", "terre_aride", "cave", "forest", "hollow_earth", "mines"]

MAP_PATHS = {
    "swamp": "map_swamp.tmx",
    "terre_aride": "ascension.tmx",
    "cave": "cave.tmx",
    "forest": "forest.tmx",
    "hollow_earth": "hollow_earth.tmx",
    "parcours": "Parcours.tmx",
    "parcours": "Parcours_2.tmx",
    "mines": "final_boss.tmx",
    "industrial": "gravelion_arene.tmx"
}

TMX_TO_FOLDER = {
    "map_swamp.tmx": "swamp",
    "ascension.tmx": "terre_aride",
    "cave.tmx": "cave",
    "boss_arene.tmx": "cave",
    "Parcours.tmx": "forest",
    "Parcours_2.tmx": "forest",
    "forest.tmx": "forest",
    "min_boss_arene.tmx": "cave",
    "hollow_earth.tmx": "hollow_earth",
    "final_boss.tmx": "mines",
    "gravelion_arene.tmx": "industrial"
}

# facilite l'utilisationn du parallax
MAP_PARALLAX_LAYERS = {
    "swamp": 5,
    "terre_aride": 5,
    "cave": 3,
    "boss_arene": 0,
    "forest": 5,
    "hollow_earth": 2,
    "mines": 1,
    "industrial": 5,
}

# spawns
DEFAULT_SPAWNS = {
    "swamp": {"x": 50, "y": 568},
    "terre_aride": {"x": 50, "y": 1197},
    "cave": {"x": 46, "y": 180},
    "forest": {"x": 42, "y": 600},
    "parcours": {"x": 300, "y": 1000},
    "parcours_2": {"x": 300, "y": 3500},
    "hollow_earth": {"x": 135, "y": 2290},
    "industrial" : {"x": 1500, "y": 150}
}
# Position de spawn par défaut selon la map (si aucun checkpoint activé)


def load_config():
    """Récupère et retourne des données depuis la sauvegarde ou la configuration pour de l'entité.
    Entrées: aucune.
    Sortie: Retourne le dico du json
    """
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def get_saved_map():
    """Récupère et retourne des données depuis la sauvegarde ou la configuration pour de l'entité.
    Entrées: aucune.
    Sortie: Renvoie les maps sauvegardées
    """
    if not os.path.exists(SAVE_FILE):
        return MAP_NAME[0], MAP_PATHS[MAP_NAME[0]]  # fallback swamp

    with open(SAVE_FILE, "r") as f:
        data = json.load(f)

    name = data.get("current_map_name")
    tmx = data.get("current_map")
    # a cause de certains pb de save, on met en minuscule
    if name:
        name = name.lower()

    # swamp par defaut
    if name not in MAP_PATHS:
        name = MAP_NAME[0]
        tmx = MAP_PATHS[name]

    return name, tmx


def get_spawn_from_checkpoints(checkpoints, map_path):
    """Calcule et retourne le point de spawn à utiliser pour de l'entité selon les checkpoints actifs.
    Entrées: checkpoints, map_path.
    Sortie: Retourne une valeur si applicable, sinon None.
    """
    dernier_checkpoint_actif = None
    for cp in checkpoints:
        if cp.activated:
            dernier_checkpoint_actif = cp  # dernier checkpoint acivé trouvé

    if dernier_checkpoint_actif:
        return pygame.math.Vector2(dernier_checkpoint_actif.rect.x, dernier_checkpoint_actif.rect.y)
    else:
        spawn = DEFAULT_SPAWNS.get(map_path, {"x": 100, "y": 100})
        return pygame.math.Vector2(spawn["x"], spawn["y"])


def get_player_equipped_charms():
    """Récupère et retourne des données depuis la sauvegarde ou la configuration pour de l'entité.
    Entrées: aucune.
    Sortie: Renvoie les charms équippé du joueur
    """
    if not os.path.exists(SAVE_FILE):
        return None

    with open(SAVE_FILE, "r") as f:
        data = json.load(f)

    return data.get("player", {}).get("equipped_charms", None)


def get_player_found_charms():
    """Récupère et retourne des données depuis la sauvegarde ou la configuration pour de l'entité.
    Entrées: aucune.
    Sortie: meme chose mais pour les charms trouvés du joueur
    """
    if not os.path.exists(SAVE_FILE):
        return None

    with open(SAVE_FILE, "r") as f:
        data = json.load(f)

    return data.get("player", {}).get("found_charms", None)


def get_player_unlocked_abilities():
    """Récupère et retourne des données depuis la sauvegarde ou la configuration pour de l'entité.
    Entrées: aucune.
    Sortie: pareil pour les abilités débloquée
    """
    if not os.path.exists(SAVE_FILE):
        return {"dash": False, "double_jump": False}
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    return data.get("abilities", {"dash": False, "double_jump": False})


def unlock_ability(ability_name):
    """Exécute la logique de la fonction unlock_ability liée à de l'entité, modifiant l'état ou produisant une action spécifique.
    Entrées: ability_name.
    Sortie: verifie la save
    """
    if not os.path.exists(SAVE_FILE):
        return
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    data["abilities"][ability_name] = True
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)


def sauvegarder(
    player,
    checkpoints,
    map_name,
    forgeron_instance=None,
    index_last_checkpoint=None,
    cadavre=None,
):
    # Sauvegarder l'état du jeu dans un fichier json
    """Sauvegarde l'état courant lié à de l'entité (player, checkpoints, objets) dans le fichier de sauvegarde.
    Entrées: player, checkpoints, map_name, forgeron_instance, index_last_checkpoint, cadavre.
    Sortie: modifie le json
    """
    spawn = get_spawn_from_checkpoints(checkpoints, map_name)
    safe_map_name = map_name.lower() if map_name else "swamp"
    tmx_file = MAP_PATHS.get(safe_map_name, MAP_PATHS["swamp"])

    # obtenir le spawn "global" (toutes map confondues)
    if index_last_checkpoint is not None:
        main_spawn = {"x": spawn.x, "y": spawn.y, "map": map_name}
    else:
        main_spawn = None
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                data_spawn = json.load(f)
            main_spawn = data_spawn.get("main_spawn")
        if main_spawn is None:
            main_spawn = {"x": spawn.x, "y": spawn.y, "map": map_name}

    if os.path.exists(
        SAVE_FILE
    ):  # pour ne pas écraser les objets ramassés, on vérifie d'abord ce qui est déjà dans le json
        with open(SAVE_FILE, "r") as f:
            old_data = json.load(f)

        taken_objects = old_data.get("taken_objects", [])
    else:
        taken_objects = []

    data = {  # on modifiera perso.py, abilities.py, et autres fichiers pour qu'ils dependent du json et pas l'inverse
        # player
        "current_map_name": map_name,
        "current_map_name": map_name.lower() if map_name else "swamp",  # fallback avec la map swamp au cas ou
        "current_map": tmx_file,
        "player": {
            "health": player.health,
            "max_health": player.max_health,
            "orbs": Monnaie.orbs,
            "minerais": player.minerais,
            "réceptacles": player.receptacles,
            "receptacles_total": player.receptacles_total,
            "found_charms": get_player_found_charms(),
            "equipped_charms": get_player_equipped_charms(),
            "upgrade_cost": forgeron_instance.upgrade_cost
            if forgeron_instance
            else 1,  # sauvegarde du coût d'amélioration du forgeron
            "orbs_cost": forgeron_instance.orb_cost
            if forgeron_instance
            else 100,  # sauvegarde du coût en orbs du forgeron
        },
        # spawn
        "spawn_point": {"x": spawn.x, "y": spawn.y},
        # abilities
        "abilities": get_player_unlocked_abilities(),
        # bancs
        "checkpoints": [
            {
                "activated": cp.activated,
                "x": cp.rect.x,  # on sauvegarde aussi la position
                "y": cp.rect.y,
            }
            for cp in checkpoints
        ],
        "last_checkpoint": index_last_checkpoint,
        # objets ramassés
        "taken_objects": taken_objects,
        # spawn global
        "main_spawn": main_spawn,
        "cadavre": {
            "map": cadavre.map_name,
            "x": cadavre.rect.centerx,
            "y": cadavre.rect.bottom,
            "orbs": cadavre.orbs,
        }
        if cadavre and cadavre.alive
        else None,  # Verifie que le cadabre existe
    }
    if cadavre is None:
        with open(SAVE_FILE, "r") as f:
            existing = json.load(f)
        data["cadavre"] = existing.get("cadavre")

    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)


def charger(player, checkpoints, map, Forgeron=None):
    """Récupère et retourne des données depuis la sauvegarde ou la configuration pour de l'entité.
    Entrées: player, checkpoints, map, Forgeron.
    Sortie: Retourne une valeur si applicable, sinon None.
    """

    if not os.path.exists(SAVE_FILE):
        return pygame.math.Vector2(
            DEFAULT_SPAWNS[map]["x"], DEFAULT_SPAWNS[map]["y"]
        ), None  # si y'a pas de save : spawn par défaut + pas de cadavre

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

    if Forgeron is not None and "upgrade_cost" in data["player"] and "orbs_cost" in data["player"]:
        Forgeron.upgrade_cost = data["player"]["upgrade_cost"]
        Forgeron.orb_cost = data["player"]["orbs_cost"]
    else:
        if Forgeron is not None:
            data["player"]["upgrade_cost"] = Forgeron.upgrade_cost
            data["player"]["orbs_cost"] = Forgeron.orb_cost

    # Abilities
    abilities_data = data.get("abilities", {})
    player.dash.unlocked = abilities_data["dash"]
    player.double_jump.unlocked = abilities_data["double_jump"]
    # Checkpoints
    main_spawn = data.get("main_spawn")
    if main_spawn:
        spawn_point = pygame.math.Vector2(main_spawn["x"], main_spawn["y"])
        spawn_map = main_spawn.get("map")
    else:
        spawn_point = get_spawn_from_checkpoints(checkpoints, map)
        spawn_map = map

    cadavre_data = data.get("cadavre")
    return spawn_point, cadavre_data, spawn_map


def supprimer_sauvegarde():
    """Sauvegarde l'état courant lié à de l'entité (player, checkpoints, objets) dans le fichier de sauvegarde.
    Entrées: aucune.
    Sortie: Aucune valeur renvoyée (None).
    """
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


def save_backup():
    """Sauvegarde l'état courant lié à de l'entité (player, checkpoints, objets) dans le fichier de sauvegarde.
    Entrées: aucune.
    Sortie: Retourne une valeur si applicable, sinon None.
    """
    if not os.path.exists(SAVE_FILE):
        try:
            with open(DEFAULT_SAVE, "r") as f_default:
                default_data = json.load(f_default)

            with open(SAVE_FILE, "w") as f_save:
                json.dump(default_data, f_save, indent=4)

            return True
        except Exception as e:
            return False


def charms_images():
    """Gère l'achat d'un charme: vérifie le coût, met à jour les ressources et enregistre la découverte dans la sauvegarde.
    Entrées: aucune.
    Sortie: Retourne une valeur si applicable, sinon None.
    """

    path = "Assets/charms"
    charms_assets = {
        "attack_long_range": path + "/attack_long_range.png",
        "attack_speed": path + "/attack_speed.png",
        "jump_boost": path + "/jump_boost.png",
        "no_knockback": path + "/no_knockback.png",
        "more_coin": path + "/more_coin.png",
        "fast_heal": path + "/fast_heal.png",
        "more_blood": path + "/more_blood.png",
        "speed_boost": path + "/speed_boost.png",
        "life_boost": path + "/life_boost.png",
        "spell_master": path + "/spell_master.png",
    }

    """
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    chrm = data.get("player", {}).get("found_charms", {})
    """

    return charms_assets


def get_chunks_params():
    """Récupère et retourne des données depuis la sauvegarde ou la configuration pour de l'entité.
    Entrées: aucune.
    Sortie: return dans config.json la valeur de chunk
    """
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    return data.get("chunks", 5)


def buy_charm(charm_name, price):
    """Gère l'achat d'un charme: vérifie le coût, met à jour les ressources et enregistre la découverte dans la sauvegarde.
    Entrées: charm_name, price.
    Sortie: modifie le nb d'orbs de Monnaie
    """

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
            data["player"]["found_charms"][charm_name] = True  # charms est trouvé et ajouté

            with open(SAVE_FILE, "w") as f:
                json.dump(data, f, indent=4)

            buy_sound.play()
            return " Charm acheté "

        else:
            error_sound.play()
            Monnaie.orbs += price  # faut bien rembourser si le joueur achete un charm qu'il a deja
            return "Vous possédez déjà ce charme."

    else:
        error_sound.play()
        return "Pas assez d'Orbs ...."
