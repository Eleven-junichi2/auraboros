from collections import UserDict

import pygame

pygame.font.init()


class TextSurfaceFactory:
    def __init__(self):
        self.current_font_key = None
        self._text_dict = {}
        self._font_dict = FontDict()

    @property
    def text_dict(self):
        return self._text_dict

    @property
    def font_dict(self):
        return self._font_dict

    def register_text(self, key, text: str):
        self.text_dict[key] = text

    def text_by_key(self, key) -> str:
        return self.text_dict[key]

    def is_text_registered(self, key):
        if self.text_dict.get(key):
            return True
        else:
            return False

    def register_font(self, key, font: pygame.font.Font):
        if len(self.font_dict) == 0:
            self.current_font_key = key
        self.font_dict[key] = font

    def set_current_font(self, key):
        self.current_font_key = key

    def font_by_key(self, key) -> pygame.font.Font:
        return self.font_dict[key]

    def font(self) -> pygame.font.Font:
        return self.font_dict[self.current_font_key]

    def render(self, text_key, surface_to_draw: pygame.surface.Surface, pos,
               wait_rendering_for_text_to_register=True):
        if self.is_text_registered(text_key):
            text_surf = self.font().render(
                self.text_by_key(text_key), True, (255, 255, 255))
            surface_to_draw.blit(text_surf, pos)


class FontDict(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, item: pygame.font.Font):
        if isinstance(item, pygame.font.Font):
            self.data[key] = item
        else:
            raise TypeError("The value must be Font object of pygame.")
