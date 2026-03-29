import pygame
from Entities.ennemi import Ennemi, Projectile, AttackZone
from Visual.sprite_sheet import VerticalAnimation, Animation
from World.map import platforms
import time
import random
import math
from World.objets import Monnaie

class Golem(pygame.sprite.Sprite):  # pas de "self" ici
    def __init__(self, fenetre, x, y):
        super().__init__()
        self.ecran = fenetre

    # Variables principales
        self.pv = 10
        self.alive = True
        self.direction = 1
        self.orbs_value = 30
        self.shake = 0

        # Spriteheets, animations :
        self.anim_idle = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_idle_sheet.png',        40, 240, 240, 0, 0)
        self.anim_walk_right = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_walk_right_sheet.png',  32, 240, 240, 0, 0)
        self.anim_walk_left = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_walk_left_sheet.png',   32, 240, 240, 0, 0)
        self.anim_smash_right = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_smash_right_sheet.png', 12, 240, 240, 0, 0)
        self.anim_smash_left = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_smash_left_sheet.png',  12, 240, 240, 0, 0)

        # Sons
        self.sound_smash1 = pygame.mixer.Sound('Assets/Sounds/golem_smash_sound1.MP3')
        self.sound_smash2 = pygame.mixer.Sound('Assets/Sounds/golem_smash_sound2.MP3')
        self.smash_sounds = [self.sound_smash1, self.sound_smash2]        
        self.smash_played_sound = False # flag pour pas que le son se joue chaque frames

        self.death_sound = pygame.mixer.Sound('Assets/Sounds/golem_death.MP3')
        self.death_sound_played = False

        v = 120
        # Vitesses d'animation (divisé par 60 pour chaque frame)
        self.anim_idle.vitesse_animation = 40 / v /2
        self.anim_walk_right.vitesse_animation = 32 / v /1.5 # plus lent
        self.anim_walk_left.vitesse_animation = 32 / v /1.5
        self.anim_smash_right.vitesse_animation = 12 / v * 2 # plus rapide
        self.anim_smash_left.vitesse_animation = 12 / v * 2

        # Affichage de base
        self.image = self.anim_idle.frames_droite[0]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Position et vitesse initiales
        self.sprite_offset_y = 53
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
        
        """ IA du golem """
        if self.is_attacking:
            self.velocity_x = 0
            if self.direction == 1:
                idx = self.anim_smash_right.gestion_animation()  # 1 fois
                self.image = self.anim_smash_right.frames_droite[int(idx)]
                
                if not self.smash_played_sound:
                    random.choice(self.smash_sounds).play()
                    self.smash_played_sound = True

                if not self.has_dealt_damage and time.time() - self.start_attack_time >= 0.35:
                    self.shake = 17
                    if self.joueur_dans_attack(player_rect):
                        player.take_damage(self.attack_data, self.rect, self)
                    self.has_dealt_damage = True

                if idx == 0:
                    self.is_attacking = False
                    self.smash_played_sound = False

            else:  # direction == -1
                idx = self.anim_smash_left.gestion_animation()
                self.image = self.anim_smash_left.frames_droite[int(idx)]

                if not self.smash_played_sound:
                    random.choice(self.smash_sounds).play()
                    self.smash_played_sound = True
                    

                if not self.has_dealt_damage and time.time() - self.start_attack_time >= 0.35:
                    self.shake = 17
                    if self.joueur_dans_attack(player_rect):
                        player.take_damage(self.attack_data, self.rect, self)
                    self.has_dealt_damage = True

                if idx == 0:
                    self.is_attacking = False
                    self.smash_played_sound = False

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
                
        # Idle
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
        if self.pv <= 0: # meurt
            self.alive = False
            Monnaie.orbs += self.orbs_value
            if not self.death_sound_played:
                self.death_sound.play()
                self.death_sound_played = True

    def draw(self, fenetre, camera):
        
        if not self.alive:
            return
        # Afficher simplement le sprite du golem
        visual_rect = self.rect.move(0, self.sprite_offset_y)
        fenetre.blit(self.image, camera.apply(visual_rect))

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

