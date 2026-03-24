import pygame
from World.map import Platform, platforms
from Visual.sprite_sheet import *
from Entities.perso import Player
from Entities.physics_entity import PhysicsEntity

class Ennemi(Animation, PhysicsEntity):
    def __init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, pv_max, vitesse, attack_data):
        Animation.__init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne)
        PhysicsEntity.__init__(self, x, y, width, height, gravity = 0.4, friction = -0.5, use_gravity=True)

        #Etat
        self.alive = True
        self.ignore_invincibility = False
        self.respawn_on_touch = False 

        #Position initiale (pour le reset)
        self.position_initiale = pygame.math.Vector2(x, y)
        self.direction = 1

        #Stats
        self.pv_max = pv_max
        self.pv_ennemi = pv_max
        self.vitesse_deplacement = vitesse
        self.attack_data = attack_data

    def orienter_sprite(self):
        if self.direction == 1: # Afficher la bonne frame en fonction de la direction
            return self.frames_droite[int(self.index_image)] 
        return self.frames_gauche[int(self.index_image)]

    def dans_trigger(self, player_rect, trigger_range):
        trigger = pygame.Rect(
            self.rect.centerx - trigger_range,
            self.rect.centery - trigger_range,
            trigger_range * 2,
            trigger_range * 2
        )
        return trigger.colliderect(player_rect)
    
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


class Patrouilleur(Ennemi):
    def __init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, pv_max, vitesse, attack_data):
        super().__init__(fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, pv_max, vitesse, attack_data)

        # Capteurs pour patrouille
        self.mur = False
        self.capteur_on_ground = False

    def patrouille(self, platforms):
        # réinitialiser capteurs à chaque boucle
        self.mur = False
        self.capteur_on_ground = False
        
        if self.on_ground:
            Animation.gestion_animation(self)
            self.image = self.frames_droite[int(self.index_image)] if self.direction == 1 else self.frames_gauche[int(self.index_image)]

        if self.direction == 1: # Si l'araignée va vers la droite, le capteur de mur est devant elle à droite
            devant = self.rect.right

        else:
            devant = self.rect.left # Si l'araignée va vers la gauche, le capteur de mur est devant elle à gauche

        # Capteur de mur : juste devant le sprite
        test_mur = pygame.Rect(0, 0, 10, 10)
        test_mur.center = (devant + (self.direction * 5), self.rect.centery)

        # Capteur de vide : juste devant le sprite et un peu en dessous pour détecter les plateformes
        capteur_vide = pygame.Rect(0, 0, 10, 10)
        capteur_vide.center = (devant + (self.direction * 5), self.rect.bottom + 5)

        # Appliquer la vitesse de patrouille
        self.velocity.x = self.vitesse_deplacement * self.direction
        self.physics_update(platforms)

        # Détecter collisions capteur pour changer de direction
        for platform in platforms:

            # Si le capteur de MUR touche une plateforme
            if test_mur.colliderect(platform.rect):
                self.mur = True

            if capteur_vide.colliderect(platform.rect):
                self.capteur_on_ground = True

        if self.on_ground: 
            # Change direction    
            if self.mur or not self.capteur_on_ground :
                self.direction *= -1



class Araignee(Patrouilleur):
    def __init__(self, fenetre, x, y):
        super().__init__(fenetre, x, y, 'Assets/Images/insecte_sheet2.png', 8, 70, 50, 13, 5, 3, 1.7, {"damage": 1, "knockback_x": 80, "knockback_y": -4})


class Volant(Ennemi):
    def __init__(self, fenetre, x, y):
        # On applique les caractéristique de l'ennemi débutant au volant
        super().__init__(fenetre, x, y, 'Assets/Images/sprit_sheet_volant.png', 4, 50, 50, 5, 3, 3, 1.7, {"damage": 1, "knockback_x": 80, "knockback_y": -4})

        self.image = self.frames_droite[0]
        self.use_gravity = False


    def poursuite(self, player_rect):
        Animation.gestion_animation(self)
        # Afficher la bonne frame en fonction de la direction (orientation perso)
        self.image = self.frames_droite[int(self.index_image)] if self.direction == 1 else self.frames_gauche[int(self.index_image)]
        
        # Calculer la direction vers le joueur
        if player_rect.x > self.rect.x:
            self.direction = 1 # Aller vers la droite
        else:
            self.direction = -1 # Aller vers la gauche
            
        # Appliquer la vitesse de poursuite
        self.velocity.x = self.vitesse_deplacement * self.direction
        if player_rect.y > self.rect.y: # Si le joueur est en dessous de l'ennemi, descendre
            self.velocity.y = self.vitesse_deplacement
        else: # Si le joueur est au dessus de l'ennemi, monter
            self.velocity.y = -self.vitesse_deplacement
            
        # Appliquer la physique (déplacements et collisions)
        self.physics_update([])  # Pas de plateformes pour les volants

if __name__ == "__main__":
    # Créer une fenêtre de jeu de test
    ecran = pygame.display.set_mode((800, 600))
    araignee = Araignee(ecran, 100, 100)
    volant = Volant(ecran, 200, 100)
    pygame.quit()


