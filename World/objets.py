import pygame
import json
import os
from Visual.sprite_sheet import *

SAVE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Core", "save.json")


class Coeur(Animation):
    def __init__(self, fenetre, x, y):
        super().__init__(fenetre, x, y, "Assets/Images/coeur2.png", 8, 88, 88, 0, 2, scale=1)
        self.state = "ALIVE"
        self.vitesse_animation = 0.3

        self.frames_droite = [pygame.transform.smoothscale(frame, (70, 70)) for frame in self.frames_droite]
        self.frames_gauche = self.frames_droite.copy()

        self.image = self.frames_droite[0]

    def update(self, current_player_health, heart_index):

        # on compare l'index du cœur avec la santé actuelle du joueur pour déterminer l'état du cœur
        """Met à jour l'état du cœur en fonction de la santé actuelle du joueur, en jouant l'animation de mort si la santé diminue, et en affichant un cœur vide si le cœur est mort.
        Entrées: current_player_health, heart_index.
        Sortie: Aucune valeur renvoyée 
        """
        if heart_index >= current_player_health and self.state == "ALIVE":
            # on enlève un cœur si la santé du joueur diminue
            self.state = "DYING"
            self.index_image = 0  # On reset l'anim pour jouer la séquence de mort

        # on ajoute un coeur si la santé du joueur augmente
        elif heart_index < current_player_health and self.state != "ALIVE":
            self.state = "ALIVE"
            self.image = self.frames_droite[0]

        # on laisse le coeur vivant
        if self.state == "ALIVE":
            self.image = self.frames_droite[0]

        # on joue l'animation de mort du cœur
        elif self.state == "DYING":
            self.index_image += self.vitesse_animation

            if self.index_image < len(self.frames_droite):
                self.image = self.frames_droite[int(self.index_image)]
            else:
                self.state = "DEAD"
                self.image = self.frames_droite[-1]  # Afficher le cœur vide une fois l'animation terminée

        # on affiche un cœur vide si le cœur est mort
        elif self.state == "DEAD":
            self.image = self.frames_droite[-1]