class Boss(Ennemi):
    #Etats généraiques à tous les boss
    IDLE = "IDLE"
    ATTACKING   = "ATTACKING"
    TELEPORTING = "TELEPORTING"
    SHIELDED    = "SHIELDED"
    STAGGER     = "STAGGER"       # temps de repos après X dégâts
    TRANSITION  = "TRANSITION"    # changement de phase
    DYING       = "DYING"

    def __init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, pv_max, vitesse, attack_data, tp_points, stagger_threshold=150):
        super().__init__(fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, pv_max, vitesse, attack_data)
        
        self.can_receive_knockback = False # Pas de recul pour les boss

        self.phase = 1
        self.state = self.IDLE
        self.state_timer = pygame.time.get_ticks()
        self.current_attack = None
        self.is_attacking = False
        self.attack_rect = pygame.Rect(0, 0, 0, 0)

        self.tp_points = tp_points
        self.current_tp_index = 0

        self.stagger_threshold = stagger_threshold
        self.pv_last_stagger = pv_max
        self.stagger_duration = 3000 # 3 secondes de pause après le seuil de dégâts

        self.projectiles = []

    def receive_hit(self, attack_data, source_rect, source):

        if not self.alive:
            return
            
        if self.is_shielded:
            self.hit_while_shielded()
            return
            
        super().receive_hit(attack_data, source_rect, source)

        # Stagger
        if self.pv_last_stagger - self.pv_ennemi >= self.stagger_threshold:
            self.enter_state(self.STAGGER)
            self.pv_last_stagger = self.pv_ennemi

        # Transition de phase à 50% de PV
        if self.pv_ennemi <= self.pv_max // 2 and self.phase == 1:
            self.enter_state(self.TRANSITION)

        #Mort 
        if self.pv_ennemi <= 0:
            self.enter_state(self.DYING)

    def hit_while_shielded(self):
        # Comportement spécifique lorsqu'il est touché avec un bouclier actif propre a chaque boss donc à redéfinir dans chaque classe de boss
        pass

    #Gestion des états

    def enter_state(self, new_state):
        self.state = new_state
        self.state_timer = pygame.time.get_ticks()

    def teleport(self, index):
        x, y = self.tp_points[index]
        self.rect.midbottom = (x, y)
        self.position = pygame.math.Vector2(self.rect.centerx, self.rect.bottom)
        self.current_tp_index = index
        self.velocity = pygame.math.Vector2(0, 0) 

    def teleport_random(self):
        indices = list(range(len(self.tp_points)))
        indices.remove(self.current_tp_index)  # éviter de se téléporter au même endroit
        self.teleport(random.choice(indices))

    def face_player(self, player_rect):
        if player_rect.centerx > self.rect.centerx:
            self.direction = 1
        else:
            self.direction = -1

    # Projectiles et affichage

    def update_projectiles(self, limite_rect):
        for proj in self.projectiles[:]:
            proj.update()
            if proj.out_of_bounds(limite_rect) or proj.lifetime_expired():
                self.projectiles.remove(proj)

    def draw(self, fenetre, camera):
        if not self.alive:
            return
        fenetre.blit(self.image, camera.apply(self.rect))
        for proj in self.projectiles:
            proj.draw(fenetre, camera)

