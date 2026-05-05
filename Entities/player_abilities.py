import pygame
from Core.save import load_config
from Entities.ennemi import Projectile

class Dash:
    def __init__(self, cfg={}): #cfg signifie "configuration"
        self.unlocked = True # Permet de débloquer le dash plus tard dans le jeu

        cfg_dash = cfg if cfg else load_config()["abilities"]["dash"]

        self.vitesse_dash = cfg_dash.get("vitesse_dash", 80)
        self.duree        = cfg_dash.get("duree", 100)
        self.cooldown     = cfg_dash.get("cooldown", 1000)

        self.in_use = False
        self.dash_timer = 0
        self.last_dash = -1000
        self.dash_invincible = False # Flag pour savoir si l'invincibilité vient du dash

    def start_dash(self, player):
        now = pygame.time.get_ticks()
        
        if not self.unlocked: # empeche d'executer le dash avant son obtention
            return False
        
        if not self.in_use and now - self.last_dash >= self.cooldown:
            self.in_use = True
            self.dash_timer = now
            self.last_dash = now
            self.dash_direction = player.direction
            
            keys = pygame.key.get_pressed()
            self.is_dash_down = keys[pygame.K_s] and not player.on_ground

            # Invincibilité juste pour le dash vers le bas
            if self.is_dash_down:
                player.invincible = True
                self.dash_invincible = True

            return True
        return False
    
    def update(self, player):
        if self.in_use:
            now = pygame.time.get_ticks()
            if now - self.dash_timer > self.duree:
                self.in_use = False
                player.velocity.y *= 0.7

                # Retirer l'invincibilité du dash seulement si c'est le dash qui l'avait activée
                # (et non une invincibilité due à des dégâts reçus)
                if self.dash_invincible:
                    player.invincible = False
                    self.dash_invincible = False

            else :
                if self.is_dash_down:
                    player.velocity.x = 0 # Ne pas permettre au joueur de se déplacer horizontalement pendant le dash vers le bas
                    player.velocity.y = self.vitesse_dash*0.3 # Appliquer la vitesse de dash vers le bas plus lente vers le bas car il n'y a pas de force qui compense le dash sur l'axe des y
                else:
                    player.velocity.x = (self.vitesse_dash*0.3 if player.on_ice else self.vitesse_dash) * self.dash_direction # Appliquer la vitesse de dash dans la direction du joueur (diminuée si joueur est sur de la glace)
                    player.velocity.y = 0 # Ne pas permettre au joueur de monter ou descendre pendant le dash

class Double_jump:
    def __init__(self, cfg={}):
        self.unlocked = True # Permet de débloquer le double saut plus tard dans le jeu

        cfg_dj = cfg if cfg else load_config()["abilities"]["double_jump"]

        self.strength = cfg_dj.get("strength", -12)
        self.used = False
    
    def reset(self): # Appelé quand le joueur touche le sol ou fait un pogo
        self.used = False
    
    def can_execute(self, player) :
        if self.unlocked and not self.used and not player.on_ground:
            return True
        return False

class sort:
    def __init__(self):
        self.cost = 33 # Coût en sang pour utiliser le sort
        
    def use(self, player, projectiles):
        if player.sang >= self.cost: # Vérifie que le joueur a assez de sang pour utiliser le sort
            player.sang -= self.cost # Consomme du sang
            direction = player.direction
            x = player.rect.centerx + (direction * 30)
            y = player.rect.centery - 20 # pour éviter la collision avec le sol
            target_x = x + (direction * 1000)  # tire loin devant
            target_y = y
            projectile = Projectile(x, y, target_x, target_y, 15, 80, 80, 3, image=pygame.image.load('Assets/Images/sort.png').convert_alpha())
            projectiles.append(projectile)
            return True
        return False

class soin:
    def __init__(self):
        self.cost = 44 # Coût en sang pour utiliser le soin
        self.heal_amount = 1 # Quantité de santé restaurée par le soin
        self.clock = 0 # Horloge pour gérer le cooldown du soin
        self.cooldown = 1000 # Cooldown du soin en millisecondes
        self.last_heal_time = -5000 # Temps du dernier soin
        self.is_healing = False # pour indiquer si le soin est en cours d'utilisation
        self.timer_soin = 0 # Timer pour gérer la durée du soin
        self.duree_soin = 2000 # Durée pendant laquelle le joueur est étourdi après avoir utilisé le soin 
        
    def use(self, player):
        now = pygame.time.get_ticks()
        if player.sang >= self.cost and player.health < player.max_health and now - self.last_heal_time >= self.cooldown: # Vérifie que le joueur a assez de sang et n'est pas déjà à pleine santé
            self.is_healing = True
            self.timer_soin = now # Démarre le timer du soin
            player.stun_timer = now # Le joueur est étourdi pendant la durée du cooldown du soin
            player.stun_duration = 3000 # Le joueur est étourdi après avoir utilisé le soin

    def update(self, player):
            if not self.is_healing:
                return
            
            now = pygame.time.get_ticks()

            if now - self.timer_soin >= self.duree_soin: # Vérifie que le cooldown est écoulé
                    player.sang -= self.cost # Consomme du sang
                    player.health = min(player.health + self.heal_amount, player.max_health) # Restaure la santé du joueur sans dépasser le maximum
                    self.last_heal_time = now # Met à jour le temps du dernier soin
                    self.is_healing = False # Réinitialise l'état de soin
                    self.timer_soin = 0 # Réinitialise le timer du soin