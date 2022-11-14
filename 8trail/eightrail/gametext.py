import pygame


class TextSurfaceFactory:
    def __init__(self, font: pygame.font.Font = None):
        self.font = font
        self.dict = {}

    def render(self, text: str):
        pass

    def blit_to(surface_to_draw: pygame.surface.Surface):
        pass
