import pygame
import random
import math

class Camera:
    def __init__(self, width, height, map_width, map_height, zoom=2):
        """ Ajout d'un zoom pour faire des effets plus tard et controler la caméra """
        self.zoom = zoom
        self.zoom_w = int(width/zoom)
        self.zoom_h = int(height/zoom)
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height
        self.camera = pygame.Rect(0, 0, self.zoom_w, self.zoom_h)


    def apply(self, entity_rect):
        return entity_rect.move(self.camera.topleft)
    
    def update_map_size(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height

    def update(self, target, shake_amount=0):
        target_x = -target.rect.centerx + self.zoom_w // 2
        target_y = -target.rect.centery + self.zoom_h // 2

        # Appliquer un lissage pour un mouvement de caméra plus fluide
        self.camera.x += (target_x - self.camera.x) * 0.15
        self.camera.y += (target_y - self.camera.y) * 0.15

        # Limiter le déplacement de la caméra pour ne pas montrer les zones hors limites
        self.camera.x = min(0, max(-(self.map_width - self.zoom_w), self.camera.x))
        self.camera.y = min(0, max(-(self.map_height - self.zoom_h), self.camera.y))
        

        if shake_amount > 0:
            self.camera.x += random.randint(-shake_amount, shake_amount)
            self.camera.y += random.randint(-shake_amount, shake_amount)

class Background_effect:    # On utilise le "parallax layer", c'est un Effet populaire en 2D et utlisé dans hollow knight pour créer de la profondeur
    def __init__(self, fenetre, path_image, profondeur):
        self.fenetre = fenetre
        self.image = pygame.image.load(path_image).convert_alpha()
        self.profondeur = profondeur
    
    def effect(self, camera):
        # On multiplie par la profondeur et elle est entre 0 et 1, 1 c'est la meme vitesse et 0 c'est immobile (quand la distance tend vers l'infini)
        offset_x = -camera.camera.x * self.profondeur  # "-" car la camera est deja negative, ça fait une valeur absolue en gros
        offset_y = -camera.camera.y * self.profondeur
        
        # Application de la "formule du tiling" classique pour faire du parallax. repete l'image au max pour couvrir tout l'écran en gros
        img_w = self.image.get_width()
        # là le modulo permet repeter l'image à l'infini
        start_x = offset_x % img_w
        
        # On dessine deux fois pour couvrir les transitions (tiling) cas classique du parallax)
        self.fenetre.blit(self.image, (start_x - img_w, offset_y))
        self.fenetre.blit(self.image, (start_x, offset_y))
        if start_x + img_w < self.fenetre.get_width():
            self.fenetre.blit(self.image, (start_x + img_w, offset_y)) 

lucioles =[] # création de luciole
for i in range(16):
    lucioles.append(
    {
        "x": random.uniform(0, 3500),   # coordonné aléatoire
        "y": random.uniform(0, 1000),   # coordonné aléatoire
        "vx": random.uniform(-0.2, 0.2), # vitesse aléatoire
        "vy": random.uniform(-0.15, 0.15),# vitesse aléatoire
        "color": random.choice([ #couleurs aléatoires
            (60, 180, 80),
            (80, 200, 60),
            (40, 160, 120),
            (100, 255, 180),
            (120, 255, 150),
            (255, 100, 255),
            (255, 150, 255),
            (255, 200, 255),
            (200, 100, 255),            
            (255, 100, 200),
            (255, 150, 200),
            (255, 200, 200),

        ]),
        # variables d'animation des lucioles
        "radius": random.randint(15, 35),
        "phase": random.uniform(0, 6.28),
        "vitesse_scintillement": random.uniform(0.0003, 0.001),
        "amplitude": random.uniform(0.4, 0.8),
        "timer_direction": 0,
        "delai_direction": random.randint(200, 500),
    })

def background(game_fenetre, offset_x, offset_y, now):
    game_fenetre.fill((8, 8, 18)) # rempli l'écran en sombre
    longeur = game_fenetre.get_width() # longueur map
    hauteur = game_fenetre.get_height() # hauteur map

    for luciole in lucioles:
        luciole["timer_direction"] += 1 # temps avant mouvement
        if luciole["timer_direction"] >= luciole["delai_direction"]: # délai de mouvement atteint
            luciole["vx"] += random.uniform(-0.3, 0.3) # déplacment x
            luciole["vy"] += random.uniform(-0.3, 0.3) # déplacemnt y
            luciole["timer_direction"] = 0 # reset chrono
            luciole["delai_direction"] = random.randint(200, 500) # délai de mouvement aléatoire

        luciole["x"] += luciole["vx"] # mise à jour de la position x
        luciole["y"] += luciole["vy"] # mise à jour de la position y

        # Rester dans la map
        luciole["x"] = luciole["x"] % 3500 # retour dans le bord opposé si hors map
        luciole["y"] = luciole["y"] % 1000 #retour dans le bord opposé si hors map

        # convertir coordonné par raaport à la caméra
        screen_x = luciole["x"] - offset_x
        screen_y = luciole["y"] - offset_y

        # ne dessiner que si proche
        radius = luciole["radius"]
        if -radius < screen_x < longeur + radius and -radius < screen_y < hauteur + radius: # proche de la caméra
            draw_luciole(game_fenetre, screen_x, screen_y, luciole, now) #dessiner les lucioles

def draw_luciole(surface, x, y, luciole, now):
    # Calculer le niveau de brillance 
    brillance = 0.5 + 0.5 * math.sin(luciole["phase"] + now * luciole["vitesse_scintillement"]) # variation régulière avec la fonction sinus

    # Taille et transparence du halo dépendent de la brillance
    taille_halo = int(luciole["radius"] * (0.6 + 0.4 * brillance))
    transparence_halo = int(60 + 120 * brillance)

    if taille_halo < 1: # fin du cycle
        return

    # Dessiner le halo lumineux
    halo = pygame.Surface((taille_halo * 2, taille_halo * 2), pygame.SRCALPHA)
    pygame.draw.circle(halo, (*luciole["color"], transparence_halo), (taille_halo, taille_halo), taille_halo)
    surface.blit(halo, (x - taille_halo, y - taille_halo), special_flags=pygame.BLEND_RGBA_ADD)

    # Dessiner le noyau de la luciole
    taille_noyau = max(2, taille_halo // 4)
    transparence_noyau = int(200 * brillance)
    noyau = pygame.Surface((taille_noyau * 2, taille_noyau * 2), pygame.SRCALPHA)
    pygame.draw.circle(noyau, (200, 255, 200, transparence_noyau), (taille_noyau, taille_noyau), taille_noyau)
    surface.blit(noyau, (x - taille_noyau, y - taille_noyau), special_flags=pygame.BLEND_RGBA_ADD)