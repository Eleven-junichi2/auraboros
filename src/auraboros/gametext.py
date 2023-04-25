from dataclasses import dataclass
# from functools import wraps
import itertools
from typing import Tuple, Union, Sequence, Optional

from pygame.color import Color
import pygame

from . import global_

pygame.font.init()


RGBAOutput = Tuple[int, int, int, int]
ColorValue = Union[Color, int, str,
                   Tuple[int, int, int], RGBAOutput, Sequence[int]]


def split_multiline_text(
        text_to_split: str,
        singleline_width_by_charcount: int) -> tuple[str, ...]:
    """
    Examples:
        >>> texts = split_multiline_text("AaBbC\nFfGg\nHhIiJjKkLlMmNnOoPp", 12)
        >>> print(texts)
        # -> ('AaBbC', 'FfGg', 'HhIiJjKkLlMm', 'NnOoPp')
    """
    if (singleline_width_by_charcount == 0) or (text_to_split == ""):
        texts = ("",)
    else:
        text_to_split = text_to_split.splitlines()
        text_lists = [[text[i:i+singleline_width_by_charcount]
                       for i in range(
            0, len(text), singleline_width_by_charcount)]
            for text in text_to_split]
        texts = tuple(filter(lambda str_: str_ != "",
                             itertools.chain.from_iterable(text_lists)))
    return texts


def line_count_of_multiline_text(
        text: str, singleline_width_by_charcount: int):
    return len(split_multiline_text(text, singleline_width_by_charcount))


class Font2(pygame.font.Font):
    """
    This class inherits from Pygame's Font object and adds some
    helpful features for multiline text.
    """

    def textwidth_by_px_into_charcount(self, text_width_by_px) -> int:
        return text_width_by_px // self.size(" ")[0]

    def textwidth_by_charcount_into_px(self, textwidth_by_charcount) -> int:
        return textwidth_by_charcount * self.size(" ")[0]

    def renderln(self, text: Union[str, bytes, None], antialias: bool,
                 color: ColorValue,
                 background_color: Optional[ColorValue] = None,
                 line_width_by_char_count: Optional[int] = None,
                 line_width_by_px: Optional[int] = None,
                 *args, **kwargs) -> pygame.surface.Surface:
        """
        line_width_by_px takes precedence over line_width_by_char_count
        if both are set.
        """
        if line_width_by_px is None and line_width_by_char_count is None:
            raise ValueError(
                "line_width_by_px or line_width_by_char_count is required.")
        else:
            if line_width_by_px:
                line_width_by_char_count = self.textwidth_by_px_into_charcount(
                    line_width_by_px)
                if len(text) == line_width_by_char_count:
                    return self.render(text, antialias, color,
                                       background_color, *args, **kwargs)
            # make text list
            texts = split_multiline_text(text, line_width_by_char_count)
            # ---
            LINE_HEIGHT = self.get_linesize()
            text_surf = pygame.surface.Surface(
                (self.size(" ")[0]*line_width_by_char_count,
                 LINE_HEIGHT*len(texts)))
            [text_surf.blit(
                self.render(text, antialias, color,
                            background_color, *args, **kwargs),
                (0, LINE_HEIGHT*line_counter))
                for line_counter, text in enumerate(texts)]
            if not background_color == (0, 0, 0):
                text_surf.set_colorkey((0, 0, 0))
            return text_surf


class Font2Dict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value: Font2):
        if isinstance(value, Font2):
            super().__setitem__(key, value)
        else:
            raise TypeError("The value must be Font2 object.")

    def __getitem__(self, key) -> Font2:
        return super().__getitem__(key)


