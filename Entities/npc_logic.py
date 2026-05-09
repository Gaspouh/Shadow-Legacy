from Visual.sprite_sheet import VerticalAnimation , Animation
import pygame
from Visual.interface import charms_market
from World.objets import Monnaie

class NPC_Logic():
    IDLE = "idle"
    def __init__(self, fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, colonne, scale=1, arrival_dialogue=None, leave_dialogue=None, market_seller=None):
        super().__init__(fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, colonne, scale)
        self.state = "idle"
        self.dialogue_triggered = False   # déclenchement dialogue
        self.dialogue_zone = pygame.Rect(self.rect.x - 50, self.rect.y - 50, self.rect.width + 100, self.rect.height + 100) # zone de déclenchement du dialogue
        self.arrival_dialogue = arrival_dialogue
        self.leave_dialogue = leave_dialogue
        self.market_seller = market_seller
        self.dialogue_index = 0
        self.current_dialogue_list = []
        self.is_speaking = False
        self.fenetre = fenetre
    
    def player_in_dialogue(self, player_rect):
        if self.dialogue_zone.colliderect(player_rect):
            if not self.dialogue_triggered:
                self.start_dialogue(self.arrival_dialogue)
                return True

    def start_dialogue(self, dialogue_list, dialogue_type = "normal"):
        """ Initialisation du dialogue """
        self.current_dialogue_list = dialogue_list
        self.dialogue_index = 0
        self.is_speaking = True
        self.dialogue_triggered = True
        self.dialogue_type = dialogue_type

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

    def update(self, player_rect, player=None, event=None, e_proches=None):
        if self.dialogue_zone.colliderect(player_rect):
            if not self.dialogue_triggered:
                self.start_dialogue(self.arrival_dialogue)
        else:
            self.dialogue_triggered = False
            self.is_speaking = False
        
        if self.is_speaking:
            raw_mouse = pygame.mouse.get_pos() # Récupère la position brute de la souris à l'écran
    
            # Appliquer l'inverse du zoom pour obtenir la position correcte de la souris dans le monde du jeu
            zoom = 1.5
            mouse_pos = (raw_mouse[0] / zoom, raw_mouse[1] / zoom)


            if self.dialogue_type == "upgrade":# Si on est dans le dialogue d'upgrade, on attend que le joueur clique sur une des options

                if hasattr(self, 'rect_oui') and self.rect_oui.collidepoint(mouse_pos): # si la souris pass sur oui
                    self.confirm_upgrade(player) # on lance l'amélioration
                    return
                elif hasattr(self, 'rect_non') and self.rect_non.collidepoint(mouse_pos): # si la souris passe sur non
                    print("joueur a choisi NON pour l'upgrade")
                    self.start_dialogue(self.leave_dialogue) # on lance le dialogue de sortie
                    return

        if self.is_speaking and event and event.type == pygame.MOUSEBUTTONUP:
            if event.button in (1, 3):
                    
                # passage au dialogue suivant
                self.dialogue_index += 1
                if self.dialogue_index >= len(self.current_dialogue_list):

                    if hasattr(self, "dialogue_equipement") and self.current_dialogue_list == self.arrival_dialogue:
                        self.dialogue_equipement()
                        return
                    self.is_speaking = False
                    if self.market_seller:
                        self.market_seller(self.fenetre, self.sell_charms)   # market seller est une fonction a modifier dans chaque npc seller
                        # dialogue sortie
                        self.start_dialogue(self.leave_dialogue)

        if event and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.is_speaking:
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

            if self.dialogue_type == "upgrade":
                self.rect_oui = pygame.draw.rect(screen, (0, 200, 0), (screen_pos[0]-60, screen_pos[1]-20, 50, 30))
                self.rect_non = pygame.draw.rect(screen, (200, 0, 0), (screen_pos[0]+10, screen_pos[1]-20, 50, 30))
                font = pygame.font.SysFont("Arial", 12, bold=True)
                screen.blit(font.render("OUI", True, (255,255,255)), (screen_pos[0]-50, screen_pos[1]-12))
                screen.blit(font.render("NON", True, (255,255,255)), (screen_pos[0]+20, screen_pos[1]-12))


