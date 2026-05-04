import math
import pygame
from Visual.sprite_sheet import *
from Entities.physics_entity import PhysicsEntity
from World.objets import Monnaie

class Ennemi(Animation, PhysicsEntity):
    def __init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, pv_max, vitesse, attack_data, scale, reward=2):
        Animation.__init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, scale)
        PhysicsEntity.__init__(self, x, y, width, height, gravity = 0.4, friction = -0.5, use_gravity=True)

        #Etat
        self.alive = True
        self.reward = reward
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
        # ne pas infliger de dégats si il est mort ou invincible
        if not self.alive or self.is_shielded:
            return
        damage_amount = attack_data["damage"]

        if source.respawn_on_touch:
            self.pv_ennemi = 0
            self.alive = False
            return
        self.pv_ennemi -= damage_amount

        # knockback
        if self.can_receive_knockback:
            if hasattr(source, "attack_direction"): #Lorsque le joeur est la source
                if source.attack_direction == "UP":
                    self.velocity.y = -20
                elif source.attack_direction == "DOWN":
                    self.velocity.y = 50
                else : 
                    self.velocity.x = attack_data["knockback_x"] * source.direction
            else :
                if source_rect.centerx > self.rect.centerx:
                    knockback_direction = -1
                else:
                    knockback_direction = 1

                self.velocity.x = attack_data["knockback_x"] * knockback_direction
                self.velocity.y = attack_data["knockback_y"]
            self.is_knocked_back = True

        # meurte si les PV sont à 0 ou moins
        if self.pv_ennemi <= 0:
            self.pv_ennemi = 0
            self.alive = False
    
    def mort(self):
        fin = False
        
        if not self.alive and not self.dead:
            self.dead = True
            self.animation_mort.gestion_animation() # Jouer l'animation de mort
            Monnaie.add_orbs(self.reward)    # la reward
        if self.dead:
            image = self.animation_mort.gestion_animation()
            if self.direction == 1:
                self.image = self.animation_mort.frames_droite[int(self.animation_mort.index_image)]
            else:
                self.image = self.animation_mort.frames_gauche[int(self.animation_mort.index_image)]
                
            if self.animation_mort.index_image >= len(self.animation_mort.frames_droite) - 1:
                    fin = True

            return fin  # True quand l'animation est terminée

        return False  # encore en vie

class Projectile:
    def __init__(self, x, y, target_x, target_y, speed, width, height, damage, gravity=0.4, \
                  lifetime=3000, should_disappear_on_contact=True, image=None, use_gravity=False):
        
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
        self.should_disappear_on_contact = should_disappear_on_contact

        if image:
            self.image = pygame.transform.scale(image, (width, height))
        else:
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            self.image.fill((255, 0, 0))  # Couleur rouge pour les projectiles sans image

        self.angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x))
        
    def update(self, platforms, limite_rect):
        if self.use_gravity:
            self.velocity.y += self.gravity

        self.position += self.velocity
        self.rect.center = (int(self.position.x), int(self.position.y))

        self.angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x))

        if self.lifetime_expired() or self.out_of_bounds(limite_rect) or self.disappear_on_contact(platforms):
            return True  # Indiquer que le projectile doit être supprimé

    def lifetime_expired(self):
        return pygame.time.get_ticks() - self.birth_time > self.lifetime

    def out_of_bounds(self, limite_rect):
        return not limite_rect.colliderect(self.rect)
    
    def disappear_on_contact(self, platforms):
        if self.should_disappear_on_contact:
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    return True
        return False
        
    def draw(self, fenetre, camera):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated_image.get_rect(center=camera.apply(self.rect).center)
        fenetre.blit(rotated_image, new_rect)

class AttackZone:
    def __init__ (self, x, y, width, height, attack_data, image, duration):
        self.rect = pygame.Rect(x, y, width, height)
        self.position = pygame.math.Vector2(x, y)
        self.attack_data = attack_data
        self.birth_time = pygame.time.get_ticks()
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

    def lifetime_expired(self):
        return pygame.time.get_ticks() - self.birth_time > self.duration
    
    def draw(self, fenetre, camera):
        if pygame.key.get_pressed()[pygame.K_a]:
            pygame.draw.rect(fenetre, (255,0,0), camera.apply(self.rect), 2)
        fenetre.blit(self.image, camera.apply(self.rect))

