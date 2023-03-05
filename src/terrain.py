import pygame

# from .animation import SpriteSheet


class TerrainTile:
    def __init__(self):
        self.image = pygame.surface.Surface((0, 0))
        self.rect = self.image.get_rect()


class Terrain:
    tilemap = []
