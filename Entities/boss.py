import pygame
from Visual.sprite_sheet import VerticalAnimation
from World.map import platforms

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
        
        v = 120
        # Vitesses d'animation (divisé par 60 pour chaque frame)
        self.anim_idle.vitesse_animation        = 40 / v
        self.anim_walk_right.vitesse_animation  = 32 / v /1.5 # plus lent
        self.anim_walk_left.vitesse_animation   = 32 / v /1.5
        self.anim_smash_right.vitesse_animation = 12 / v
        self.anim_smash_left.vitesse_animation  = 12 / v

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

    def update(self, player_rect):
        if not self.alive:
            return

        # Recul et friction
        self.rect.x += self.velocity_x
        self.velocity_x *= self.friction
        if abs(self.velocity_x) < 0.2:
            self.velocity_x = 0

        # Gravité (gestion de chute)
        self.velocity_y += self.gravity
        if self.velocity_y > 20:
            self.velocity_y = 20
        self.rect.y += self.velocity_y

        self.hitbox.midbottom = self.rect.midbottom

        # Collisions du boss sur plateformes
        for platform in platforms:
                    if self.hitbox.colliderect(platform.rect):
                        if self.velocity_y > 0: # En chute (sol)
                            self.hitbox.bottom = platform.rect.top
                            self.velocity_y = 0
                        elif self.velocity_y < 0: # En haut (plafond)
                            self.hitbox.top = platform.rect.bottom
                            self.velocity_y = 0

        self.rect.midbottom = self.hitbox.midbottom
        self.rect.y += 53 # hitbox ajustée manuellement

        # Logique ia du golem
        if self._joueur_dans_trigger(player_rect):
            if player_rect.centerx > self.rect.centerx:
                self.direction = 1
                self.rect.x += self.vitesse_deplacement
                self.image = self.anim_walk_right.frames_droite[int(self.anim_walk_right.gestion_animation())]
            else:
                self.direction = -1
                self.rect.x -= self.vitesse_deplacement
                self.image = self.anim_walk_left.frames_droite[int(self.anim_walk_left.gestion_animation())]
        else:
            self.image = self.anim_idle.frames_droite[int(self.anim_idle.gestion_animation())]

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
        """