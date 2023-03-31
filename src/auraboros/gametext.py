from dataclasses import dataclass
from typing import Any, Tuple

import pygame

from . import global_

pygame.font.init()


@dataclass
class GameText:
    text: str
    pos: list
    rgb: list
    surface: pygame.surface.Surface = None

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.surface, self.pos)


class TextSurfaceFactory:
    def __init__(self):
        self.current_font_key = None
        self._text_dict: dict[Any, GameText] = {}
        self._font_dict = FontDict()

    @property
    def text_dict(self) -> dict[Any, GameText]:
        return self._text_dict

    @property
    def font_dict(self):
        return self._font_dict

    def register_text(self, key, text: str = "", pos=[0, 0],
                      color_rgb=[255, 255, 255]):
        self.text_dict[key] = GameText(text=text, pos=pos, rgb=color_rgb)

    def rewrite_text(self, key, text: str):
        self.text_dict[key].text = text

    def text_by_key(self, key) -> str:
        return self.text_dict[key].text

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
        """Return Font object that is currently being used"""
        return self.font_dict[self.current_font_key]

    def char_size(self) -> Tuple[int, int]:
        return self.font_dict[self.current_font_key].size(" ")

    def set_text_pos(self, key, pos):
        self.text_dict[key].pos = pos

    def set_text_color(self, key, color_rgb):
        self.text_dict[key].rgb = color_rgb

    def set_text_pos_to_right(self, key):
        self.text_dict[key].pos[0] = \
            global_.w_size[0] - \
            self.font().size(self.text_dict[key].text)[0]

    def set_text_pos_to_bottom(self, key):
        self.text_dict[key].pos[1] = \
            global_.w_size[1] - \
            self.font().size(self.text_dict[key].text)[1]

    def center_text_pos_x(self, key):
        self.text_dict[key].pos[0] = \
            global_.w_size[0]//2 - \
            self.font().size(self.text_dict[key].text)[0]//2

    def center_text_pos_y(self, key):
        self.text_dict[key].pos[1] = \
            global_.w_size[1]//2 - \
            self.font().size(self.text_dict[key].text)[1]//2

    def render(self, text_key, surface_to_draw: pygame.surface.Surface,
               pos=None, wait_rendering_for_text_to_register=True):
        if self.is_text_registered(text_key):
            text_surf = self.font().render(
                self.text_by_key(text_key), True,
                self.text_dict[text_key].rgb)
            if pos is None:
                pos_ = self.text_dict[text_key].pos
            else:
                pos_ = pos
            self.text_dict[text_key].surface = text_surf
            surface_to_draw.blit(text_surf, pos_)

    def generate_gametext(self, text_key):
        return self.text_dict[text_key]


class FontDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value: pygame.font.Font):
        if isinstance(value, pygame.font.Font):
            super().__setitem__(key, value)
        else:
            raise TypeError("The value must be Font object of pygame.")

    def __getitem__(self, key) -> pygame.font.Font:
        return super().__getitem__(key)