class Patrouilleur(Ennemi):
    def __init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, pv_max, vitesse, attack_data, scale, reward=2):
        super().__init__(fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, pv_max, vitesse, attack_data, scale,reward)

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
        super().__init__(fenetre, x, y, 'Assets/Images/insecte_sheet2.png', 8, 70, 50, 13, 5, 3, 1.7, {"damage": 1, "knockback_x": 80, "knockback_y": -4}, scale=1, reward=4)

        self.animation_mort = Animation(fenetre, x, y, 'Assets/Images/insecte_sheet2.png', 7, 62, 50, 27, 7, scale=1)
        self.dead = False
        self.death_sound = pygame.mixer.Sound("Assets/Sounds/ennemi_death.mp3")
        self.death_sound.set_volume(0.2)
        self.death_sound_played = False

    def mort(self):
        if not self.death_sound_played:
            self.death_sound.play()
            self.death_sound_played = True
        return super().mort()

class Scorpion(Patrouilleur):
    def __init__(self, fenetre, x, y):
        super().__init__(fenetre, x, y, 'Assets/Images/scorpion.png', 8, 64, 64, 0, 0, 4, 1.7, {"damage": 1, "knockback_x": 80, "knockback_y": -4}, scale=1, reward=5)

        self.animation_mort = Animation(fenetre, x, y, 'Assets/Images/insecte_sheet2.png', 8, 70, 50, 13, 7, scale=1)
        self.dead = False

class Volant(Ennemi):
    def __init__(self, fenetre, x, y):
        
        # On applique les caractéristique de l'ennemi débutant au volant
        super().__init__(fenetre, x, y, 'Assets/Images/bat.png', 8, 16, 30, 0, 0, 3, 0.9, {"damage": 1, "knockback_x": 80, "knockback_y": -4}, scale=2, reward=4)

        self.image = self.frames_droite[0]
        self.use_gravity = False
        self.friction = -0.3
        self.animation_mort = Animation(fenetre, x, y, 'Assets/Images/insecte_sheet2.png', 8, 70, 50, 13, 7, scale=1)
        self.dead = False
        self.death_sound = pygame.mixer.Sound("Assets/Sounds/ennemi_death.mp3")
        self.death_sound.set_volume(0.2)
        self.death_sound_played = False

    def poursuite(self, player_rect, platforms):
        Animation.gestion_animation(self)
        if abs(player_rect.x - self.rect.x) < 300 and abs(player_rect.y - self.rect.y) < 300:  # Si le joueur est à proximité
            # Calculer la direction vers le joueur
            if player_rect.x > self.rect.x:
                self.direction = 1 # Aller vers la droite
            else:
                self.direction = -1 # Aller vers la gauche
            
            # Afficher la bonne frame en fonction de la direction (orientation perso)
            self.image = self.frames_gauche[int(self.index_image)] if self.direction == 1 else self.frames_droite[int(self.index_image)]
                
        # Calculer les composantes du vecteur de déplacement vers le joueur
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery

            # norme du vecteur de déplacement pour une vitesse constante
            vecteur_deplacement = math.sqrt(dx**2 + dy**2)
            if vecteur_deplacement != 0:
                self.velocity.x += (dx / vecteur_deplacement) * self.vitesse_deplacement
                self.velocity.y += (dy / vecteur_deplacement) * self.vitesse_deplacement
                
            # Appliquer la physique (déplacements et collisions)
            self.physics_update(platforms)

    def mort(self):
        if not self.death_sound_played:
            self.death_sound.play()
            self.death_sound_played = True
        return super().mort()
    

