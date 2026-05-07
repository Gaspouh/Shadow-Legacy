from Visual.sprite_sheet import VerticalAnimation
import pygame

class NPC_Logic():
    IDLE = "idle"
    def __init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, colonne, arrival_dialogue, leave_dialogue):
        super().__init__(fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, colonne)
        self.state = "idle"

        # variable necessaires pour fonctionner meme si inutiles
        self.alive = True
        self.attack_data = {"damage": 0}

        self.dialogue_triggered = False   # déclenchement dialogue
        self.dialogue_zone = pygame.Rect(self.rect.x - 50, self.rect.y - 50, self.rect.width + 100, self.rect.height + 100) # zone de déclenchement du dialogue
        self.arrival_dialogue = arrival_dialogue
        self.leave_dialogue = leave_dialogue
        self.dialogue_index = 0
        self.current_dialogue_list = []
        self.is_speaking = False
    
    def player_in_dialogue(self, player_rect):
        if self.dialogue_zone.colliderect(player_rect):
            if not self.dialogue_triggered:
                self.start_dialogue(self.arrival_dialogue)
                return True

    def start_dialogue(self, dialogue_list):
        """ Initialisation du dialogue """
        self.current_dialogue_list = dialogue_list
        self.dialogue_index = 0
        self.is_speaking = True
        self.dialogue_triggered = True

    def build_dialogue_bubble(self, screen, text, pos):
        
        """
        FAIT PAR AI : GEMINI FAST 3.0 (bruh), @everyone 🤓👆, c'est juste parce que y'a le match j'ai pas le temps

        """
        font = pygame.font.SysFont("Arial", 16, bold=True)
        # Gestion du padding et de la taille
        padding = 10
        text_surface = font.render(text, True, (0, 0, 0)) # Texte noir
        text_rect = text_surface.get_rect()
        
        # Dimensions de la bulle
        bubble_rect = pygame.Rect(0, 0, text_rect.width + padding * 2, text_rect.height + padding * 2)
        bubble_rect.midbottom = (pos[0], pos[1] - 20) # Placé au dessus du PNJ

        # Dessiner le triangle (la pointe)
        point_list = [
            (bubble_rect.centerx - 10, bubble_rect.bottom),
            (bubble_rect.centerx + 10, bubble_rect.bottom),
            (bubble_rect.centerx, bubble_rect.bottom + 10)
        ]
        
        # Dessin de l'ombre (optionnel pour le style)
        shadow_rect = bubble_rect.copy()
        shadow_rect.move_ip(3, 3)
        pygame.draw.rect(screen, (50, 50, 50), shadow_rect, border_radius=10)

        # Dessin du corps de la bulle
        pygame.draw.polygon(screen, (255, 255, 255), point_list)
        pygame.draw.rect(screen, (255, 255, 255), bubble_rect, border_radius=10)
        
        # Bordure de la bulle
        pygame.draw.rect(screen, (0, 0, 0), bubble_rect, width=2, border_radius=10)

        # Affichage du texte
        text_rect.center = bubble_rect.center
        screen.blit(text_surface, text_rect)

    def update(self, player_rect, player=None, e_proches=None, event=None):
        if self.dialogue_zone.colliderect(player_rect):
            if not self.dialogue_triggered:
                self.start_dialogue(self.arrival_dialogue)
        else:
            self.dialogue_triggered = False
            self.is_speaking = False

        if self.is_speaking:
            if event and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 3):
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.current_dialogue_list):
                        self.is_speaking = False

            if event and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.is_speaking = False
                self.dialogue_triggered = False
    
    def draw(self, screen, camera=None):
        # Avancer l'animation idle
        self.gestion_animation()
        
        # Blitter le sprite
        if camera:
            screen.blit(self.image, camera.apply(self.rect))
        else:
            screen.blit(self.image, self.rect)

        # Bulle de dialogue
        if self.is_speaking and self.dialogue_index < len(self.current_dialogue_list):
            if camera:
                pos = camera.apply(self.rect)
                screen_pos = (pos.centerx, pos.top)
            else:
                screen_pos = (self.rect.centerx, self.rect.top)
            self.build_dialogue_bubble(screen, self.current_dialogue_list[self.dialogue_index], screen_pos)

        if camera:
            pygame.draw.rect(screen, (255, 0, 0), camera.apply(self.rect), 2)
        else:
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

class Gordon_NPC(NPC_Logic, VerticalAnimation):
    def __init__(self, fenetre, x, y):
        sprite_sheet = f'Assets/Npc/Gordon/idle.png'
        nb_frames = 4
        width = 32
        height = 32
        marge = 0
        colonne = 0
        self.arrival_dialogue = [
            " salut toi, tu veux quoi ? ",
            " Bon j'ai compris, tu parles pas beaucoup hein ? ",
            " je vend des trucs si tu veux, jette un oeil au magasin !"
        ]

        self.leave_dialogue = [
            " ... ",
            " Bon, à plus alors ! "
        ]

        super().__init__(fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, colonne, self.arrival_dialogue, self.leave_dialogue)

        

