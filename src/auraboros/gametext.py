from typing import Optional
import itertools

import pygame

from .utils.coordinate import window_size_in_scaled_px
from .utils.string import (
    is_char_fullwidth,
    len_str_contain_fullwidth_char,
    count_fullwidth_char,
    count_halfwidth_char,
)
from .utils.sequence import (
    is_flat,
    search_consecutive_pairs_of_list,
    joint_stritems_in_range_indexpair_list,
)

pygame.font.init()


def split_multiline_text(
    text_to_split: str, linelength: Optional[int] = None
) -> tuple[str, ...]:
    """
    Examples:
        >>> split_multiline_text("AaBbC\nFfGg\nHhIiJjKkLlMmNnOoPp", 12)
        >>> ('AaBbC', 'FfGg', 'HhIiJjKkLlMm', 'NnOoPp')
        >>> split_multiline_text("ABC\n\n\n", 0)
        >>> ('ABC', '', '', '')
        >>> split_multiline_text("abcdef\nghijk\n\n\nああ", 5)
        >>> ('abcde', 'f', 'fghij', '', '', 'ああ')
    """
    # TODO: Refactoring this function to make it more readable
    if text_to_split == "":
        lines = ("",)
    else:
        # --split multiline text to list of lines--
        splited_texts = text_to_split.splitlines(keepends=True)
        splited_texts = [
            line.split("\n") if line != "\n" else line for line in splited_texts
        ]
        for index, flatten_or_not in enumerate(splited_texts):
            if not is_flat(flatten_or_not):
                splited_texts[index] = [
                    "\n" if str_ == "" else str_ for str_ in flatten_or_not
                ]
        splited_texts = tuple(itertools.chain.from_iterable(splited_texts))
        if len(splited_texts) >= 2:
            index_pairs_to_joint = search_consecutive_pairs_of_list(
                splited_texts, "\n", "[^\n]", regular_expression=True
            )[1]
            if index_pairs_to_joint is not None:
                splited_texts = joint_stritems_in_range_indexpair_list(
                    splited_texts, index_pairs_to_joint
                )
        splited_texts = [line.replace("\n", "") for line in splited_texts]
        lines: list[str] = []
        if isinstance(linelength, int):
            # --split to new lines with linelength--
            for line in splited_texts:
                if len(line) > linelength:
                    new_lines = []
                    for char_index in range(0, len(line), linelength):
                        new_lines.append(line[char_index : char_index + linelength])
                    for new_line in new_lines:
                        lines.append(new_line)
                else:
                    lines.append(line)
            # ----
        elif linelength is None:
            lines = splited_texts
        lines = tuple(lines)
        # ----

    return lines


