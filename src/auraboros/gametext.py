# TODO: implement func that return px size of multiline text to GameText

from dataclasses import dataclass
from typing import Tuple, Union, Sequence, Optional
import itertools

from pygame.color import Color
import pygame

from . import global_
from .utilities import is_char_fullwidth, len_str_contain_fullwidth_char

pygame.font.init()


RGBAOutput = Tuple[int, int, int, int]
ColorValue = Union[Color, int, str, Tuple[int, int, int], RGBAOutput, Sequence[int]]


def split_multiline_text(
    text_to_split: str, singlelinelength_in_charcount: int
) -> tuple[str, ...]:
    """
    Examples:
        >>> print(split_multiline_text("AaBbC\nFfGg\nHhIiJjKkLlMmNnOoPp", 12))
        # -> ('AaBbC', 'FfGg', 'HhIiJjKkLlMm', 'NnOoPp')
        >>> print(split_multiline_text("ABC\n\n\n", 0))
        # -> ('ABC', '', '', '')
    """
    if text_to_split == "":
        texts = ("",)
    else:
        if singlelinelength_in_charcount == 0:
            step = 1
        else:
            step = singlelinelength_in_charcount
        if text_to_split[-1] == "\n" and "\n" in text_to_split[:-1]:
            newline_at_end_in_multilinetext = True
        else:
            newline_at_end_in_multilinetext = False
        text_to_split = text_to_split.splitlines(keepends=True)
        text_lists = [
            [""] if item == [] else item
            for item in [
                [text[i : i + step] for i in range(0, len(text), step)]
                for text in text_to_split
            ]
        ]
        texts = [
            line.replace("\n", "")
            for line in list(
                itertools.chain.from_iterable(text_lists),
            )
        ]
        if newline_at_end_in_multilinetext:
            texts.append("")
        texts = tuple(texts)

    return texts


def line_count_of_multiline_text(text: str, singlelinelength_in_charcount: int):
    return len(split_multiline_text(text, singlelinelength_in_charcount))