class Monnaie:
    global orbs
    orbs = 0  # Globale

    def __init__(self, fenetre, x, y):
        self.fenetre = fenetre

        self.image = pygame.image.load("Assets/Images/orbs.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (55, 55))
        self.font = pygame.font.SysFont("Playfair Display", 60, bold=True)
        self.rect = self.image.get_rect(topright=(fenetre.get_width() - 50, 50))

    @staticmethod  # permet de rendre global
    def add_orbs(amount, cadavre=False):
        """Ajoute un certain nombre d'orbes à la monnaie du joueur, en appliquant un multiplicateur si le joueur a le charme "more_coin" équipé et que les orbes ne proviennent pas d'un cadavre.
        Entrées: amount, cadavre.
        Sortie: Aucune valeur renvoyée (None).
        """
        from Core.save import get_player_equipped_charms

        if get_player_equipped_charms().get("more_coin", False) and not cadavre:
            Monnaie.orbs += amount * 1.3
        else:
            Monnaie.orbs += amount

    def draw(self, fenetre):
        """Dessine à l'écran le nombre d'orbes du joueur avec un effet de brillance, en tenant compte de la position et de l'animation.
        Entrées: fenetre.
        Sortie: Aucune valeur renvoyée (None).
        """
        self.rect = self.image.get_rect(topright=(fenetre.get_width() - 50, 50))
        texte = str(Monnaie.orbs)

        # effet de brillance, on décale autour du texte pour créer un halo + blit vertical pour que ça recouvre tout le texte (halo)
        for ox in range(-8, 9, 3):
            for oy in range(-8, 9, 3):
                glow_surf = self.font.render(texte, True, (210, 225, 255))  # version plus "bleu"
                glow_surf.set_alpha(11)  # Fondue plus moins forte
                fenetre.blit(
                    glow_surf,
                    (
                        self.rect.left - glow_surf.get_width() - 8 + ox,
                        self.rect.centery - glow_surf.get_height() // 2 + oy,
                    ),
                )

        # Texte en blanc
        texte_surf = self.font.render(texte, True, (255, 255, 255))
        fenetre.blit(
            texte_surf,
            (
                self.rect.left - texte_surf.get_width() - 8,
                self.rect.centery - texte_surf.get_height() // 2,
            ),
        )

        # Image orb à droite
        fenetre.blit(self.image, self.rect)


class Receptacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.taken = False

        self.img1 = pygame.transform.scale(pygame.image.load("Assets/Images/fragment1.png").convert_alpha(), (20, 40))
        self.img2 = pygame.transform.scale(pygame.image.load("Assets/Images/fragment2.png").convert_alpha(), (20, 40))
        self.img3 = pygame.transform.scale(pygame.image.load("Assets/Images/fragment3.png").convert_alpha(), (20, 40))

        self.image = self.img1
        self.rect = self.image.get_rect(topleft=(x, y))

        self.show_big = False
        self.show_timer = 0

    def update(self, player, objets, current_map_name, data):
        # Logique pour vérifier si le joueur est proche du réceptacle et peut le prendre
        """Met à jour le réceptacle en vérifiant la collision avec le joueur pour permettre la collecte, et en mettant à jour l'état du réceptacle en conséquence.
        Entrées: player, objets, current_map_name, data.
        Sortie: Aucune valeur renvoyée (None).
        """
        if self.rect.colliderect(player.rect) and not self.taken:
            player.receptacles += 1  # Augmente le nombre de réceptacles du joueur
            player.receptacles_total += 1  # Augmente le nombre total de réceptacles du joueur
            self.taken = True  # Marque le réceptacle comme pris
            self.show_big = True  # Affiche le réceptacle en grand pour indiquer qu'il a été pris
            self.show_timer = pygame.time.get_ticks()  # Démarre le timer pour l'affichage en grand

            objet_data = {"map": current_map_name, "x": self.rect.x, "y": self.rect.y}

            data.setdefault("taken_objects", [])

            if objet_data not in data["taken_objects"]:
                data["taken_objects"].append(objet_data)
                with open(SAVE_FILE, "w") as f:
                    json.dump(data, f, indent=4)

        if player.receptacles == 1:
            self.image = self.img1

        elif player.receptacles == 2:
            self.image = self.img2

        elif player.receptacles == 3:  # Si le joueur a 3 réceptacles, il gagne un cœur supplémentaire
            player.max_health += 1
            player.health = player.max_health
            self.image = self.img3
            player.receptacles = 0  # Reset les réceptacles après avoir obtenu le cœur

    def draw_big(self, game_fenetre, player):
        """Dessine en grand le réceptacle à l'écran pour indiquer qu'il a été pris, en tenant compte de la caméra, de la position et de l'animation.
        Entrées: game_fenetre, player.
        Sortie: Aucune valeur renvoyée (None).
        """
        if self.show_big:  # Affiche le réceptacle en grand pendant 2 secondes après l'avoir pris
            now = pygame.time.get_ticks()

            # durée affichage (2 secondes)
            if now - self.show_timer < 2000:
                big_img = pygame.transform.scale(self.image, (200, 400))

                rect = big_img.get_rect(
                    center=(
                        game_fenetre.get_width() // 2,
                        game_fenetre.get_height() // 2,
                    )
                )

                # Glow simple
                glow = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)
                pygame.draw.ellipse(glow, (255, 255, 150, 120), glow.get_rect())
                game_fenetre.blit(glow, (rect.x - 20, rect.y - 20))

                game_fenetre.blit(big_img, rect)

            else:
                self.show_big = False


class Minerai(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("Assets/Images/minerai.png").convert_alpha(), (30, 30))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.taken = False
        self.show_big = False
        self.show_timer = 0

    def update(self, player, objets, current_map_name, data):
        # Logique pour vérifier si le joueur est proche du minerai et peut le prendre
        """ met à jour les minerais en vérifiant la collision avec le joueur pour permettre la collecte, et en mettant à jour l'état du minerai en conséquence.
        Entrées: player, objets, current_map_name, data.
        Sortie: Aucune valeur renvoyée (None).
        """
        if self.rect.colliderect(player.rect) and not self.taken:
            player.minerais += 1  # Augmente le nombre de minerai du joueur
            self.taken = True  # Marque le minerai comme pris
            self.show_big = True  # Affiche le minerai en grand pour indiquer qu'il a été pris
            self.show_timer = pygame.time.get_ticks()  # Démarre le timer pour l'affichage en grand

            objet_data = {"map": current_map_name, "x": self.rect.x, "y": self.rect.y}

            data.setdefault("taken_objects", [])

            if objet_data not in data["taken_objects"]:
                data["taken_objects"].append(objet_data)
                with open(SAVE_FILE, "w") as f:
                    json.dump(data, f, indent=4)

    def draw_big(self, game_fenetre, player):
        """ Dessine en grand le minerai à l'écran pour indiquer qu'il a été pris, en tenant compte de la caméra, de la position et de l'animation.
        Entrées: game_fenetre, player.
        Sortie: Aucune valeur renvoyée 
        """
        if self.taken:  # Affiche le minerai en grand pendant 2 secondes après l'avoir pris
            now = pygame.time.get_ticks()

            # durée affichage (2 secondes)
            if now - self.show_timer < 2000:
                big_img = pygame.transform.scale(self.image, (150, 150))

                rect = big_img.get_rect(
                    center=(
                        game_fenetre.get_width() // 2,
                        game_fenetre.get_height() // 2,
                    )
                )

                # Glow simple
                glow = pygame.Surface((rect.width + 30, rect.height + 30), pygame.SRCALPHA)
                pygame.draw.ellipse(glow, (150, 255, 255, 120), glow.get_rect())
                game_fenetre.blit(glow, (rect.x - 15, rect.y - 15))

                game_fenetre.blit(big_img, rect)

            else:
                self.show_big = False


