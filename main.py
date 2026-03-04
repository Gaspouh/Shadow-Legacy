import pygame
from perso import Player, Platform
from ennemi import ennemi_debutant

pygame.init()
fenetre = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
pygame.display.set_caption("Shadow Legacy")
 
araignee = ennemi_debutant(fenetre)
player = Player(100, 100, fenetre)
platforms = [
    Platform(0, 500, 800, 100),
    Platform(200, 400, 200, 20),
    Platform(500, 300, 200, 20)
]

continuer = True
while continuer:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            continuer = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                player.stop_jump()
    player.update(platforms)
    araignee.gestion_animation()
      # Remplir le fond 
    fenetre.fill((135, 206, 235))  # Couleur de fond (ciel bleu)

    for platform in platforms:
        fenetre.blit(platform.image, platform.rect)

    # Dessiner les personnages
    fenetre.blit(araignee.image, araignee.rect)
    image_rect = player.image.get_rect(midbottom=player.rect.midbottom)
    fenetre.blit(player.image, image_rect)
    
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