class Font2(pygame.font.Font):
    """
    This class inherits from Pygame's Font object and adds some
    helpful features for multiline text.
    """

    def fullwidth_charsize(self) -> Tuple[int, int]:
        return self.size("　")

    def halfwidth_charsize(self) -> Tuple[int, int]:
        return self.size(" ")

    def size_of_multiline_text(
        self,
        text: str,
        linelength_limit_in_px: Optional[int] = None,
        linelength_limit_in_char: Optional[int] = None,
        getsize_in_charcount: bool = False,
    ) -> Tuple[int, int]:
        if text == "":
            return (0, 0)
        longest_line = max(
            text.splitlines(), key=len_str_contain_fullwidth_char
        )  # erase escape sequence
        if linelength_limit_in_px is not None:
            halfwidth_charcount = 0
            fullwidth_charcount = 0
            for char in longest_line:
                if is_char_fullwidth(char):
                    fullwidth_charcount += 1
                else:
                    halfwidth_charcount += 1
            linelength_in_px_of_text = 0
            if halfwidth_charcount > 0:
                linelength_in_px_of_text = (
                    self.halfwidth_charsize()[0] * halfwidth_charcount
                )
            elif fullwidth_charcount > 0:
                linelength_in_px_of_text = (
                    self.fullwidth_charsize()[0] * fullwidth_charcount
                )
            if linelength_in_px_of_text < 0:
                size = (0, 0)
            else:
                checked_charcount = 0
                while linelength_in_px_of_text > linelength_limit_in_px:
                    if is_char_fullwidth(text[-(1 + checked_charcount)]):
                        fullwidth_charcount -= 1
                        linelength_in_px_of_text -= self.fullwidth_charsize()[0]
                    else:
                        halfwidth_charcount -= 1
                        linelength_in_px_of_text -= self.halfwidth_charsize()[0]
                    checked_charcount += 1
                linelength_in_charcount = fullwidth_charcount + halfwidth_charcount
                print(text.replace("\n", "\\n"))
                line_count = len(split_multiline_text(text, linelength_in_charcount))
                print(split_multiline_text(text, linelength_in_charcount))
                # print(split_multiline_text(text, linelength_in_charcount))
                if getsize_in_charcount:
                    size = (linelength_in_charcount, line_count)
                else:
                    size = (
                        linelength_in_px_of_text,
                        line_count * self.get_linesize(),
                    )
        elif linelength_limit_in_char is not None:
            longest_line_charcount = len(longest_line)
            if longest_line_charcount > linelength_limit_in_char:
                longest_line_charcount = linelength_limit_in_char
            line_count = len(split_multiline_text(text, longest_line_charcount))
            if getsize_in_charcount:
                size = (
                    longest_line_charcount,
                    line_count,
                )
            else:
                size = (
                    self.size(longest_line)[0],
                    line_count * self.get_linesize(),
                )
            size = (0, 0)
        else:
            raise ValueError(
                "linelength_limit_in_px or linelength_limit_in_charcount is required."
            )
        return size

    def renderln(
        self,
        text: Union[str, bytes, None],
        antialias: bool,
        color: ColorValue,
        background_color: Optional[ColorValue] = None,
        linelength_in_charcount: Optional[int] = None,
        linelength_in_px: Optional[int] = None,
        *args,
        **kwargs,
    ) -> pygame.surface.Surface:
        """
        linelength_in_px takes precedence over linelength_in_charcount
        if both are set.
        """
        if linelength_in_px is None and linelength_in_charcount is None:
            raise ValueError("linelength_in_px or linelength_in_charcount is required.")
        else:
            if linelength_in_px is not None:
                linelength_in_charcount = self.size_of_multiline_text(
                    text, linelength_in_px, getsize_in_charcount=True
                )[0]
            # make text list
            texts = split_multiline_text(text, linelength_in_charcount)
            # longest_line = max(texts, key=len)
            # ---
            text_surf = pygame.surface.Surface(
                self.size_of_multiline_text(
                    text,
                    linelength_limit_in_px=linelength_in_px,
                    linelength_limit_in_char=linelength_in_charcount,
                )
            )
            [
                text_surf.blit(
                    self.render(
                        text,
                        antialias,
                        color,
                        background_color,
                        *args,
                        **kwargs,
                    ),
                    (0, self.get_linesize() * line_counter),
                )
                for line_counter, text in enumerate(texts)
            ]
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
        self,
        text: Union[str, bytes, None],
        pos: pygame.math.Vector2,
        is_antialias_enable: bool = True,
        color_foreground: ColorValue = pygame.Color(255, 255, 255, 255),
        color_background: Optional[ColorValue] = None,
    ):
        self.text = text
        self.is_antialias_enable = is_antialias_enable
        self.pos = pos
        self.color_foreground = color_foreground
        self.color_background = color_background

    @classmethod
    def setup_font(cls, font: Font2, name_for_registering_in_dict: str):
        """
        The classmethod to set Font object.

        Alias:
            register_font()
        """
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

    def render(
        self, surface_to_blit: Optional[pygame.Surface] = None, *args, **kwargs
    ) -> pygame.surface.Surface:
        """GameText.font.render(with its attributes as args)"""
        text_surface = self.font.render(
            self.text,
            self.is_antialias_enable,
            self.color_foreground,
            self.color_background,
            *args,
            **kwargs,
        )
        if surface_to_blit:
            surface_to_blit.blit(text_surface, self.pos)
        return text_surface

    def renderln(
        self,
        linelength_in_charcount: Optional[int] = None,
        linelength_in_px: Optional[int] = None,
        surface_to_blit: pygame.surface.Surface = None,
        *args,
        **kwargs,
    ) -> pygame.surface.Surface:
        """GameText.font.renderln(with its attributes as args)"""
        text_surface = self.font.renderln(
            self.text,
            self.is_antialias_enable,
            self.color_foreground,
            self.color_background,
            linelength_in_charcount,
            linelength_in_px,
            *args,
            **kwargs,
        )
        if surface_to_blit:
            surface_to_blit.blit(text_surface, self.pos)
        return text_surface

    def set_pos_to_right(self):
        self.pos[0] = global_.w_size[0] - self.font.size(self.text)[0]

    def set_pos_to_bottom(self):
        self.pos[1] = global_.w_size[1] - self.font.size(self.text)[1]

    def set_pos_to_center_x(self):
        self.pos[0] = global_.w_size[0] // 2 - self.font.size(self.text)[0] // 2

    def set_pos_to_center_y(self):
        self.pos[1] = global_.w_size[1] // 2 - self.font.size(self.text)[1] // 2


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