class Tourelle(Ennemi):
    def __init__(self, fenetre, x, y):
        
        # On applique les caractéristique de l'ennemi débutant a la tourelle
        super().__init__(fenetre, x, y, 'Assets/Images/tourelle.png', 8, 70, 63, 0, 0, 1, 1.7, {"damage": 1, "knockback_x": 80, "knockback_y": -4}, scale=1, reward=0)

        self.animation_mort = Animation(fenetre, x, y, 'Assets/Images/insecte_sheet2.png', 8, 70, 50, 13, 7, scale=1)
        self.animation_tir = Animation(fenetre, x, y, 'Assets/Images/tourelle.png', 8, 70, 63, 0, 0, scale=1)
        self.dead = False
        self.use_gravity = False
        self.can_receive_knockback = False
        self.apply_knockback = False
        self.coldown = 0
        self.shooting = False

        self.angle = 0              # Angle actuel du canon
        self.vitesse_rotation = 3  # orientation des frames de tir
        self.oriente = False        # alignement du canon avec le joueur pour tirer

        self.shoot_sound = pygame.mixer.Sound("Assets/Sounds/tourelle_shoot.mp3")
        self.shoot_sound.set_volume(0.7)
        self.shoot_sound_played = False

    def get_angle_vers_joueur(self, player_rect):
        dx = player_rect.centerx - self.rect.centerx #composante x du vecteur entre la tourelle et le joueur
        dy = player_rect.centery - self.rect.centery #composante y du vecteur entre la tourelle et le joueur
        return math.degrees(math.atan2(-dy, dx)) # Calculer l'angle entre la tourelle et le joueur pour orienter le tir
     
    def update(self,player_rect, player, platforms):    # j'ai ajouté platform en argument juste pour etre cohérent avec la physique des boss
        
        if self.coldown > 0:
            self.coldown -= 1

        # rotation permanente
        if self.dans_trigger(player_rect, trigger_range=300):
            self.rotation_vers_joueur(player_rect)

        # image de base par défaut
        base_image = self.frames_droite[0]

        # animation tir
        if self.shooting:
            base_image, fin = self.animation_tir.gestion_animation_once()

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
            if self.shoot_sound_played == False:
                self.shoot_sound.play()
                self.shoot_sound_played = False

            self.animation_tir.index_image = 0 
            # Créer un projectile qui se dirige vers le joueur
            projectile = Projectile(self.rect.centerx, self.rect.centery, player_rect.centerx, player_rect.centery, speed=5, width=20, height=20, damage= 1, image=pygame.image.load('Assets/Images/tir_tourelle.png').convert_alpha()) 
            tir_tourelle.append(projectile)
            self.coldown = 150  # Mettre un cooldown entre les tirs
    
class Fighter(Ennemi):
    def __init__(self, fenetre, x, y):
        
        # On applique les caractéristique de l'ennemi débutant a la tourelle
        super().__init__(fenetre, x, y, 'Assets/Images/fighter.png', 8, 62, 70, 3, 0, 10, 1.5, {"damage": 2, "knockback_x": 40, "knockback_y": -4}, scale=1, reward=5)
        self.animation_mort = Animation(fenetre, x, y, 'Assets/Images/insecte_sheet2.png', 8, 70, 50, 13, 7, scale=1)
        self.animation_attaque = Animation(fenetre, x, y, 'Assets/Images/attaque_fighter.png', 4, 83, 76, 0, 0, scale=1)
        self.dead = False
        self.use_gravity = True
        self.cooldown = 0
        self.attacking = False
        self.hitbox = None
        self.can_receive_knockback = False
     
    def mouvement(self, player_rect, player, platforms):
        Animation.gestion_animation(self)
        # Afficher la bonne frame en fonction de la direction (orientation perso)
        self.image = self.frames_droite[int(self.index_image)] if self.direction == 1 else self.frames_gauche[int(self.index_image)]

        if self.cooldown > 0: # Gérer le cooldown pour limiter la fréquence des attaques
            self.cooldown -= 1
        # Calculer la direction vers le joueur
        if player_rect.x > self.rect.x and abs(player_rect.centerx - self.rect.centerx) > 80:
            self.direction = 1 # Aller vers la droite
        elif player_rect.x < self.rect.x and abs(player_rect.centerx - self.rect.centerx) > 80:
            self.direction = -1 # Aller vers la gauche
        else:
            self.attaque() # Attaquer si proche du joueur
        
        if self.is_knocked_back:
            # Appliquer la physique (déplacements et collisions) pendant le knockback
            self.physics_update(platforms)
            if self.on_ground and abs(self.velocity.x) < 0.5:
                self.is_knocked_back = False
        else:
            self.velocity.x = self.vitesse_deplacement * self.direction
            self.physics_update(platforms)
        
        if self.attacking:
            if self.hitbox:
                        if self.hitbox.rect.colliderect(player.rect):
                            if self.hitbox not in player.entite_touches: # Vérifier que cet ennemi n'a pas déjà été touché par cette attaque
                                player.entite_touches.append(self.hitbox) # Ajouter l'ennemi à la liste d'entités déjà touchées
                                hitstop_duration, shake_amount = player.take_damage(self.attack_data, self.rect, self)# Appliquer les effets de l'attaque au joueur
                                hitstop_until = pygame.time.get_ticks() + hitstop_duration
            image, fin = self.animation_attaque.gestion_animation_once()
            self.image = image if self.direction == 1 else pygame.transform.flip(image, True, False)
            
            if fin:
                self.attacking = False
                self.animation_attaque.index_image = 0
        if self.hitbox is not None and self.hitbox.lifetime_expired():
                self.hitbox = None  # Supprimer la hitbox après la durée de l'attaque

    def attaque(self):
        if self.attacking:   
            return
        # Attaquer si le cooldown est écoulé
        if self.cooldown == 0:
            self.attacking = True
            self.animation_attaque.index_image = 0 
            self.cooldown = 210  # Mettre un cooldown entre les attaques
            self.hitbox = AttackZone(self.rect.centerx , self.rect.centery , 80, 40, self.attack_data, None, duration=500)
            self.hitbox.rect.center = (self.rect.centerx + (80 * self.direction), self.rect.centery)  # Positionner la hitbox devant le fighter en fonction de sa direction
            return self.hitbox

