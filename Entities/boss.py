import pygame
from Visual.sprite_sheet import VerticalAnimation
from World.map import platforms
import time
import random

class Golem(pygame.sprite.Sprite):  # pas de "self" ici
    def __init__(self, fenetre, x, y):
        super().__init__()
        self.ecran = fenetre

        # Variables d'état
        self.pv = 1000
        self.alive = True
        self.direction = 1

        # Spriteheets, animations :
        self.anim_idle        = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_idle_sheet.png',        40, 240, 240, 0, 0)
        self.anim_walk_right  = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_walk_right_sheet.png',  32, 240, 240, 0, 0)
        self.anim_walk_left   = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_walk_left_sheet.png',   32, 240, 240, 0, 0)
        self.anim_smash_right = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_smash_right_sheet.png', 12, 240, 240, 0, 0)
        self.anim_smash_left  = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_smash_left_sheet.png',  12, 240, 240, 0, 0)

        # Sons : dans le dossier : C:\Users\user\Shadow-Legacy\Assets\Sounds
        self.sound_smash1 = pygame.mixer.Sound('Assets/Sounds/golem_smash_sound1.MP3')
        self.sound_smash2 = pygame.mixer.Sound('Assets/Sounds/golem_smash_sound2.MP3')
        self.smash_sounds = [self.sound_smash1, self.sound_smash2]        

        self.played_sound = False # flag pour pas que le son se joue chaque frames

        v = 120
        # Vitesses d'animation (divisé par 60 pour chaque frame)
        self.anim_idle.vitesse_animation        = 40 / v /2
        self.anim_walk_right.vitesse_animation  = 32 / v /1.5 # plus lent
        self.anim_walk_left.vitesse_animation   = 32 / v /1.5
        self.anim_smash_right.vitesse_animation = 12 / v * 2 # plus rapide
        self.anim_smash_left.vitesse_animation  = 12 / v * 2

        # Affichage de base
        self.image = self.anim_idle.frames_droite[0]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Position et vitesse initiales
        self.position_initiale_x = x
        self.position_initiale_y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.5
        self.friction = 0.8
        self.vitesse_deplacement = 1

        # "Triggerbox" (declencheur de l'ia)
        self.trigger_range = 250
        # Dégat au contact
        self.attack_data = {
            "damage": 1,
            "knockback_x": 100,
            "knockback_y": -5
        }
        self.ignore_invincibility = False
        self.respawn_on_touch = False
        self.is_attacking = False

        # Attack range
        self.attack_range_x = 57
        self.attack_range_y = 125

        # Cooldown d'attaque
        self.attack_cooldown = 2.0
        self.last_attack_time = 0.0

        # Gestion hitbox avec le inflate
        self.rect = self.image.get_rect(topleft=(x, y))
        # avec inflate on reduit la hitbox du golem (-x, -y)
        self.hitbox = self.rect.inflate(-140, -95)
        
    def _joueur_dans_trigger(self, player_rect):
        trigger = pygame.Rect(
            self.rect.centerx - self.trigger_range,
            self.rect.centery - self.trigger_range,
            self.trigger_range * 2,
            self.trigger_range * 2)
        return trigger.colliderect(player_rect)

    def joueur_dans_attack(self, player_rect):
        attack_range_x = self.attack_range_x
        attack_range_y = self.attack_range_y
        if self.direction == 1:
            attack_rect = pygame.Rect(
                self.hitbox.right,
                self.hitbox.centery - attack_range_y // 2,
                attack_range_x,
                attack_range_y
            )
        if self.direction == -1:
            attack_rect = pygame.Rect(
                self.hitbox.left - attack_range_x,
                self.hitbox.centery - attack_range_y // 2,
                attack_range_x,
                attack_range_y
            )

        return attack_rect.colliderect(player_rect)
    
    def update(self, player_rect, player):
        if not self.alive:
            return

        # Gravité et physique
        self.rect.x += self.velocity_x
        self.velocity_x *= self.friction
        if abs(self.velocity_x) < 0.2:
            self.velocity_x = 0

        self.velocity_y += self.gravity
        if self.velocity_y > 20:
            self.velocity_y = 20
        self.rect.y += self.velocity_y

        self.hitbox.midbottom = self.rect.midbottom

        # Collion avec les plateformes
        for platform in platforms:
            if self.hitbox.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.hitbox.bottom = platform.rect.top
                    self.velocity_y = 0
                elif self.velocity_y < 0:
                    self.hitbox.top = platform.rect.bottom
                    self.velocity_y = 0

        self.rect.midbottom = self.hitbox.midbottom
        self.rect.y += 53

        """ IA du golem """
        
        # Blocage de l'attaque
        if self.is_attacking:
            self.velocity_x = 0
            if self.direction == 1:
                
                idx = self.anim_smash_right.gestion_animation() # "idx" = index de l'animation
                self.image = self.anim_smash_right.frames_droite[int(idx)]
                if self.played_sound == False:
                    random.choice(self.smash_sounds).play()  # jouer un son de smash random
                    self.played_sound = True  # Joue une fois
                if idx == 0: 
                    self.is_attacking = False
                    self.played_sound = False
            else:
                idx = self.anim_smash_left.gestion_animation()
                self.image = self.anim_smash_left.frames_droite[int(idx)]   
                if self.played_sound == False:
                    random.choice(self.smash_sounds).play()
                    self.played_sound = True
                if idx == 0: 
                    self.is_attacking = False
                    self.played_sound = False

        # Attaque quand le joueur est dans l'attack range, et bloque dans l'état d'attaque. le joueur prend du degat au moment de l'impact du smash de l'animation
        elif self.joueur_dans_attack(player_rect):
            temps_actuel = time.time()
            
            # Si le délai du cooldown est respecté, on lance l'attaque
            if temps_actuel - self.last_attack_time >= self.attack_cooldown:
                self.is_attacking = True
                self.has_dealt_damage = False      
                self.start_attack_time = temps_actuel  
                self.last_attack_time = temps_actuel
                self.velocity_x = 0
            else:
                self.velocity_x = 0
                self.image = self.anim_idle.frames_droite[int(self.anim_idle.gestion_animation())]

        # On vérifie le delai
        if self.is_attacking:
            self.velocity_x = 0
            if self.direction == 1:
                idx = self.anim_smash_right.gestion_animation()
                self.image = self.anim_smash_right.frames_droite[int(idx)]
                
                # degat a l'impact de l'animation
                if not self.has_dealt_damage and time.time() - self.start_attack_time >= 0.3:
                    if self.joueur_dans_attack(player_rect):
                        player.take_damage(self.attack_data, self.rect, self)
                    self.has_dealt_damage = True
                
                if idx == 0:
                    self.is_attacking = False
                    self.played_sound = False
            else:
                idx = self.anim_smash_left.gestion_animation()
                self.image = self.anim_smash_left.frames_droite[int(idx)]
                
                if not self.has_dealt_damage and time.time() - self.start_attack_time >= 0.4:
                    if self.joueur_dans_attack(player_rect):
                        player.take_damage(self.attack_data, self.rect, self)
                    self.has_dealt_damage = True
                
                if idx == 0:
                    self.is_attacking = False
                    self.played_sound = False
        # Poursuite
        elif self._joueur_dans_trigger(player_rect):
            if player_rect.centerx > self.rect.centerx:
                self.direction = 1
                self.rect.x += self.vitesse_deplacement
                self.image = self.anim_walk_right.frames_droite[int(self.anim_walk_right.gestion_animation())]
            elif self._joueur_dans_trigger(player_rect):
                dx = player_rect.centerx - self.rect.centerx
                if abs(dx) > 5:  # seuil de tolérance en pixels
                    if dx > 0:
                        self.direction = 1
                        self.rect.x += self.vitesse_deplacement
                        self.image = self.anim_walk_right.frames_droite[int(self.anim_walk_right.gestion_animation())]
                    else:
                        self.direction = -1
                        self.rect.x -= self.vitesse_deplacement
                        self.image = self.anim_walk_left.frames_droite[int(self.anim_walk_left.gestion_animation())]
                else:
                    self.image = self.anim_idle.frames_droite[int(self.anim_idle.gestion_animation())]  # ← idle si aligné
                
        # 4. IDLE
        else:
            self.image = self.anim_idle.frames_droite[int(self.anim_idle.gestion_animation())]
                

    def attack_special(self, player_rect, player):
        if self.joueur_dans_attack(player_rect):
            player.take_damage(self.attack_data, self.rect, self)

    def knockback(self, player_rect, player):
        recul_direction = -1 if player_rect.centerx > self.rect.centerx else 1
        self.velocity_x += 5 * recul_direction
        self.velocity_y = -5
        self.pv -= player.attack
        if self.pv <= 0:
            self.alive = False

    def draw(self, fenetre, camera):
        
        if not self.alive:
            return
        # Afficher simplement le sprite du golem
        fenetre.blit(self.image, camera.apply(self.rect))
        """
        # La hitbox en rouge
        pygame.draw.rect(fenetre, (255, 0, 0), camera.apply(self.hitbox), 2)
        
        # Le triggerbox en orange
        trigger_rect = pygame.Rect(
            self.hitbox.centerx - self.trigger_range,
            self.hitbox.centery - self.trigger_range,
            self.trigger_range * 2,
            self.trigger_range * 2
        )
        pygame.draw.rect(fenetre, (255, 165, 0), camera.apply(trigger_rect), 1)
        
        # La zone d'attaque en jaune
        attack_range_x = self.attack_range_x
        attack_range_y = self.attack_range_y
        if self.direction == 1:
            attack_rect = pygame.Rect(
                self.hitbox.right,
                self.hitbox.centery - attack_range_y // 2,
                attack_range_x,
                attack_range_y
            )
        else:
            attack_rect = pygame.Rect(
                self.hitbox.left - attack_range_x,
                self.hitbox.centery - attack_range_y // 2,
                attack_range_x,
                attack_range_y
            )
        pygame.draw.rect(fenetre, (255, 255, 0), camera.apply(attack_rect), 1)

        """