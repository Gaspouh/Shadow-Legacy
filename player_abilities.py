import pygame

class Dash:
    def __init__(self):
        self.unlocked = True # Permet de débloquer le dash plus tard dans le jeu

        self.vitesse_dash = 80
        self.duree = 100
        self.cooldown = 1000

        self.in_use = False
        self.dash_timer = 0
        self.last_dash = -1000

    def start_dash(self, player):
        now = pygame.time.get_ticks()
        
        if not self.unlocked: # empeche d'executer le dash avant son obtention
            return False
        
        if not self.in_use and now - self.last_dash >= self.cooldown:
            self.in_use = True
            self.dash_timer = now
            self.last_dash = now
            
            keys = pygame.key.get_pressed()
            self.is_dash_down = keys[pygame.K_s] and not player.on_ground
            return True
        return False
    
    def update(self, player):
        if self.in_use:
            now = pygame.time.get_ticks()
            if now - self.dash_timer > self.duree:
                self.in_use = False
                player.velocity.x *= 0.5 # Ralentir le joueur après le dash
                player.velocity.y *= 0.7
            else :
                if self.is_dash_down:
                    player.velocity.x = 0 # Ne pas permettre au joueur de se déplacer horizontalement pendant le dash vers le bas
                    player.velocity.y = self.vitesse_dash*0.3 # Appliquer la vitesse de dash vers le bas plus lente vers le bas car il n'y a pas de force qui compense le dash sur l'axe des y
                else:
                    player.velocity.x = self.vitesse_dash * player.direction # Appliquer la vitesse de dash dans la direction du joueur
                    player.velocity.y = 0 # Ne pas permettre au joueur de monter ou descendre pendant le dash5

class Double_jump:
    def __init__ (self):
        self.unlocked = True # Permet de débloquer le double saut plus tard dans le jeu

        self.strength = -12
        self.used= False
    
    def reset(self): # Appelé quand le joueur touche le sol ou fait un pogo
        self.used = False
    
    def can_execute(self, player) :
        if self.unlocked and not self.used and not player.on_ground:
            return True
        return False
