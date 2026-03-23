import pygame
from World.map import Platform, platforms
from Visual.sprite_sheet import *
from Entities.perso import Player

class Ennemi(Animation):
    def __init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, pv_max, vitesse, attack_data):
        super().__init__(fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne)

        #Etat
        self.alive = True
        self.ignore_invincibility = False
        self.respawn_on_touch = False 

        #Position initiale (pour le reset)
        self.position_initiale_x = x # sur l'axe x
        self.position_initiale_y = y # sur l'axe y

        #Physique
        self.velocity = pygame.math.Vector2(0,0)
        self.friction = 0.8
        self.direction = 1

        #Stats
        self.pv_max = pv_max
        self.pv_ennemi = pv_max
        self.vitesse_deplacement = vitesse
        self.attack_data = attack_data
    
    def appliquer_physique(self, platforms):

        # Mouvement
        self.velocity.x *= self.friction # On applique la friction pour que l'araignée s'arrête petit à petit
        self.rect.x += self.velocity.x # on rajoute la vitesse horizontale à la position de l'araignée
        self.rect.y += self.velocity.y # on rajoute la vitesse verticale à la position de l'araignée

        # Collisions horizontales (murs)
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity.x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity.x < 0:
                    self.rect.left = platform.rect.right
                self.velocity.x = 0

        # Collisions verticales (sol + plafond)
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity.y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                elif self.velocity.y < 0:
                    self.rect.top = platform.rect.bottom
                    self.velocity.y = 0

    def knockback(self,player_rect, player):
        if player_rect.centerx > self.rect.centerx:
            recul_direction = -1 # Reculer vers la gauche si le joueur est à droite de l'ennemi
        else:
            recul_direction = 1
        self.velocity.x += 10 * recul_direction # Reculer l'ennemi dans la direction opposée à laquelle il fait face lorsqu'il est touché
        self.velocity.y = -5 # faire sauter légerement l'ennemi si touché
        self.pv_ennemi -=  player.attack
        if self.pv_ennemi <= 0:
            self.alive = False
        

class Araignee(Ennemi):
    def __init__(self, fenetre, x, y):
        # On applique les caractéristique de l'ennemi débutant à l'araignée
        super().__init__(fenetre, x, y, 'Assets/Images/insecte_sheet2.png', 8, 70, 50, 13, 5, 3, 1.7, {"damage": 1, "knockback_x": 80, "knockback_y": -4})

        #caracteristique deplacement de l'araignée
        self.gravité = 0.4

    def patrouille(self):
        Animation.gestion_animation(self)
        self.mur = False
        self.on_ground = False
        self.capteur_on_ground = False


        if abs(self.velocity.x) < 0.2:# Si la vitesse est très faible, on la met à zéro pour éviter les mouvements de glissement infinis
            self.velocity.x = 0

        if self.direction == 1: # Si l'araignée va vers la droite, le capteur de mur est devant elle à droite
            devant = self.rect.right
        else:
            devant = self.rect.left # Si l'araignée va vers la gauche, le capteur de mur est devant elle à gauche
        # Afficher la bonne frame en fonction de la direction (orientation perso)
        self.image = self.frames_droite[int(self.index_image)] if self.direction == 1 else self.frames_gauche[int(self.index_image)]

        # Capteur de mur : juste devant le sprite
        test_mur = pygame.Rect(0, 0, 10, 10)
        test_mur.center = (devant + (self.direction * 5), self.rect.centery)

        # Capteur de vide : juste devant le sprite et un peu en dessous pour détecter les plateformes
        capteur_vide = pygame.Rect(0, 0, 10, 10)
        capteur_vide.center = (devant + (self.direction * 5), self.rect.bottom + 5)

        self.velocity.y += self.gravité # L'araignée accélère vers le bas
        if self.velocity.y > 20: # Limite la vitesse de chute des ennemis
            self.velocity.y = 20
        self.rect.y += self.velocity.y  # On applique la chute

        # Gérer les collisions avec les plateformes après la chute
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity.y > 0: # Si elle tombe
                    self.rect.bottom = platform.rect.top
                    self.velocity.y = 0
                    self.on_ground = True

        for platform in platforms:
            # Si le capteur de MUR touche une plateforme
            if test_mur.colliderect(platform.rect):
                self.mur = True
            if capteur_vide.colliderect(platform.rect):
                self.capteur_on_ground = True
    
        if self.on_ground:
            if self.velocity.x == 0:
                if self.mur or not self.capteur_on_ground :
                    self.direction *= -1
                    self.rect.x += self.direction * 2 # Reculer légèrement pour éviter de rester coincé contre le mur
                else:
                    self.rect.x += self.vitesse_deplacement * self.direction

class Volant(Ennemi):
    def __init__(self, fenetre, x, y):
        # On applique les caractéristique de l'ennemi débutant au volant
        super().__init__(fenetre, x, y, 'Assets/Images/sprit_sheet_volant.png', 4, 50, 50, 5, 3, 3, 1.7, {"damage": 1, "knockback_x": 80, "knockback_y": -4})

        self.image = self.frames_droite[0]


    def poursuite(self, player_rect):
            Animation.gestion_animation(self)
            # Afficher la bonne frame en fonction de la direction (orientation perso)
            self.image = self.frames_droite[int(self.index_image)] if self.direction == 1 else self.frames_gauche[int(self.index_image)]
            if player_rect.x > self.rect.x:
                self.direction = 1 # Aller vers la droite
            else:
                self.direction = -1 # Aller vers la gauche
            self.rect.x += self.vitesse_deplacement * self.direction # Déplacer horizontalement vers le joueur
            if player_rect.y > self.rect.y: # Si le joueur est en dessous de l'ennemi, descendre
                self.rect.y += self.vitesse_deplacement
            else:
                self.rect.y -= self.vitesse_deplacement # Si le joueur est au dessus de l'ennemi, monter

if __name__ == "__main__":
     # Créer une fenêtre de jeu
    ecran = pygame.display.set_mode((800, 600))
    ennemi = Ennemi(ecran)
    pygame.quit()