class Gravelion(Boss):

    #Indices points de téléportation
    SOL_GAUCHE = 0
    SOL_DROIT = 1
    AIR_GAUCHE = 2
    AIR_DROIT = 3

    #Noms des attaques :
    ATK_MELEE       = "melee"
    ATK_ARM         = "arm"
    ATK_LASER       = "laser"
    ATK_COCON       = "cocon"

    def __init__(self, fenetre,x, y, arene_rect):
        marge_x = 150
        hauteur_air = arene_rect.top + 100
        tp_points = [
            (arene_rect.left + marge_x, arene_rect.bottom),
            (arene_rect.right - marge_x, arene_rect.bottom),
            (arene_rect.left + marge_x, hauteur_air),
            (arene_rect.right - marge_x, hauteur_air)
        ]
        super().__init__(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 4, 400, 100, 0, 0, 500, 1,\
                        {"damage": 1, "knockback_x": 80, "knockback_y": -5}, tp_points)

        self.arene_rect = arene_rect
        self.use_gravity = False # Pas de gravité pour ce boss lévitant

        # Animations 
        self.anims = {
            "idle":         Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 4, 400, 100, 0, 0),
            "glowing":      Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 8, 800, 200, 0, 1),
            "arm":          Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 9, 900, 300, 0, 2),
            "cocon":        Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 8, 800, 400, 0, 3),
            "melee":        Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 7, 700, 500, 0, 4),
            "laser_charge": Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 7, 700, 600, 0, 5),
            "transition":   Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 10, 1000, 700, 0, 6),
            "death":        Animation(fenetre, x, y, "Assets/Boss/Gravelion/Gravelion_sprite_sheet.png", 14, 1000, 900, 0, 7) #Probleme avec la classe a regler pour fonctionner sur deux lignes
        }

        #Vitesse d'animation 
        v = 60
        self.anims["idle"].vitesse_animation = 4 / v / 2
        self.anims["glowing"].vitesse_animation = 8 / v
        self.anims["arm"].vitesse_animation = 9 / v * 1.5
        self.anims["cocon"].vitesse_animation = 8 / v 
        self.anims["melee"].vitesse_animation = 7 / v * 1.5
        self.anims["laser_charge"].vitesse_animation = 7 / v 
        self.anims["transition"].vitesse_animation = 10 / v / 2
        self.anims["death"].vitesse_animation = 14 / v / 3

        self.current_anim = "idle"
        self.image = self.anims["idle"].frames_droite[0]
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.hitbox = self.rect.inflate(40, -20)

        # Timers et variables d'attaque
        self.idle_duration = 1500
        self.is_attacking = False
        self.cocon_punish = False
        self.cocon_chance = 1/6
        self.laser = None


        #Spawn 
        self.enter_state(self.IDLE)
        self.teleport(self.SOL_GAUCHE)

    def on_ground(self, index):
        return index in [self.SOL_GAUCHE, self.SOL_DROIT]
    
    def speed(self, valeur_base):
        # Augmente la vitesse de déplacement et d'animation en fonction de la phase
        if self.phase == 1:
            return valeur_base
        elif self.phase == 2:
            return valeur_base * 1.5
        
    def update_anim(self):
        anim = self.anims[self.current_anim]
        anim.gestion_animation()
        if self.direction == 1 :
            self.image = anim.frames_droite[int(anim.index_image)]
        else:
            self.image = anim.frames_gauche[int(anim.index_image)]

    def anim_over(self):
        # Vrai si l'index de l'animation actuelle a bouclé (retourné à 0 après avoir atteint la fin)
        return self.anims[self.current_anim].index_image < self.anims[self.current_anim].vitesse_animation
    
    def choose_attack(self, player_rect):
        distance = abs(player_rect.centerx - self.rect.centerx)
        au_sol = self.on_ground(self.current_tp_index)

        cocon_chance = 1/3 if self.phase == 2 else self.cocon_chance
        if random.random() < cocon_chance:
            return self.ATK_COCON
        
        if not au_sol:
            return random.choice([self.ATK_LASER, self.ATK_ARM])
        if distance < 200:
            return self.ATK_MELEE
        return random.choice([self.ATK_MELEE, self.ATK_ARM])
    
    #Contre-attaque cocon
    def hit_while_shielded(self):
        self.cocon_punish = True

    def update(self, player_rect, player):
        now = pygame.time.get_ticks()
        elapsed = now - self.state_timer

        self.face_player(player_rect)
        self.update_anim()

        if self.state == self.IDLE:
            self.update_idle(elapsed, player_rect)

        elif self.state == self.ATTACKING:
            self.update_attack(elapsed, player_rect)

        elif self.state == self.TELEPORTING:
            self.update_teleport(elapsed, player_rect)

        elif self.state == self.SHIELDED:
            self.update_cocon(elapsed, player_rect, player)

        elif self.state == self.STAGGER:
            self.update_stagger(elapsed)

        elif self.state == self.TRANSITION:
            self.update_transition(elapsed)

        elif self.state == self.DYING:
            self.update_dying(elapsed)

        if self.laser:
            now = pygame.time.get_ticks()
            self.laser.rect.x += self.laser.speed_x
            if now - self.laser.birth_time >= self.laser.lifetime:
                self.laser = None
                self.enter_state(self.TELEPORTING)

        self.update_projectiles(self.arene_rect)
        self.hitbox.midbottom = self.rect.midbottom

    # ETATS

    def update_idle(self, elapsed, player_rect):
        if elapsed >= self.speed(self.idle_duration):
            self.current_attack = self.choose_attack(player_rect)
            if self.current_attack == self.ATK_COCON:
                self.enter_state(self.SHIELDED)
            else:
                self.enter_state(self.ATTACKING)
        
    def update_attack(self, elapsed, player_rect):
        attack = self.current_attack

        if attack == self.ATK_MELEE:
            self.attack_melee(elapsed)
        elif attack == self.ATK_ARM:
            self.attack_arm(elapsed, player_rect)
        elif attack == self.ATK_LASER:
            head = self.rect.midtop + pygame.math.Vector2(0, 20)
            self.attack_laser(elapsed, head)

    def update_cocon(self, elapsed, player_rect, player):
        self.current_anim = "cocon"
        self.is_shielded = True # Pour ne pas prendre de dégats pendant le cocon

        if self.cocon_punish:
            # Si le joueur touche le cocon, il subit une contre-attaque
            self.cocon_punish = False 
            self.is_shielded = False
            self.position.x = player.position.x - 100 * player.direction # Se téléporte dans le dos du joeur
            self.rect.midbottom = (self.position.x, self.position.y)
            self.face_player(player_rect)
            self.current_attack = self.ATK_MELEE
            self.enter_state(self.ATTACKING)
            return
        
        if elapsed >= 1500:
            #Fin du cocon sans etre frappé
            self.is_shielded = False
            self.enter_state(self.TELEPORTING)
        
    def update_stagger(self, elapsed):
        self.current_anim = "glowing"
        if elapsed >= self.stagger_duration:
            self.enter_state(self.IDLE)

    def update_transition(self, elapsed):
        self.current_anim = "transition"
        if elapsed >= 2000:
            self.phase = 2
            self.enter_state(self.TELEPORTING)

    def update_teleport(self, elapsed, player_rect):
        if elapsed >= 500:
            self.teleport_random()
            self.face_player(player_rect)
            self.enter_state(self.IDLE)

    def update_dying(self, elapsed):
        self.current_anim = "death"
        if self.anim_over() and elapsed > 500:
            self.alive = False

    #ATTAQUES
    def attack_melee(self, elapsed):
        self.current_anim = "melee"
        charge = self.speed(600)
        if elapsed >= charge :
            onde = Projectile(
                x=self.rect.centerx + self.direction * 50,
                y=self.rect.bottom -30,
                target_x=self.arene_rect.right if self.direction == 1 else self.arene_rect.left,
                target_y=self.rect.bottom -30,
                speed=self.speed(10),
                width=30,
                height=30,
                damage=2,
                lifetime=6000,
                disappear_on_contact=False,
            )
            self.projectiles.append(onde)
        
        if elapsed >= charge + 800:
            self.enter_state(self.TELEPORTING)

    def attack_arm(self, elapsed, player_rect):
        self.current_anim = "arm"
        charge = self.speed(500)
        pos_x = self.rect.centerx + self.direction * 60
        pos_y = self.rect.centery - 30
        if elapsed >= charge :
            self.attack_rect = AttackZone(
                x=self.rect.centerx+20,
                y=self.rect.right,
                width=70, height=100,
                attack_data={"damage": 1, "knockback_x": 40, "knockback_y": -10},
                image=None
                )
        
            bras = Projectile(
                pos_x, pos_y,
                target_x=player_rect.centerx,
                target_y=player_rect.centery,
                speed=self.speed(8),
                width=30,
                height=15,
                damage=1,
                lifetime=3000,
            )
            self.projectiles.append(bras)
        
        if elapsed >= charge + 800:
            self.enter_state(self.TELEPORTING)

    def attack_laser(self, elapsed, head):
        self.current_anim = "laser_charge"
        charge = self.speed(1000)

        if self.laser is None and elapsed >= charge:
            self.laser = AttackZone(
                x=head.x,
                y=head.y,
                width=10,
                height=200,
                attack_data={"damage": 2, "knockback_x": 80, "knockback_y": -2},
                image=None
            )
            self.laser.rect.midtop = (head.x, head.y)
            if elapsed >= charge + 600:
                self.enter_state(self.TELEPORTING)

    def draw(self, fenetre, camera):
        if not self.alive:
            return
        fenetre.blit(self.image, camera.apply(self.rect))
        if self.laser:
            fenetre.blit(self.laser.image, camera.apply(self.laser.rect))
        for proj in self.projectiles:
            proj.draw(fenetre, camera)


