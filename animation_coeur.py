import pygame
 
class Coeur(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 135   # Largeur: 676 / 5 frames
        self.height = 95  # Hauteur d'une rangée
        self.row = 1       # Utiliser la 2e rangée (index 1)
        
        # Chargement de la planche de sprite
        self.sheet = pygame.image.load('coeur.png').convert_alpha()
        
        # Découpage des frames de l'animation à partir de la sprite sheet
        self.frames = [self.get_frame(i) for i in range(5)]
        
        # Configuration de l'état
        self.state = "ALIVE"
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # variables d'animation
        self.index_anim = 0.0
        self.vitesse_animation = 0.15

    def get_frame(self, index):
        """Découpe une image précise dans la planche de sprites."""
        frame = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Extraire de la ligne 2 avec un petit offset pour éviter le débordement
        y_offset = self.row * self.height + 80
        frame.blit(self.sheet, (0, 0), (index * self.width, y_offset, self.width, self.height))

        # Redimensionner à 100x100 pour l'affichage
        frame_redimensionnee = pygame.transform.smoothscale(frame, (100, 100))
        return frame_redimensionnee

    def update(self, current_player_health, heart_index):
        # on compare l'index du cœur avec la santé actuelle du joueur pour déterminer l'état du cœur
        if heart_index >= current_player_health and self.state == "ALIVE":
            # on enlève un cœur si la santé du joueur diminue
            self.state = "DYING"
            self.index_anim = 0  # On reset l'anim pour jouer la séquence de mort
        
        # on ajoute un coeur si la santé du joueur augmente
        elif heart_index < current_player_health and self.state != "ALIVE":
            self.state = "ALIVE"
        
        # on laisse le coeur vivant
        if self.state == "ALIVE":
            self.index_anim += self.vitesse_animation
            self.image = self.frames[0]
        
        # on joue l'animation de mort du cœur
        elif self.state == "DYING":
            self.index_anim += self.vitesse_animation
            if self.index_anim < len(self.frames):
                self.image = self.frames[int(self.index_anim)]
            else:
                self.state = "DEAD"
                
        # on affiche un cœur vide si le cœur est mort
        elif self.state == "DEAD":
            self.image = self.frames[-1] # Frame du cœur vide
