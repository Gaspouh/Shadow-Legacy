import pygame
from Visual.sprite_sheet import *
 
class Coeur(Animation):
    def __init__(self, fenetre, x, y):
        super().__init__(fenetre, x, y, 'Assets/Images/coeur2.png', 8, 88, 88, 0, 2, scale=1)
        self.state = "ALIVE"
        self.vitesse_animation = 0.3

        self.frames_droite = [
            pygame.transform.smoothscale(frame, (70,70)) 
            for frame in self.frames_droite
        ]
        self.frames_gauche = self.frames_droite.copy()

        self.image = self.frames_droite[0]
       
    def update(self, current_player_health, heart_index):

        # on compare l'index du cœur avec la santé actuelle du joueur pour déterminer l'état du cœur
        if heart_index >= current_player_health and self.state == "ALIVE":
            # on enlève un cœur si la santé du joueur diminue
            self.state = "DYING"
            self.index_image = 0  # On reset l'anim pour jouer la séquence de mort
        
        # on ajoute un coeur si la santé du joueur augmente
        elif heart_index < current_player_health and self.state != "ALIVE":
            self.state = "ALIVE"
            self.image = self.frames_droite[0] 
        
        # on laisse le coeur vivant
        if self.state == "ALIVE":
            self.image = self.frames_droite[0] 
        
        # on joue l'animation de mort du cœur
        elif self.state == "DYING":
            self.index_image += self.vitesse_animation

            if self.index_image < len(self.frames_droite):
                self.image = self.frames_droite[int(self.index_image)]
            else:
                self.state = "DEAD"
                self.image = self.frames_droite[-1]  # Afficher le cœur vide une fois l'animation terminée
                
        # on affiche un cœur vide si le cœur est mort
        elif self.state == "DEAD":
           self.image = self.frames_droite[-1]  
            
class Monnaie:
    global orbs
    orbs = 0 # Globale
    def __init__(self, fenetre, x, y):
        self.fenetre = fenetre

        self.image = pygame.image.load("Assets/Images/orbs.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (55, 55))
        self.font = pygame.font.SysFont("Playfair Display", 60, bold=True)
        self.rect = self.image.get_rect(topright=(fenetre.get_width() - 50, 50))

    @staticmethod   # permet de rendre global
    def add_orbs(amount):
        Monnaie.orbs += amount

    def draw(self, fenetre):
        self.rect = self.image.get_rect(topright=(fenetre.get_width() - 50, 50))
        texte = str(Monnaie.orbs)

        # effet de brillance, on décale autour du texte pour créer un halo + blit vertical pour que ça recouvre tout le texte (halo)
        for ox in range(-8, 9, 3):
            for oy in range(-8, 9, 3):
                glow_surf = self.font.render(texte, True, (210, 225, 255)) # version plus "bleu"
                glow_surf.set_alpha(11) # Fondue plus moins forte
                fenetre.blit(glow_surf, (self.rect.left - glow_surf.get_width() - 8 + ox,
                    self.rect.centery - glow_surf.get_height() // 2 + oy))


        # Texte en blanc
        texte_surf = self.font.render(texte, True, (255, 255, 255))
        fenetre.blit(texte_surf, (self.rect.left - texte_surf.get_width() - 8,
                                   self.rect.centery - texte_surf.get_height() // 2))

        # Image orb à droite
        fenetre.blit(self.image, self.rect)

