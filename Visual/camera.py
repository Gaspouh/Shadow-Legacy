import os

import pygame
import random
import math

Chemin_absolu = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
        self.camera.x = 0
        self.camera.y = 0

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

class Background_effect:
    def __init__(self, path_image, profondeur, fenetre):
        image = pygame.image.load(path_image).convert_alpha()
        ratio = fenetre.get_height() / image.get_height()
        new_width = int(image.get_width() * ratio)
        self.image = pygame.transform.scale(image, (new_width, fenetre.get_height()))  # int, pas de * 1.2
        self.image_width = new_width
        self.profondeur = profondeur
        self.path_image = path_image
        image = pygame.transform.scale(self.image, (new_width, fenetre.get_height()))
    
    def effect(self, fenetre, camera):
        # On multiplie par la profondeur et elle est entre 0 et 1, 1 c'est la meme vitesse et 0 c'est immobile (quand la distance tend vers l'infini + Application de la "formule du tiling" classique pour faire du parallax. repete l'image au max pour couvrir tout l'écran en gros
        offset_x = (camera.camera.x * self.profondeur)  % self.image_width # là le modulo permet repeter l'image à l'infini
        if self.path_image == os.path.join(Chemin_absolu, "Graphics", "hollow_earth", "Background", "3.png"):
            offset_y = camera.camera.y + 2010 # y_offset
        elif self.path_image == os.path.join(Chemin_absolu, "Graphics", "hollow_earth", "Background", "4.png"):
            offset_y = camera.camera.y + 1990 # y_offset
        else:
            offset_y = camera.camera.y * self.profondeur * 0.3
            offset_y = max(-(self.image.get_height() - fenetre.get_height()), min(0, offset_y)) # limiter le déplacement vertical pour ne pas montrer les zones hors limites

        # On dessine deux fois pour couvrir les transitions (tiling) cas classique du parallax)
        fenetre.blit(self.image, (offset_x - self.image_width, offset_y)) 
        fenetre.blit(self.image, (offset_x, offset_y))
        if offset_x + self.image_width < fenetre.get_width(): # Ne pas dessiner si deja hors de l'écran
            fenetre.blit(self.image, (offset_x + self.image_width, offset_y))
            

def create_parallax_layers(map_path, nb_layers, fenetre):
        profondeurs = [(i / nb_layers) * 0.5 for i in range(1, nb_layers + 1)]
        layers = []
        for i, p in enumerate(profondeurs):
            image_path = os.path.join(map_path, "Background", f"{i+1}.png")
            layers.append(Background_effect(image_path, p, fenetre))
        return layers

def draw_parallax(fenetre, camera, layers):
        for layer in layers:
            layer.effect(fenetre, camera)
       
print(Chemin_absolu)
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


def background_luciole(game_fenetre, offset_x, offset_y, now):
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

def intro(fenetre):
    clock = pygame.time.Clock()
    font = pygame.font.Font("Assets/Font/Cinzel.ttf", 40)
    texte = ["Le monde est tombé dans l’ombre", "Les royaumes ont disparu", "et la lumière s’est éteinte", "Il ne reste que des ruines"\
              ,"et un silence sans fin", "Mais une lueur persiste encore", "Et cette lueur, c’est toi", "va jeune héros et sauve le monde de l'obscurité"]

    # Position de départ (bas de l’écran)
    y_offset = fenetre.get_height()

     # Paramètres
    scroll_speed = 2
    duration = 10000  # durée totale en ms

    start_time = pygame.time.get_ticks()
    running = True

    while running:
        now = pygame.time.get_ticks()
        temps = now - start_time

        #scoll vers le haut
        y_offset -= scroll_speed

        fenetre.fill((0,0,0))

        for i, ligne in enumerate(texte):
            text_surface = font.render(ligne, True, (180, 180, 200))
            text_rect = text_surface.get_rect(center=(fenetre.get_width()//2, y_offset + i * 80))

            fenetre.blit(text_surface, text_rect)
        
        pygame.display.update()
        clock.tick(60)

        if temps > duration :
            running = False