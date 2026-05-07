import pygame
from Visual.sprite_sheet import Animation

class Marchand:
    def __init__(self, fenetre, x, y):
        
        self.image = pygame.image.load('Assets/Images/marchand.png').convert_alpha()
        self.animation = Animation(fenetre, x, y, 'Assets/Images/marchand.png', 7, 62, 50, 5, 0, scale=1)
        self.rect = self.animation.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.produits = {
            "receptacle": {"prix": 100, "stock": 5},
            "charme_jump": {"prix": 50, "stock": 1},
            "charme_vitesse": {"prix": 30, "stock": 1}
        }

        self.catalogue_rects = {}

    def update(self):
        self.animation.gestion_animation()

    def acheter(self, player, fenetre):
        # Logique d'achat du marchand
        x,y = self.rect.topleft
        font = pygame.font.Font(None, 36)
        i = 0
         
        for item in self.produits:

            rect = pygame.Rect(x, y + i * 60, 200, 50)
            i += 1
            pygame.draw.rect(fenetre, (50, 50, 50), rect)
            pygame.draw.rect(fenetre, (255, 255, 255), rect, 2)

            texte = font.render(f"{item} - {self.produits[item]['prix']}g (x{self.produits[item]['stock']})", True, (255, 255, 255))
            fenetre.blit(texte, (rect.x + 10, rect.y + 10))
            self.catalogue_rects[item] = rect
            
             
                      