class Sac_logic:
    """a utiliser pour pouvoir créer un sac avec son nb d'orbes, son image, et le nb de coups a mettre pour le casser (puis obtenir les orbes)"""

    def __init__(self, x, y, orbs, image, life):
        self.x = x
        self.y = y
        self.orbs = orbs
        self.image = image
        self.life = life
        self.alive = True
        self.sound = pygame.mixer.Sound("Assets/Sounds/sac.mp3")
        self.sound.set_volume(0.5)
        self.hit = False
        self.taken = False

    def update(self, player, objects=None, current_map_name=None, data=None):
        # gestion de collision avc le joueur
        """Met à jour l'état du joueur (position, santé, capacités) en fonction des entrées, des collisions et du temps.
        Entrées: player, objects, current_map_name, data.
        Sortie: Aucune valeur renvoyée (None).
        """
        if player.is_attacking and player.attack_rect.colliderect(self.rect):
            if not self.hit and not self.taken:
                self.life -= 1
                self.hit = True
                self.sound.play()
                if self.life <= 0 :
                    Monnaie.add_orbs(self.orbs)
                    # faire disparaitre le sac et l'image
                    self.alive = False
                    self.taken = True

        else:
            self.hit = False  # pour pas attaquer a chaque frame

    def draw(self, fenetre, camera=None):
        """Dessine à l'écran
        Entrées: fenetre, camera.
        Sortie: Aucune valeur renvoyée 
        """
        if self.alive:
            pos = camera.apply(self.rect) if camera else self.rect
            fenetre.blit(self.image, pos)


class petit_sac(Sac_logic):
    def __init__(self, x, y):
        image = pygame.transform.scale(pygame.image.load("Assets/Images/sac_1.png").convert_alpha(), (40, 40))
        y += 24
        super().__init__(x, y, orbs=8, image=image, life=1)
        self.rect = self.image.get_rect(topleft=(x, y))


class moyen_sac(Sac_logic):
    def __init__(self, x, y):
        image = pygame.transform.scale(pygame.image.load("Assets/Images/sac_2.png").convert_alpha(), (50, 50))
        y += 5
        super().__init__(x, y, orbs=15, image=image, life=3)
        self.rect = self.image.get_rect(topleft=(x, y))


class grand_sac(Sac_logic):
    def __init__(self, x, y):
        image = pygame.transform.scale(pygame.image.load("Assets/Images/sac_3.png").convert_alpha(), (60, 60))
        y += 1
        super().__init__(x, y, orbs=25, image=image, life=6)
        self.rect = self.image.get_rect(topleft=(x, y))


class Cadavre:
    """permet au  joueur de recuperer ses orbes apres etre mort"""

    def __init__(self, x, y, orbs, map_name):
        self.orbs = orbs
        self.alive = True
        self.image = pygame.image.load("Assets/Player/dead_inventory.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.font = pygame.font.SysFont("Arial", 16, bold=True)
        self.map_name = map_name

    def update(self, player):
        """Met à jour le cadavre en vérifiant la collision avec le joueur pour permettre la récupération des orbes, et en mettant à jour l'état du cadavre en conséquence.
        Entrées: player.
        Sortie: Aucune valeur renvoyée (None).
        """
        if self.alive and self.rect.colliderect(player.rect):
            from Core.save import (
                SAVE_FILE,
            )  # imoport ici sinon ça bug a cause du circular import
            import json

            Monnaie.add_orbs(self.orbs, cadavre=True)  # recupere ses orbs mais sans multiplicateur
            self.alive = False
            # maj du json, on supprime le cadavre (le met a none)
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            data["cadavre"] = None
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f, indent=4)

    def draw(self, screen, camera=None):
        """ Dessine le cadavre à l'écran en tenant compte de la caméra, de la position et de l'animation.
        Entrées: screen, camera.
        Sortie: Aucune valeur renvoyée 
        """
        if not self.alive:
            return

        # Détermination de la position d'affichage
        if camera:
            pos = camera.apply(self.rect)
        else:
            pos = self.rect

        # Dessin de l'image du cadavre
        screen.blit(self.image, pos)

        # Préparation et affichage du texte (nombre d'orbes)
        texte = self.font.render(str(self.orbs), True, (255, 255, 255))
        # Calcul des coordonnées pour centrer le texte au-dessus
        texte_x = pos.centerx - (texte.get_width() // 2)
        texte_y = pos.top - 20

        screen.blit(texte, (texte_x, texte_y))
