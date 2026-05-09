import pygame
from Entities.ennemi import Ennemi, Projectile, AttackZone
from Visual.sprite_sheet import VerticalAnimation
import random
from World.objets import Monnaie

"""class Golem(pygame.sprite.Sprite):  # pas de "self" ici
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
        self.anim_idle = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_idle_sheet.png', 40, 240, 240, 0, 0)
        self.anim_walk_right = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_walk_right_sheet.png', 32, 240, 240, 0, 0)
        self.anim_walk_left = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_walk_left_sheet.png', 32, 240, 240, 0, 0)
        self.anim_smash_right = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_smash_right_sheet.png', 12, 240, 240, 0, 0)
        self.anim_smash_left = VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_smash_left_sheet.png', 12, 240, 240, 0, 0)

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
        self.hitbox = pygame.Rect(0, 0, 70, 80)
        self.hitbox.center = self.rect.center
        
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
        
        #IA du golem

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
    NOT_TRIGGERED = "NOT_TRIGGERED"  # avant que le joueur soit détecté
    IDLE = "IDLE"
    ATTACKING   = "ATTACKING"
    TELEPORTING = "TELEPORTING"
    SHIELDED    = "SHIELDED"
    STAGGER     = "STAGGER"       # temps de repos après X dégâts
    TRANSITION  = "TRANSITION"    # changement de phase
    DYING       = "DYING"

    def __init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, pv_max, vitesse, attack_data, tp_points, stagger_threshold=150, scale=1):
        super().__init__(fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, pv_max, vitesse, attack_data, scale=1)
        
        self.can_receive_knockback = False # Pas de recul pour les boss
        self.sprite_inverted = False
        self.combat_lance = False
        self.dead = False #pour l'animation de mort

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

        self.hitboxs = []
        self.anims = {}
        self.current_anim = "idle"

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

        # Changement de phase
        if self.pv_ennemi < self.pv_max // 2 and self.phase == 1:
            self.enter_state(self.TRANSITION)

        #Mort
        if self.pv_ennemi <= 0 and self.state != self.DYING:
            self.enter_state(self.DYING)

    def hit_while_shielded(self):
        # Comportement spécifique lorsqu'il est touché avec un bouclier actif propre a chaque boss donc à redéfinir dans chaque classe de boss
        pass

    #Gestion des états

    def enter_state(self, new_state):
        self.state = new_state
        self.state_timer = pygame.time.get_ticks()
        self.atk_spawned = False
        if self.current_anim in self.anims:
            self.anims[self.current_anim].index_image = 0.0  # Réinitialiser l'animation à chaque changement d'état
            self.anims[self.current_anim].fin = False  # Réinitialiser le flag de fin d'animation
    
    def face_player(self, player_rect):
        if player_rect.centerx > self.rect.centerx:
            self.direction = 1
        else:
            self.direction = -1

    def teleport(self, index):
        x, y = self.tp_points[index]
        self.rect.midbottom = (x, y)
        self.position = pygame.math.Vector2(self.rect.centerx, self.rect.bottom)
        self.current_tp_index = index
        self.velocity = pygame.math.Vector2(0, 0) 

    def teleport_random(self):
        indices = list(range(len(self.tp_points)))
        if self.current_tp_index in indices:
            indices.remove(self.current_tp_index)  # éviter de se téléporter au même endroit
        self.teleport(random.choice(indices))

    #Animation
        
    def update_anim(self, once=False):
        anim = self.anims[self.current_anim]

        if once:
            anim.gestion_animation_once()
        else:
            anim.gestion_animation()

        index = int(anim.index_image)
        
        if self.direction == 1 and not self.sprite_inverted or self.direction != 1 and self.sprite_inverted:
            self.image = anim.frames_droite[index]
        else:
            self.image = anim.frames_gauche[index]

    def anim_over(self):
        anim = self.anims[self.current_anim]
        return anim.fin
    
    def speed(self, valeur_base, is_proj=False):
        # Augmente la vitesse de déplacement et d'animation en fonction de la phase
        if self.phase == 1:
            return valeur_base
        else :
            if is_proj:
                return valeur_base * 1.5
            return valeur_base / 1.3
    
    def scale_all_anims_speed(self, factor):
        for anims in self.anims.values():
            anims.vitesse_animation *= factor
        
    # Spawn et gestion des hitboxs

    def spawn_attack_zone(self, x, y, width, height, attack_data, image, duration):
        zone = AttackZone(x, y, width, height, attack_data, image, duration)
        self.hitboxs.append(zone)
        return zone

    def spawn_projectile(self, target_x, target_y, speed, width, height, damage, offset_x, offset_y, gravity=0.4, lifetime=3000, should_disappear_on_contact=True):
        projectile = Projectile(self.rect.centerx + offset_x, self.rect.centery + offset_y,
                                 target_x, target_y, speed, width, height, damage, gravity, lifetime, should_disappear_on_contact)
        self.hitboxs.append(projectile)

    def update_hitbox(self, platforms, limite_rect):
        for elem in self.hitboxs[:]:
            if hasattr(elem, "update"):
                delete = elem.update(platforms, limite_rect)
            else :
                delete = elem.lifetime_expired()
            if delete:
                self.hitboxs.remove(elem)
    
    # Etats génériques

    def update_stagger(self, elapsed):
        self.current_anim = "idle"
        if elapsed >= self.stagger_duration:
            self.enter_state(self.IDLE)

    def update_transition(self, elapsed):
        self.current_anim = "transition"
        if elapsed >= 2000:
            self.phase = 2
            self.scale_all_anims_speed(1.5)
            self.enter_state(self.TELEPORTING)

    def update_teleport(self, elapsed, player_rect):
        self.current_anim = "idle"
        if elapsed >= 500:
            self.teleport_random()
            self.face_player(player_rect)
            self.enter_state(self.IDLE)

    def update_dying(self, elapsed):
        self.current_anim = "death"
        self.update_anim(once=True)
        if self.anim_over() and elapsed > 500:
            self.alive = False
    
    #Affichage

    def draw(self, fenetre, camera):
        if not self.alive:
            return
        fenetre.blit(self.image, camera.apply(self.rect))
        for elem in self.hitboxs:
            elem.draw(fenetre, camera)

class Golem(Boss):
    ATK_SMASH = "smash"

    def __init__(self, fenetre, x, y):
        tp_points = [(x, y)]  
        super().__init__(
            fenetre, x, y,
            'Assets/Boss/golem/golem_idle_sheet.png',  
            40*2, 240*2, 240*2, 0, 0,
            pv_max=10,
            vitesse=1,
            attack_data={"damage": 1, "knockback_x": 100, "knockback_y": -5}, # Dégat au contact
            tp_points=tp_points,
            stagger_threshold=3,
            scale=1
        )

        # Variables principales
        self.use_gravity = True 
        self.can_receive_knockback = True # gestion du recul
        self.recul_intensite = 0.1
        self.orbs_value = 30
        self.vitesse_deplacement = 2

        self.arene_rect = pygame.Rect(-99999, -99999, 999999, 999999)
        
        self.orbs_value = 15
        
        self.scale = 0.5

        # Gestion hitbox
        self.rect = pygame.Rect(x, y, 70, 80)
        self.position = pygame.math.Vector2(self.rect.centerx, self.rect.bottom)
        self.sprite_offset_y = 500 

        # Triggerbox
        self.trigger_range = 250

        # Attack range
        self.attack_range_x = 57
        self.attack_range_y = 125
        
        # Cooldown d'attaque
        self.attack_cooldown = 2000  

        # Spriteheets, animations :
        v = 200
        self.anims = {
            "idle": VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_idle_sheet.png',       40, 240, 240, 0, 0),
            "walk_right": VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_walk_right_sheet.png', 32, 240, 240, 0, 0),
            "walk_left": VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_walk_left_sheet.png',  32, 240, 240, 0, 0),
            "smash_right": VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_smash_right_sheet.png',12, 240, 240, 0, 0),
            "smash_left": VerticalAnimation(fenetre, x, y, 'Assets/Boss/golem/golem_smash_left_sheet.png', 12, 240, 240, 0, 0),
        }

        for anim in self.anims.values():
            anim.frames_droite = [pygame.transform.scale(f, (int(240 * self.scale), int(240 * self.scale))) for f in anim.frames_droite]
            anim.frames_gauche = [pygame.transform.scale(f, (int(240 * self.scale), int(240 * self.scale))) for f in anim.frames_gauche]

        # Vitesses d'animation (divisé par 60 pour chaque frame)
        self.anims["idle"].vitesse_animation = 40 / v / 2
        self.anims["walk_right"].vitesse_animation = 32 / v / 1.5
        self.anims["walk_left"].vitesse_animation = 32 / v / 1.5
        self.anims["smash_right"].vitesse_animation = 12 / v * 2
        self.anims["smash_left"].vitesse_animation = 12 / v * 2

        # Affichage de base
        self.current_anim = "idle"
        self.image = self.anims["idle"].frames_droite[0]

        # Sons
        self.smash_sounds = [
            pygame.mixer.Sound('Assets/Sounds/golem_smash_sound1.MP3'),
            pygame.mixer.Sound('Assets/Sounds/golem_smash_sound2.MP3')
        ]
        self.death_sound = pygame.mixer.Sound('Assets/Sounds/golem_death.MP3')
        self.smash_played_sound = False
        self.death_sound_played = False

        self.combat_lance = False
        self.enter_state(self.NOT_TRIGGERED)

    def receive_hit(self, attack_data, source_rect, source):
        if not self.alive:
            return

        self.pv_ennemi -= attack_data["damage"]

        # petit knockback
        if source_rect.centerx < self.rect.centerx:
            self.velocity.x = 3
        else:
            self.velocity.x = -3

        if self.pv_ennemi <= 0:
            self.alive = False
            Monnaie.orbs += self.orbs_value

            if not self.death_sound_played:
                self.death_sound.play()
                self.death_sound_played = True

    def _zone_smash(self):
        if self.direction == 1:
            return pygame.Rect(self.rect.right, self.rect.centery - self.attack_range_y // 2,
                               self.attack_range_x, self.attack_range_y)
        return pygame.Rect(self.rect.left - self.attack_range_x, self.rect.centery - self.attack_range_y // 2,
                           self.attack_range_x, self.attack_range_y)

    def _joueur_dans_attack(self, player_rect):
        return self._zone_smash().colliderect(player_rect)

    def _update_anim(self, key):
        anim = self.anims[key]
        idx = int(anim.gestion_animation())
        
        if "left" in key:
            self.image = anim.frames_droite[idx]
        elif "right" in key:
            self.image = anim.frames_droite[idx]
        else:
            self.image = anim.frames_droite[idx] if self.direction == 1 else anim.frames_gauche[idx]

    def update(self, player_rect, player, platforms=[]):
        now = pygame.time.get_ticks()
        elapsed = now - self.state_timer

        if not self.alive:
            return

        # IA du golem
        if self.state == self.NOT_TRIGGERED:
            if self.dans_trigger(player_rect, self.trigger_range): 
                self.combat_lance = True
                self.enter_state(self.IDLE)

        elif self.state == self.IDLE:
            self.update_idle(elapsed, player_rect)

        elif self.state == self.ATTACKING:
            self.update_attack(elapsed, player_rect, player)

        elif self.state == self.DYING:
            self.update_dying(elapsed)

        # Gravité et physique
        if self.state == self.IDLE and abs(self.velocity.x) < self.vitesse_deplacement:
            self.velocity.x = self.vitesse_deplacement * self.direction
        elif self.state == self.ATTACKING:
            # On laisse le recul agir un peu même pendant l'attaque, mais on freine fort
            self.velocity.x *= 0.9 
        
        # Collion avec les plateformes
        self.physics_update(platforms)  

        self.update_hitbox(platforms, self.arene_rect)

    def update_idle(self, elapsed, player_rect):
        # Idle
        self.face_player(player_rect)

        if self._joueur_dans_attack(player_rect):
            now = pygame.time.get_ticks()
            if now - self.state_timer >= self.attack_cooldown:
                self.current_attack = self.ATK_SMASH
                self.enter_state(self.ATTACKING)
                return

        # Poursuite
        dx = player_rect.centerx - self.rect.centerx
        if abs(dx) > 5:
            key = "walk_right" if self.direction == 1 else "walk_left"
        else:
            key = "idle"

        self._update_anim(key)

    def update_attack(self, elapsed, player_rect, player):
        key = "smash_right" if self.direction == 1 else "smash_left"
        self._update_anim(key)

        if not self.smash_played_sound:
            import random
            random.choice(self.smash_sounds).play()
            self.smash_played_sound = True

        if elapsed >= 350 and not self.atk_spawned:
            atk = AttackZone(
                x=self._zone_smash().x,
                y=self._zone_smash().y,
                width=self.attack_range_x,
                height=self.attack_range_y,
                attack_data=self.attack_data,
                image=None,
                duration=200
            )
            self.hitboxs.append(atk)
            self.atk_spawned = True

        if elapsed >= 1200:
            self.smash_played_sound = False
            self.enter_state(self.IDLE)

    def update_dying(self, elapsed):
        # meurt
        self.alive = False # fait disparaitre le sprite
        Monnaie.add_orbs(self.orbs_value)
        if not self.death_sound_played:
            self.death_sound.play()
            self.death_sound_played = True
    
    def mort(self):
        self.alive = False
        return True

    def draw(self, fenetre, camera):
        if not self.alive:
            return

        # Technique pour aligner le spirte avec la hitbox
        visual_rect = self.image.get_rect(midbottom=(self.rect.centerx, self.rect.bottom + 25))
        fenetre.blit(self.image, camera.apply(visual_rect))
        """
        for elem in self.hitboxs:
            elem.draw(fenetre, camera)

        pygame.draw.rect(fenetre,(255,0,0),camera.apply(self.rect),2)

        # La hitbox en rouge
        pygame.draw.rect(fenetre, (255, 0, 0), camera.apply(self.rect), 2)
        
        # triggerbox en orange
        trigger_rect = pygame.Rect(
            self.rect.centerx - self.trigger_range,
            self.rect.centery - self.trigger_range,
            self.trigger_range * 2,
            self.trigger_range * 2
        )
        pygame.draw.rect(fenetre, (255, 165, 0), camera.apply(trigger_rect), 2)
        
        # zone d'attaque en jaune
        pygame.draw.rect(fenetre, (255, 255, 0), camera.apply(self._zone_smash()), 2)
        """