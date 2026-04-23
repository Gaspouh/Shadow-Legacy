import math
import pygame
from World.map import Platform
from Visual.sprite_sheet import *
from Entities.physics_entity import PhysicsEntity

class Ennemi(Animation, PhysicsEntity):
    def __init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, pv_max, vitesse, attack_data):
        Animation.__init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne)
        PhysicsEntity.__init__(self, x, y, width, height, gravity = 0.4, friction = -0.5, use_gravity=True)

        #Etat
        self.alive = True
        self.ignore_invincibility = False
        self.respawn_on_touch = False 
        self.is_shielded = False
        self.can_receive_knockback = True
        self.apply_knockback = True
        self.is_knocked_back = False

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
    
    def receive_hit(self, attack_data, source_rect, source):

        if not self.alive or self.is_shielded:
            return 
        
        damage_amount = attack_data["damage"]

        if source.respawn_on_touch: # Tue ennemi lorsqu'il touche un piège
            self.pv_ennemi = 0
            return

        self.pv_ennemi -= damage_amount # Réduire la santé de l'ennemi lorsqu'il est touché

        if self.can_receive_knockback:
            if source_rect.centerx > self.rect.centerx:
                knockback_direction = -1
            else :
                knockback_direction = 1

            self.velocity.x = attack_data["knockback_x"] * knockback_direction # Reculer le joueur dans la direction opposée à laquelle il fait face lorsqu'il est touché
            self.velocity.y = attack_data["knockback_y"]  # faire sauter légerement le joueur si touché
            self.is_knocked_back = True
        if self.pv_ennemi <= 0:
            self.alive = False      
    
    def mort(self):
        if not self.alive and not self.dead:
            self.dead = True
            self.animation_mort.gestion_animation() # Jouer l'animation de mort
        if self.dead:
            image = self.animation_mort.gestion_animation()
        if self.direction == 1:
            self.image = self.animation_mort.frames_droite[int(self.animation_mort.index_image)]
        else:
            self.image = self.animation_mort.frames_gauche[int(self.animation_mort.index_image)]
class Projectile:
    def __init__(self, x, y, target_x, target_y, speed, width, height, damage, gravity=0.4, \
                  lifetime=3000, disappear_on_contact=True, image=None, use_gravity=False):
        
        dist_x = target_x - x
        dist_y = target_y - y
        dist = math.sqrt(dist_x ** 2 + dist_y ** 2)
        self.velocity = pygame.math.Vector2((dist_x / dist) * speed, (dist_y / dist) * speed)

        self.rect = pygame.Rect(x, y, width, height)
        self.position = pygame.math.Vector2(x, y)

        self.use_gravity = use_gravity
        self.gravity = gravity

        self.attack_data = {
            "damage": damage,
            "knockback_x": self.velocity.x * 0.5,
            "knockback_y": self.velocity.y * 0.5
        }

        #Etat
        self.ignore_invincibility = False
        self.respawn_on_touch = False 
        self.apply_knockback = True
        self.hit = False

        # Durée de vie du projectile
        self.birth_time = pygame.time.get_ticks()
        self.lifetime = lifetime
        self.disappear_on_contact = disappear_on_contact

        if image:
            self.image = pygame.transform.scale(image, (width, height))
        else:
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            self.image.fill((255, 0, 0))  # Couleur rouge pour les projectiles sans image


        self.angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x))
        
    def update(self):
        if self.use_gravity:
            self.velocity.y += self.gravity

        self.position += self.velocity
        self.rect.center = (int(self.position.x), int(self.position.y))

        self.angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x))

    def lifetime_expired(self):
        return pygame.time.get_ticks() - self.birth_time > self.lifetime

    def out_of_bounds(self, limite_rect):
        return not limite_rect.colliderect(self.rect)
        
    def draw(self, fenetre, camera):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated_image.get_rect(center=camera.apply(self.rect).center)
        fenetre.blit(rotated_image, new_rect)

class AttackZone():
    def __init__ (self, x, y, width, height, attack_data, image, duration):
        self.rect = pygame.Rect(x, y, width, height)
        self.position = pygame.math.Vector2(x, y)
        self.attack_data = attack_data
        self.birth_time = -1000
        self.duration = duration

        #Etat
        self.ignore_invincibility = False
        self.respawn_on_touch = False 
        self.apply_knockback = True

        if image:
            self.image = pygame.transform.scale(image, (width, height))
        else:
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            self.image.fill((255, 0, 0))  # Couleur rouge pour les projectiles sans image

        if image:
            self.image = pygame.transform.scale(image, (width, height))
        else:
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            self.image.fill((255, 0, 0))  # Couleur rouge pour les projectiles sans image

    def update(self):
        pass

    def lifetime_expired(self):
        return pygame.time.get_ticks() - self.birth_time > self.duration


    def out_of_bounds(self, limite_rect):
        pass

    def draw(self, fenetre, camera):
        pygame.draw.rect(fenetre, (255,0,0), camera.apply(self.rect), 2)
        fenetre.blit(self.image, camera.apply(self.rect))

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
        if self.is_knocked_back:
            self.physics_update(platforms)
            if self.on_ground and abs(self.velocity.x) < 0.5:
                self.is_knocked_back = False
        else:
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

        self.animation_mort = Animation(fenetre, x, y, 'Assets/Images/insecte_sheet2.png', 7, 62, 50, 27, 7)
        self.dead = False

