import pygame
import random

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

