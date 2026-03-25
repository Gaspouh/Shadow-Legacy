import pygame

def reset(player, liste_ennemis, hearts, spawn_point):
    # Fonction de réinitialisation du jeu après la mort du joueur
    player.health = player.max_health
    player.position = pygame.math.Vector2(spawn_point.x, spawn_point.y)
    player.rect.midbottom = player.position
    player.velocity = pygame.math.Vector2(0, 0)
    player.acceleration = pygame.math.Vector2(0, 0)
    player.invincible = False

    for ennemi in liste_ennemis:
        # Chaque ennemi retourne à sa position de départ et reinitialise sa vitesse
        ennemi.rect.x = ennemi.position_initiale.x
        ennemi.rect.y = ennemi.position_initiale.y 
        ennemi.velocity.y = 0
        ennemi.velocity.x = 0
        ennemi.alive = True # Réactiver les ennemis
        ennemi.pv_ennemi = ennemi.pv_max  # Réinitialiser la santé de l'ennemi
    # Réinitialiser les cœurs
    for heart in hearts:
        heart.state = "ALIVE"
        heart.index_anim = 0