import pygame
from Core.save import (
    load_config,
    get_player_equipped_charms,
    get_player_unlocked_abilities,
    unlock_ability,
)
from Entities.ennemi import Projectile


class Ability(pygame.sprite.Sprite):
    KEYS = {"dash": "Maj Gauche", "double_jump": "Espace dans les airs"}

    def __init__(self, x, y, width, height, ability_name, name):
        self.name = name
        self.ability_name = ability_name
        self.text_timer = 0
        self.collected = get_player_unlocked_abilities()[ability_name]
        self.image = pygame.image.load("Assets\Images\Ability.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, player_rect, player):
        """Met à jour l'état du joueur (position, santé, capacités) en fonction des entrées, des collisions et du temps.
        Entrées: player_rect, player.
        Sortie: Aucune valeur renvoyée (None).
        """
        if not self.collected and self.rect.colliderect(player_rect):
            unlock_ability(self.ability_name)
            getattr(player, self.ability_name).unlocked = True  # mettre ability.unlocked à True
            self.collected = True
            self.text_timer = pygame.time.get_ticks()

    def draw(self, game_fenetre, camera):
        """Dessine du joueur à l'écran en tenant compte de la caméra, de la position et de l'animation.
        Entrées: game_fenetre, camera.
        Sortie: Aucune valeur renvoyée (None).
        """
        if not self.collected:
            game_fenetre.blit(self.image, camera.apply(self.rect))

    def draw_text(self, game_fenetre):
        """Dessine du joueur à l'écran en tenant compte de la caméra, de la position et de l'animation.
        Entrées: game_fenetre.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        if not self.text_timer or pygame.time.get_ticks() - self.text_timer > 3500:
            return
        font = pygame.font.SysFont("Arial", 25, bold=True)
        text = font.render(
            f"{self.name} débloqué  —  [{self.KEYS[self.ability_name]}] pour l'utiliser",
            True,
            (255, 255, 255),
        )
        text_x = game_fenetre.get_width() // 2 - text.get_width() // 2
        text_y = game_fenetre.get_height() // 2 - text.get_height() // 2
        cadre = pygame.Surface((text.get_width() + 20, text.get_height() + 20), pygame.SRCALPHA)
        cadre.fill((0, 0, 0, 150))  # Noir avec Opacité de 150
        game_fenetre.blit(cadre, (text_x - 10, text_y - 10))  # Centrer le cadre
        game_fenetre.blit(text, (text_x, text_y))


class Dash:
    def __init__(self, cfg={}):  # cfg signifie "configuration"
        self.unlocked = False  # Permet de débloquer le dash plus tard dans le jeu

        cfg_dash = cfg if cfg else load_config()["abilities"]["dash"]

        self.vitesse_dash = cfg_dash.get("vitesse_dash", 80)
        self.duree = cfg_dash.get("duree", 100)
        self.cooldown = cfg_dash.get("cooldown", 1000)

        self.in_use = False
        self.dash_timer = 0
        self.last_dash = -1000
        self.dash_invincible = False  # Flag pour savoir si l'invincibilité vient du dash

    def start_dash(self, player):
        """Vérifie si un son peut être joué selon le cooldown et le temps écoulé pour éviter les répétitions.
        Entrées: player.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        now = pygame.time.get_ticks()

        if not self.unlocked:  # empeche d'executer le dash avant son obtention
            return False

        if not self.in_use and now - self.last_dash >= self.cooldown:
            self.in_use = True
            self.dash_timer = now
            self.last_dash = now
            self.dash_direction = player.direction

            keys = pygame.key.get_pressed()
            self.is_dash_down = keys[pygame.K_s] and not player.on_ground

            # Invincibilité juste pour le dash vers le bas
            if self.is_dash_down:
                player.invincible = True
                self.dash_invincible = True

            return True
        return False

    def update(self, player):
        """Met à jour l'état du joueur (position, santé, capacités) en fonction des entrées, des collisions et du temps.
        Entrées: player.
        Sortie: Aucune valeur renvoyée (None).
        """
        if self.in_use:
            now = pygame.time.get_ticks()
            if now - self.dash_timer > self.duree:
                self.in_use = False
                player.velocity.y *= 0.7

                # Retirer l'invincibilité du dash seulement si c'est le dash qui l'avait activée
                # (et non une invincibilité due à des dégâts reçus)
                if self.dash_invincible:
                    player.invincible = False
                    self.dash_invincible = False

            else:
                if self.is_dash_down:
                    player.velocity.x = (
                        0  # Ne pas permettre au joueur de se déplacer horizontalement pendant le dash vers le bas
                    )
                    player.velocity.y = (
                        self.vitesse_dash * 0.3
                    )  # Appliquer la vitesse de dash vers le bas plus lente vers le bas car il n'y a pas de force qui compense le dash sur l'axe des y
                else:
                    player.velocity.x = (
                        (self.vitesse_dash * 0.3 if player.on_ice else self.vitesse_dash) * self.dash_direction
                    )  # Appliquer la vitesse de dash dans la direction du joueur (diminuée si joueur est sur de la glace)
                    player.velocity.y = 0  # Ne pas permettre au joueur de monter ou descendre pendant le dash


class Double_jump:
    def __init__(self, cfg={}):
        self.unlocked = False  # Permet de débloquer le double saut plus tard dans le jeu

        cfg_dj = cfg if cfg else load_config()["abilities"]["double_jump"]

        self.strength = cfg_dj.get("strength", -12)
        self.used = False

    def reset(self):  # Appelé quand le joueur touche le sol ou fait un pogo
        """Réinitialise du joueur à son état de départ en restaurant position, santé et vitesses.
        Entrées: aucune.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.used = False

    def can_execute(self, player):
        """Exécute la logique de la fonction can_execute liée à du joueur, modifiant l'état ou produisant une action spécifique.
        Entrées: player.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        if self.unlocked and not self.used and not player.on_ground:
            return True
        return False


class sort:
    def __init__(self):
        self.cost = 33  # Coût en sang pour utiliser le sort
        self.damage = 3

    def use(self, player, projectiles):
        """Gère la réception des dégâts du joueur en appliquant les effets selon les attributs de la source (dégâts, type, recul, invincibilité, etc.).
        Entrées: player, projectiles.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        if get_player_equipped_charms().get("spell_master"):
            self.cost = 22
            self.damage = 5
        else:
            self.cost = 33
            self.damage = 3
        if player.sang >= self.cost:  # Vérifie que le joueur a assez de sang pour utiliser le sort
            player.sang -= self.cost  # Consomme du sang
            direction = player.direction
            x = player.rect.centerx + (direction * 30)
            y = player.rect.centery - 20  # pour éviter la collision avec le sol
            target_x = x + (direction * 1000)  # tire loin devant
            target_y = y
            projectile = Projectile(
                x,
                y,
                target_x,
                target_y,
                15,
                80,
                80,
                self.damage,
                image=pygame.image.load("Assets/Images/sort.png").convert_alpha(),
            )
            projectiles.append(projectile)
            return True
        return False


class soin:
    def __init__(self):
        self.cost = 33  # Coût en sang pour utiliser le soin
        self.heal_amount = 1  # Quantité de santé restaurée par le soin
        self.clock = 0  # Horloge pour gérer le cooldown du soin
        self.cooldown = 1000  # Cooldown du soin en millisecondes
        self.last_heal_time = -5000  # Temps du dernier soin
        self.is_healing = False  # pour indiquer si le soin est en cours d'utilisation
        self.timer_soin = 0  # Timer pour gérer la durée du soin
        self.duree_soin = 2000  # Durée pendant laquelle le joueur est étourdi après avoir utilisé le soin

    def use(self, player):
        """Exécute la logique de la fonction use liée à du joueur, modifiant l'état ou produisant une action spécifique.
        Entrées: player.
        Sortie: Aucune valeur renvoyée (None).
        """
        now = pygame.time.get_ticks()
        if get_player_equipped_charms().get("fast_heal", False):
            self.timer_soin = 1200
        else:
            self.timer_soin = 2000
        if (
            player.sang >= self.cost
            and player.health < player.max_health
            and now - self.last_heal_time >= self.cooldown
        ):  # Vérifie que le joueur a assez de sang et n'est pas déjà à pleine santé
            self.is_healing = True
            self.timer_soin = now  # Démarre le timer du soin
            player.stun_timer = now  # Le joueur est étourdi pendant la durée du cooldown du soin
            player.stun_duration = 3000  # Le joueur est étourdi après avoir utilisé le soin

    def update(self, player):
        """Met à jour l'état du joueur (position, santé, capacités) en fonction des entrées, des collisions et du temps.
        Entrées: player.
        Sortie: Retourne une valeur si applicable, sinon None.
        """
        if not self.is_healing:
            return

        now = pygame.time.get_ticks()

        if now - self.timer_soin >= self.duree_soin:  # Vérifie que le cooldown est écoulé
            player.sang -= self.cost  # Consomme du sang
            player.health = min(
                player.health + self.heal_amount, player.max_health
            )  # Restaure la santé du joueur sans dépasser le maximum
            self.last_heal_time = now  # Met à jour le temps du dernier soin
            self.is_healing = False  # Réinitialise l'état de soin
            self.timer_soin = 0  # Réinitialise le timer du soin