class Chargeur(Ennemi):
    def __init__(self, fenetre, x, y):
        super().__init__(fenetre, x, y, 'Assets/Images/chargeur.png', 8, 82, 58, 3, 0, 3, 3, {"damage": 1, "knockback_x": 150, "knockback_y": -4}, scale=1, reward=8)

        self.animation_mort = Animation(fenetre, x, y, 'Assets/Images/chargeur_dead.png', 8, 82, 58, 3, 0, scale=1)
        self.dead = False
        self.charge_timer = 0
        self.attacking = False
        self.duree_charge = 0

        self.death_sound = pygame.mixer.Sound("Assets/Sounds/ennemi_death.mp3")
        self.death_sound.set_volume(0.2)
        self.death_sound_played = False

    def charge(self, player_rect, platforms):
        Animation.gestion_animation(self)
        # Afficher la bonne frame en fonction de la direction (orientation perso)
        self.image = self.frames_droite[int(self.index_image)] if self.direction == 1 else self.frames_gauche[int(self.index_image)]
        
        if self.attacking:
            self.vitesse_animation = 0.2  # accélérer l'animation pendant la charge
            self.duree_charge -= 1
            if self.direction == 1:
                self.velocity.x = self.vitesse_deplacement * 5 * 1  # Se lancer vers le joueur à grande vitesse
            elif self.direction == -1:
                self.velocity.x = self.vitesse_deplacement * 5 * -1  # Se lancer vers le joueur à grande vitesse
            if self.duree_charge <= 0:
                self.attacking = False
                self.vitesse_animation = 0.1  # Réinitialiser la vitesse d'animation après la charge
                self.charge_timer = 0

        else:
            # Calculer la direction vers le joueur
            if player_rect.x > self.rect.x:
                self.direction = 1 # Aller vers la droite
            else:
                self.direction = -1 # Aller vers la gauche
                 
            if abs(player_rect.centerx - self.rect.centerx) < 300:  # Si le joueur est à portée de charge
                self.charge_timer += 1
                if self.charge_timer >= 70:  # Temps de charge avant de se lancer
                    self.duree_charge = 90  # Durée pendant laquelle le chargeur reste en mode charge
                    self.attacking = True

            self.velocity.x = self.vitesse_deplacement * self.direction  # Se déplacer normalement

        # Appliquer la physique (déplacements et collisions)
        self.physics_update(platforms)
    
    def mort(self):
        if not self.death_sound_played:
            self.death_sound.play()
            self.death_sound_played = True
        return super().mort()
    
if __name__ == "__main__":
    # Créer une fenêtre de jeu de test
    ecran = pygame.display.set_mode((800, 600))
    araignee = Araignee(ecran, 100, 100)
    volant = Volant(ecran, 200, 100)
    pygame.quit()