class GameText:
    font_dict: Font2Dict = Font2Dict()
    current_font_name: str

    def __init__(
        self, text: Union[str, bytes, None],
            pos: pygame.math.Vector2,
            is_antialias_enable: bool = True,
            color_foreground: ColorValue = pygame.Color(255, 255, 255, 255),
            color_background: Optional[ColorValue] = None):
        self.text = text
        self.is_antialias_enable = is_antialias_enable
        self.pos = pos
        self.color_foreground = color_foreground
        self.color_background = color_background

    @classmethod
    def setup_font(cls, font: Font2, name_for_registering_in_dict: str):
        """The classmethod to set Font object."""
        cls.font_dict[name_for_registering_in_dict] = font
        cls.current_font_name = name_for_registering_in_dict

    @classmethod
    def use_font(cls, name_of_font_in_dict: str):
        cls.current_font_name = name_of_font_in_dict

    # alias of the method
    register_font = setup_font

    @classmethod
    def get_font(cls) -> Font2:
        return cls.font_dict[cls.current_font_name]

    @classmethod
    @property
    def font(cls) -> Font2:
        return cls.font_dict[cls.current_font_name]

    def char_size(self) -> Tuple[int, int]:
        return self.font_dict[self.current_font_name].size(" ")

    def rewrite(self, text: str):
        self.text = text

    def render(self, surface_to_blit: Optional[pygame.Surface] = None,
               *args, **kwargs) -> pygame.surface.Surface:
        """GameText.font.render(with its attributes as args)"""
        text_surface = self.font.render(
            self.text, self.is_antialias_enable,
            self.color_foreground, self.color_background,
            *args, **kwargs)
        if surface_to_blit:
            surface_to_blit.blit(text_surface, self.pos)
        return text_surface

    def renderln(self,
                 line_width_by_char_count: Optional[int] = None,
                 line_width_by_px: Optional[int] = None,
                 surface_to_blit: pygame.surface.Surface = None,
                 *args, **kwargs) -> pygame.surface.Surface:
        """GameText.font.renderln(with its attributes as args)"""
        text_surface = self.font.renderln(
            self.text, self.is_antialias_enable,
            self.color_foreground, self.color_background,
            line_width_by_char_count,
            line_width_by_px,
            *args, **kwargs)
        if surface_to_blit:
            surface_to_blit.blit(text_surface, self.pos)
        return text_surface

    def set_pos_to_right(self):
        self.pos[0] = \
            global_.w_size[0] - \
            self.font.size(self.text)[0]

    def set_pos_to_bottom(self):
        self.pos[1] = \
            global_.w_size[1] - \
            self.font.size(self.text)[1]

    def set_pos_to_center_x(self):
        self.pos[0] = \
            global_.w_size[0]//2 - \
            self.font.size(self.text)[0]//2

    def set_pos_to_center_y(self):
        self.pos[1] = \
            global_.w_size[1]//2 - \
            self.font.size(self.text)[1]//2

    def height_multiline(
            self, line_width_by_char_count: Optional[int] = None,
            line_width_by_px: Optional[int] = None,):
        pass


@dataclass
class TextData:
    """This class is going to be deprecated"""
    text: str
    pos: list
    color_foreground: list
    rgb_background: list
    surface: pygame.surface.Surface = None

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.surface, self.pos)


# class TextSurfaceFactory:
#     """This class is going to be deprecated"""

#     def __init__(self):
#         self.current_font_key = None
#         self._text_dict: dict[Any, TextData] = {}
#         self._font_dict = FontDict()

#     @property
#     def text_dict(self) -> dict[Any, TextData]:
#         return self._text_dict

#     @property
#     def font_dict(self):
#         return self._font_dict

#     def register_text(self, key, text: str = "", pos=[0, 0],
#                       color_rgb=[255, 255, 255]):
#         self.text_dict[key] = TextData(text=text, pos=pos, rgb=color_rgb)

#     def rewrite_text(self, key, text: str):
#         self.text_dict[key].text = text

#     def text_by_key(self, key) -> str:
#         return self.text_dict[key].text

#     def is_text_registered(self, key):
#         if self.text_dict.get(key):
#             return True
#         else:
#             return False

#     def register_font(self, key, font: pygame.font.Font):
#         if len(self.font_dict) == 0:
#             self.current_font_key = key
#         self.font_dict[key] = font

#     def set_current_font(self, key):
#         self.current_font_key = key

#     def font_by_key(self, key) -> pygame.font.Font:
#         return self.font_dict[key]

#     def font(self) -> pygame.font.Font:
#         """Return Font object that is currently being used"""
#         return self.font_dict[self.current_font_key]

#     def char_size(self) -> Tuple[int, int]:
#         return self.font_dict[self.current_font_key].size(" ")

#     def set_text_pos(self, key, pos):
#         self.text_dict[key].pos = pos

#     def set_text_color(self, key, color_rgb):
#         self.text_dict[key].color_foreground = color_rgb

#     def set_text_pos_to_right(self, key):
#         self.text_dict[key].pos[0] = \
#             global_.w_size[0] - \
#             self.font().size(self.text_dict[key].text)[0]

#     def set_text_pos_to_bottom(self, key):
#         self.text_dict[key].pos[1] = \
#             global_.w_size[1] - \
#             self.font().size(self.text_dict[key].text)[1]

#     def center_text_pos_x(self, key):
#         self.text_dict[key].pos[0] = \
#             global_.w_size[0]//2 - \
#             self.font().size(self.text_dict[key].text)[0]//2

#     def center_text_pos_y(self, key):
#         self.text_dict[key].pos[1] = \
#             global_.w_size[1]//2 - \
#             self.font().size(self.text_dict[key].text)[1]//2

#     def render(self, text_key, surface_to_draw: pygame.surface.Surface,
#                pos=None):
#         if self.is_text_registered(text_key):
#             text_surf = self.font().render(
#                 self.text_by_key(text_key), True,
#                 self.text_dict[text_key].color_foreground,
#                 self.text_dict[text_key].rgb_background)
#             if pos is None:
#                 pos_ = self.text_dict[text_key].pos
#             else:
#                 pos_ = pos
#             self.text_dict[text_key].surface = text_surf
#             surface_to_draw.blit(text_surf, pos_)

#     def generate_gametext(self, text_key):
#         return self.text_dict[text_key]