class Gordon_NPC(NPC_Logic, VerticalAnimation):
    def __init__(self, fenetre, x, y):
        sprite_sheet = f'Assets/Npc/Gordon/idle.png'
        y -= 50  # faire monter le npc sur Y
        nb_frames = 51
        width = 256
        height = 256
        marge = 0
        colonne = 0
        self.arrival_dialogue = [
            " salut toi, tu veux quoi ? ",
            " Un conseil, appuie sur E quand tu es assis sur un banc,",
            " tu pourras voir les Charms que tu possèdes et en équiper jusqu'a 3.",
            " Je vend des trucs si tu veux, jette un oeil au magasin !"
        ]

        self.leave_dialogue = [
            " Les charms permettent d'améliorer tes capacités ... ",
            " Bon, à plus alors. "
        ]

        super().__init__(fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, colonne, scale=1, arrival_dialogue=self.arrival_dialogue, leave_dialogue=self.leave_dialogue)
        self.sell_charms = {
            "attack_long_range": {"price": 125, "image": "Assets/charms/attack_long_range.png"},
            "attack_speed": {"price": 100, "image": "Assets/charms/attack_speed.png"},
            "jump_boost": {"price": 150, "image": "Assets/charms/jump_boost.png"},
        }
        self.market_seller = charms_market  # appel de la fonction des charms

class Forgeron(NPC_Logic, Animation):
    def __init__(self, fenetre, x, y):
        sprite_sheet = 'Assets/Npc/forgeron.png'
        nb_frames = 9
        width = 75
        height = 58
        marge = 0
        ligne= 0
        self.upgrade_done = 0
        self.upgrade_cost = 1
        self.orb_cost = 100

        self.arrival_dialogue = [
            "Bonjour étrange voyageur, que puis-je faire pour toi ?",
            "Je peux améliorer ton équipement si tu me donnes les matériaux nécessaires."]
        
        self.leave_dialogue = [
            "À bientôt, prends garde aux ténèbres qui rôdent dans ce monde."
        ]

        super().__init__(fenetre, x, y, sprite_sheet, nb_frames, width, height, marge, ligne, scale=1, arrival_dialogue=self.arrival_dialogue, leave_dialogue=self.leave_dialogue)
    
    def dialogue_equipement(self): 
        # lance le dialogue d'amélioration

        self.upgrade_dialogue = [
            "Je peux améliorer ton arme si tu me donnes " + str(self.upgrade_cost) + " minerais et " + str(self.orb_cost) + " pièces. Veux-tu procéder à l'amélioration ?"
        ]

        self.start_dialogue(self.upgrade_dialogue, dialogue_type="upgrade")

    def confirm_upgrade(self, player):
        if player.minerais >= self.upgrade_cost and Monnaie.orbs >= self.orb_cost: # Vérifie si le joueur a les ressources nécessaires pour l'amélioration
            self.upgrade(player) # Effectue l'amélioration de l'équipement du joueur
            
        else:
            self.start_dialogue(["Désolé, tu n'as pas les ressources nécessaires pour l'amélioration."], dialogue_type="normal") # Dialogue si le joueur n'a pas les ressources nécessaires

    def upgrade(self, player):
        # Retire les ressources du joueur
        player.minerais -= self.upgrade_cost
        Monnaie.orbs -= self.orb_cost

        player.attack += 1 # Améliore l'attaque du joueur
        self.upgrade_done += 1 # Incrémente le nombre d'améliorations effectuées
        self.upgrade_cost += 1 # Augmente le coût de la prochaine amélioration
        self.orb_cost += 50 # Augmente le coût en pièce de la prochaine amélioration
        self.start_dialogue(["Ton arme a été améliorée , tu es maintenant plus fort contre les ennemis !"], dialogue_type="normal") # Dialogue de confirmation de l'amélioration