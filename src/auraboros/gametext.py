from dataclasses import dataclass
# from functools import wraps
import itertools
from typing import Any, Tuple, Union, Sequence, Optional

from pygame.color import Color
import pygame

from . import global_

pygame.font.init()


RGBAOutput = Tuple[int, int, int, int]
ColorValue = Union[Color, int, str,
                   Tuple[int, int, int], RGBAOutput, Sequence[int]]


class Font2(pygame.font.Font):
    """
    This class inherits from Pygame's Font object and adds some
    helpful features.
    """

    def renderln(self, text: Union[str, bytes, None], antialias: bool,
                 color: ColorValue,
                 background_color: Optional[ColorValue] = None,
                 line_width_by_px: Optional[int] = None,
                 line_width_by_char_count: Optional[int] = None,
                 *args, **kwargs) -> pygame.surface.Surface:
        """
        line_width_by_px takes precedence over line_width_by_char_count
        if both are set.
        """
        if line_width_by_px is None and line_width_by_char_count is None:
            raise ValueError(
                "line_width_by_px or line_width_by_char_count is required.")
        else:
            TEXT_SIZE = self.size(text)
            CHAR_WIDTH = TEXT_SIZE[0] // len(text)
            if line_width_by_px:
                line_width_by_char_count = line_width_by_px // CHAR_WIDTH
                if len(text) == line_width_by_char_count:
                    return self.render(text, antialias, color,
                                       background_color, *args, **kwargs)
                # make text list
            print(line_width_by_char_count)
            texts = [text[i:i+line_width_by_char_count]
                     for i in range(0, len(text), line_width_by_char_count)]
            print(texts)
            text_lists = tuple(map(str.splitlines, texts))
            texts = tuple(filter(lambda str_: str_ != "",
                                 itertools.chain.from_iterable(text_lists)))
            print(texts)
            # ---
            text_surf = pygame.surface.Surface(
                (CHAR_WIDTH*line_width_by_char_count, TEXT_SIZE[1]*len(texts)))
            [text_surf.blit(
                self.render(text, antialias, color,
                            background_color, *args, **kwargs),
                (0, TEXT_SIZE[1]*line_counter))
                for line_counter, text in enumerate(texts)]
            if not background_color == (0, 0, 0):
                text_surf.set_colorkey((0, 0, 0))
            return text_surf


class GameText:
    font: Font2

    @classmethod
    def setup_font(cls, font: Font2):
        cls.font = font

    def __init__(self, text: str,
                 pos: pygame.math.Vector2,
                 rgb_foreground: ColorValue,
                 rgb_background: Optional[ColorValue] = None):
        self.text = text
        self.pos = pos
        self.rgb_foreground = rgb_foreground
        self.rgb_background = rgb_background

    def rewrite(self, text: str):
        self.text = text

    def render(self, text: Union[str, bytes, None], antialias: bool,
               color: ColorValue,
               background_color: Optional[ColorValue] = None,
               screen: pygame.surface.Surface = None,
               *args, **kwargs) -> pygame.surface.Surface:
        """GameText.font.render(with its attributes as args)"""
        text_surface = self.font.render(
            text, antialias, color, background_color,
            *args, **kwargs)
        if screen:
            screen.blit(text_surface, self.pos)
        return text_surface

    def renderln(self, text: Union[str, bytes, None], antialias: bool,
                 color: ColorValue,
                 background_color: Optional[ColorValue] = None,
                 line_width_by_px: Optional[int] = None,
                 line_width_by_char_count: Optional[int] = None,
                 screen: pygame.surface.Surface = None,
                 *args, **kwargs) -> pygame.surface.Surface:
        """GameText.font.renderln(with its attributes as args)"""
        text_surface = self.font.renderln(
            text, antialias, color, background_color,
            line_width_by_px,
            line_width_by_char_count,
            *args, **kwargs)
        if screen:
            screen.blit(text_surface, self.pos)
        return text_surface

    def set_pos_to_right(self):
        self.pos[0] = \
            global_.w_size[0] - \
            self.font().size(self.text)[0]

    def set_pos_to_bottom(self):
        self.pos[1] = \
            global_.w_size[1] - \
            self.font().size(self.text)[1]

    def set_pos_to_center_x(self):
        self.pos[0] = \
            global_.w_size[0]//2 - \
            self.font().size(self.text)[0]//2

    def set_pos_to_center_y(self):
        self.pos[1] = \
            global_.w_size[1]//2 - \
            self.font().size(self.text)[1]//2


@dataclass
class TextData:
    """This class is going to be deprecated"""
    text: str
    pos: list
    rgb_foreground: list
    rgb_background: list
    surface: pygame.surface.Surface = None

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.surface, self.pos)


class TextSurfaceFactory:
    """This class is going to be deprecated"""

    def __init__(self):
        self.current_font_key = None
        self._text_dict: dict[Any, TextData] = {}
        self._font_dict = FontDict()

    @property
    def text_dict(self) -> dict[Any, TextData]:
        return self._text_dict

    @property
    def font_dict(self):
        return self._font_dict

    def register_text(self, key, text: str = "", pos=[0, 0],
                      color_rgb=[255, 255, 255]):
        self.text_dict[key] = TextData(text=text, pos=pos, rgb=color_rgb)

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
               pos=None):
        if self.is_text_registered(text_key):
            text_surf = self.font().render(
                self.text_by_key(text_key), True,
                self.text_dict[text_key].rgb_foreground,
                self.text_dict[text_key].rgb_background)
            if pos is None:
                pos_ = self.text_dict[text_key].pos
            else:
                pos_ = pos
            self.text_dict[text_key].surface = text_surf
            surface_to_draw.blit(text_surf, pos_)

    def generate_gametext(self, text_key):
        return self.text_dict[text_key]


class FontDict(dict):
    """This class is going to be deprecated"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value: pygame.font.Font):
        if isinstance(value, pygame.font.Font):
            super().__setitem__(key, value)
        else:
            raise TypeError("The value must be Font object of pygame.")

    def __getitem__(self, key) -> pygame.font.Font:
        return super().__getitem__(key)