class Volant(Ennemi):
    def __init__(self, fenetre, x, y):
        
        # On applique les caractéristique de l'ennemi débutant au volant
        super().__init__(fenetre, x, y, 'Assets/Images/sprit_sheet_volant.png', 4, 50, 50, 5, 3, 3, 1.7, {"damage": 1, "knockback_x": 80, "knockback_y": -4})

        self.image = self.frames_droite[0]
        self.use_gravity = False
        self.animation_mort = Animation(fenetre, x, y, 'Assets/Images/insecte_sheet2.png', 8, 70, 50, 13, 7)
        self.dead = False

    def poursuite(self, player_rect):
        Animation.gestion_animation(self)
        # Afficher la bonne frame en fonction de la direction (orientation perso)
        self.image = self.frames_droite[int(self.index_image)] if self.direction == 1 else self.frames_gauche[int(self.index_image)]
        
        # Calculer la direction vers le joueur
        if player_rect.x > self.rect.x:
            self.direction = 1 # Aller vers la droite
        else:
            self.direction = -1 # Aller vers la gauche
            
       # Calculer les composantes du vecteur de déplacement vers le joueur
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery

        # norme du vecteur de déplacement pour une vitesse constante
        vecteur_deplacement = math.sqrt(dx**2 + dy**2)
        if vecteur_deplacement != 0:
            self.velocity.x = (dx / vecteur_deplacement) * self.vitesse_deplacement
            self.velocity.y = (dy / vecteur_deplacement) * self.vitesse_deplacement
            
        # Appliquer la physique (déplacements et collisions)
        self.physics_update([])  # Pas de plateformes pour les volants

class Tourelle(Ennemi):
    def __init__(self, fenetre, x, y):
        
        # On applique les caractéristique de l'ennemi débutant a la tourelle
        super().__init__(fenetre, x, y, 'Assets/Images/tourelle.png', 8, 63, 63, 8, 0, 1, 1.7, {"damage": 1, "knockback_x": 80, "knockback_y": -4})

        self.animation_mort = Animation(fenetre, x, y, 'Assets/Images/insecte_sheet2.png', 8, 70, 50, 13, 7)
        self.animation_tir = Animation(fenetre, x, y, 'Assets/Images/tourelle.png', 8, 63, 63, 8, 0)
        self.dead = False
        self.use_gravity = False
        self.can_receive_knockback = False
        self.apply_knockback = False
        self.coldown = 0
        self.shooting = False

        self.angle = 0              # Angle actuel du canon
        self.vitesse_rotation = 3  # orientation des frames de tir
        self.oriente = False        # alignement du canon avec le joueur pour tirer

    def get_angle_vers_joueur(self, player_rect):
        dx = player_rect.centerx - self.rect.centerx #composante x du vecteur entre la tourelle et le joueur
        dy = player_rect.centery - self.rect.centery #composante y du vecteur entre la tourelle et le joueur
        return math.degrees(math.atan2(-dy, dx)) # Calculer l'angle entre la tourelle et le joueur pour orienter le tir
    
    
    def update(self,player_rect):
        
        if self.coldown > 0:
            self.coldown -= 1

        # rotation permanente
        if self.dans_trigger(player_rect, trigger_range=300):
            self.rotation_vers_joueur(player_rect)

        # image de base par défaut
        base_image = self.frames_droite[0]

        # animation tir
        if self.shooting:
            base_image = self.animation_tir.gestion_animation_once()

            if self.animation_tir.index_image >= len(self.animation_tir.frames_droite) - 1:
                self.shooting = False
                self.animation_tir.index_image = 0

        # rotation de la tourelle vers le joueur
        self.image = pygame.transform.rotate(base_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
    def rotation_vers_joueur(self, player_rect):
        angle_cible = self.get_angle_vers_joueur(player_rect)

        # Chemin de rotation le plus court
        diff = (angle_cible - self.angle + 180) % 360 - 180

        if abs(diff) < self.vitesse_rotation:  # orientation proche du jpueur
            self.angle = angle_cible
            self.oriente = True   # Le canon est orienté vers le joueur
        elif diff > 0:
            self.angle += self.vitesse_rotation
            self.oriente = False
        else:
            self.angle -= self.vitesse_rotation
            self.oriente = False

        self.angle %= 360

    def tir(self, player_rect, tir_tourelle):
        if self.dans_trigger(player_rect, trigger_range=300) and self.coldown == 0 and self.oriente:
            self.shooting = True
            self.animation_tir.index_image = 0 
            # Créer un projectile qui se dirige vers le joueur
            projectile = Projectile(self.rect.centerx, self.rect.centery, player_rect.centerx, player_rect.centery, speed=5, width=20, height=20, damage= 1, gravity=False) 
            tir_tourelle.append(projectile)
            self.coldown = 150  # Mettre un cooldown entre les tirs
            
    


if __name__ == "__main__":
    # Créer une fenêtre de jeu de test
    ecran = pygame.display.set_mode((800, 600))
    araignee = Araignee(ecran, 100, 100)
    volant = Volant(ecran, 200, 100)
    pygame.quit()