class Font2(pygame.font.Font):
    """
    This class inherits from Pygame's Font object and adds some
    helpful features for multiline text.
    """

    def fullwidth_charsize(self) -> tuple[int, int]:
        return self.size("　")

    def halfwidth_charsize(self) -> tuple[int, int]:
        return self.size(" ")

    def lines_and_sizes_of_multilinetext(
        self,
        text: str,
        linelength_limit: Optional[int] = None,
        is_linelength_limit_in_px: bool = True,
        is_window_size_default_for_length: bool = True,
    ) -> tuple[tuple[str, ...], tuple[int, int], tuple[int, int]]:
        """
        Returns:
            lines_and_sizes_of_multilinetext()[0] is lines,
            lines_and_sizes_of_multilinetext()[1] is size of surface,
            lines_and_sizes_of_multilinetext()[2] is size in char,
        """
        if linelength_limit is None:
            if is_window_size_default_for_length:
                linelength_limit = window_size_in_scaled_px()[0]
                is_linelength_limit_in_px = True
        lines = split_multiline_text(text)  # split to lines without sizing of length
        longest_line = max(lines, key=len_str_contain_fullwidth_char)
        fullwidth_charcount = count_fullwidth_char(longest_line)
        halfwidth_charcount = count_halfwidth_char(longest_line)
        linelength_without_sizing = (
            fullwidth_charcount * self.fullwidth_charsize()[0]
            + halfwidth_charcount * self.halfwidth_charsize()[0]
        )
        if linelength_limit is not None:
            if is_linelength_limit_in_px:
                # 計算したlinelengthが指定のlinelengthを超えていた場合、超えている字を次の行に回す
                move_to_newline_charcount = 0
                while linelength_without_sizing > linelength_limit:
                    if is_char_fullwidth(longest_line[-1]):
                        move_to_newline_charcount += 1
                        linelength_without_sizing -= self.fullwidth_charsize()[0]
                    else:
                        move_to_newline_charcount += 1
                        linelength_without_sizing -= self.halfwidth_charsize()[0]
                if move_to_newline_charcount > 0:
                    linelength_in_char = (
                        fullwidth_charcount
                        + halfwidth_charcount
                        - move_to_newline_charcount
                    )
                else:
                    linelength_in_char = fullwidth_charcount + halfwidth_charcount
            else:
                linelength_in_char = linelength_limit
            lines = split_multiline_text(text, linelength_in_char)
        else:
            linelength_in_char = fullwidth_charcount + halfwidth_charcount
        size_in_px = (linelength_without_sizing, len(lines) * self.get_linesize())
        size_in_char = (linelength_in_char, len(lines))
        return lines, size_in_px, size_in_char

    def renderln(
        self,
        text: str,
        antialias: bool,
        color: pygame.Color,
        background_color: Optional[pygame.Color] = None,
        linelength: Optional[int] = None,
        is_linelength_in_px: bool = True,
        is_window_size_default_for_length: bool = True,
    ) -> pygame.surface.Surface:
        if not isinstance(text, str):
            raise ValueError("argument `text` must be str")
        lines, size_in_px, _ = self.lines_and_sizes_of_multilinetext(
            text,
            linelength_limit=linelength,
            is_linelength_limit_in_px=is_linelength_in_px,
            is_window_size_default_for_length=is_window_size_default_for_length,
        )
        text_surf = pygame.surface.Surface(size=size_in_px)
        for line_num, line in enumerate(lines):
            text_surf.blit(
                self.render(line, antialias, color, background_color),
                (0, self.get_linesize() * line_num),
            )
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
    default_font_name: Optional[str] = None

    def __init__(
        self,
        text: str | bytes | None,
        is_antialias_enable: bool = True,
        color_foreground: pygame.Color = pygame.Color(255, 255, 255, 255),
        color_background: Optional[pygame.Color] = None,
        linelength: Optional[int] = None,
        is_linelength_in_px: bool = True,
        font_name: Optional[str] = None,
    ):
        if font_name:
            if self.font_dict.get(font_name):
                self.font_name = font_name
            else:
                raise ValueError("Font2 object for given `font_name` is not found.")
        else:
            if self.default_font_name:
                self.font_name = self.default_font_name
            else:
                raise ValueError(
                    "default_font_name is None." + "(hint: `setup_font()`)"
                )
        self.text = text
        self.is_antialias_enable = is_antialias_enable
        self.color_foreground = color_foreground
        self.color_background = color_background
        self.linelength = linelength
        self.is_linelength_in_px = is_linelength_in_px

    @classmethod
    def setup_font(cls, font: Font2, name_for_dict_key: str):
        """
        The classmethod to set Font object.
        If `font_dict` is empty, given font will be a default font.

        Alias:
            register_font()
        """
        if len(cls.font_dict) == 0:
            cls.default_font_name = name_for_dict_key
        cls.font_dict[name_for_dict_key] = font

    @classmethod
    def set_font_as_default(cls, font_name: str):
        cls.default_font_name = font_name

    def use_font(self, font_name: str):
        self.font_name = font_name

    # alias of the method
    register_font = setup_font

    @property
    def font(self) -> Font2:
        return self.font_dict[self.font_name]

    def rewrite(self, text: str):
        self.text = text

    def render(
        self,
        surface_to_blit: Optional[pygame.Surface] = None,
        pos_for_surface_to_blit_option: Optional[tuple[int, int]] = None,
    ) -> pygame.surface.Surface:
        """GameText.font.render(with its attributes as args)"""
        text_surface = self.font.render(
            self.text,
            self.is_antialias_enable,
            self.color_foreground,
            self.color_background,
        )
        if surface_to_blit:
            if pos_for_surface_to_blit_option:
                surface_to_blit.blit(text_surface, pos_for_surface_to_blit_option)
            else:
                raise ValueError(
                    "Require `pos_for_surface_to_blit_option`"
                    + " when `surface_to_blit` is True"
                )

        return text_surface

    def renderln(
        self,
        surface_to_blit: Optional[pygame.Surface] = None,
        pos_for_surface_to_blit_option: Optional[tuple[int, int]] = None,
        linelength: Optional[int] = None,
        is_linelength_in_px: bool = True,
        is_window_size_default_for_length: bool = True,
    ) -> pygame.surface.Surface:
        """GameText.font.renderln(with its attributes as args)"""
        text_surface = self.font.renderln(
            text=self.text,
            antialias=self.is_antialias_enable,
            color=self.color_foreground,
            background_color=self.color_background,
            linelength=linelength,
            is_linelength_in_px=is_linelength_in_px,
            is_window_size_default_for_length=is_window_size_default_for_length,
        )
        if surface_to_blit:
            if pos_for_surface_to_blit_option:
                surface_to_blit.blit(text_surface, pos_for_surface_to_blit_option)
            else:
                raise ValueError(
                    "Require `pos_for_surface_to_blit_option`"
                    + " when `surface_to_blit` is True"
                )
        return text_surface
