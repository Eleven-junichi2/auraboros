from dataclasses import dataclass, field, asdict
from typing import Any, Sequence, Union
from pathlib import Path
import json
import sys
import unicodedata
import re

import pygame

from . import global_

RGBAOutput = tuple[int, int, int, int]
ColorValue = Union[
    pygame.color.Color, int, str, tuple[int, int, int], RGBAOutput, Sequence[int]
]


def is_flat(list_: Union[list, tuple, Sequence], consider_str_as_sequence=True):
    for item in list_:
        if isinstance(item, Sequence):
            if not consider_str_as_sequence and isinstance(item, str):
                continue
            return False
    return True


def is_typed_sequence(type_: type, sequence: Sequence):
    return all(
        [
            all([isinstance(item, type_) for item in sequence])
            if isinstance(sequence, Sequence)
            else False
        ]
    )


def joint_stritems_in_range_a_to_b(
    str_sequence: Sequence[str],
    index_a: int,
    index_b: int,
) -> list[str]:
    jointed_list = []
    MAX_INDEX = len(str_sequence) - 1
    if (index_a or index_b) > MAX_INDEX or (index_a or index_b) < 0:
        raise ValueError(
            f"Index out of range: index_a and index_b must be between 0 and {MAX_INDEX}"
        )
    for index, str_ in enumerate(str_sequence):
        if index < index_a:
            jointed_list.append(str_)
        elif index < index_b:
            str_to_append = ""
            for index_ in range(index_a, index_b + 1):
                str_to_append += str_sequence[index_]
            jointed_list.append(str_to_append)
    return jointed_list


def joint_two_stritems_by_indexpair_list(
    str_sequence: Sequence[str],
    indexpair_list: Sequence[tuple[int, int]],
) -> list[str]:
    result = []
    MAX_INDEX = len(str_sequence) - 1
    step_to_joint = 0
    for index_a, index_b in indexpair_list:
        if (index_a or index_b) > MAX_INDEX or (index_a or index_b) < 0:
            raise ValueError("Index out of range")
        parts_not_to_be_joint = str_sequence[step_to_joint:index_a]
        result += [*parts_not_to_be_joint]
        step_to_joint = index_b + 1
        jointed_parts = str_sequence[index_a] + str_sequence[index_b]
        result += [jointed_parts]
    else:
        result += str_sequence[step_to_joint:]
    return result


def search_consecutive_pairs_of_list(
    sequence: Sequence,
    item_a,
    item_b,
    regular_expression: bool = False,
) -> tuple[list[tuple[Any, Any]], list[tuple[int, int]]]:
    """
    item_a and item_b are considered regular expression patterns
    if regular_expression is True.
    Returns:
        tuple[list[tuple[Any, Any]], list[tuple[int, int]]]:
            list[tuple[Any, Any]]:
                this is list of found consecutive item pairs,
            list[tuple[int, int]]:
                this is list of consecutive index pairs.
    """
    if len(sequence) < 2:
        ValueError("count_consecutive_items must have at least 2 items")
    if regular_expression:
        if not (isinstance(item_a, str) or isinstance(item_b, str)):
            ValueError(" item_a and item_b must be str if regular_expression is True")
        if not all([isinstance(item, str) for item in sequence]):
            ValueError(
                "type of items of 'sequence' must be str if regular_expression is True"
            )
    indexpair_list = []
    itempair_list = []
    for index, item in enumerate(sequence):
        if index > 0:
            if regular_expression:
                if re.match(item_a, sequence[index - 1]) and re.match(item_b, item):
                    indexpair_list.append((index - 1, index))
                    itempair_list.append((sequence[index - 1], item))
            else:
                if sequence[index - 1] == item_a and item == item_b:
                    indexpair_list.append((index - 1, index))
                    itempair_list.append((sequence[index - 1], item))
    if itempair_list == []:
        itempair_list = None
    if indexpair_list == []:
        indexpair_list = None
    return itempair_list, indexpair_list


def pos_on_px_scale(pos) -> tuple[int, int]:
    """
    map(lambda num: num//global_.PIXEL_SCALE,
        pygame.mouse.get_pos())
    """
    return tuple(map(lambda num: num // global_.PIXEL_SCALE, pos))


def calc_x_to_center(width_of_stuff_to_be_centered: int) -> int:
    return global_.w_size[0] // 2 - width_of_stuff_to_be_centered // 2


def calc_y_to_center(height_of_stuff_to_be_centered: int) -> int:
    return global_.w_size[1] // 2 - height_of_stuff_to_be_centered // 2


def calc_pos_to_center(
    size_of_stuff_to_be_centered: tuple[int, int]
) -> tuple[int, int]:
    return calc_x_to_center(size_of_stuff_to_be_centered[0]), calc_y_to_center(
        size_of_stuff_to_be_centered[1]
    )


def open_json_file(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


def is_char_fullwidth(char: str):
    if unicodedata.east_asian_width(char) in ("F", "W", "A"):
        return True
    else:
        return False


def len_str_contain_fullwidth_char(str_: str) -> int:
    """
    This function considers the length of full-width characters to be twice the length
    of half-width characters.
    """
    return sum(2 if is_char_fullwidth(char) else 1 for char in str_)


def count_fullwidth_char(str_: str):
    return len(tuple(filter(is_char_fullwidth, str_)))


def count_halfwidth_char(str_: str):
    return len(tuple(filter(lambda char: not is_char_fullwidth(char), str_)))


@dataclass
class Arrow:
    """Arrow symbol"""

    LEFT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3


@dataclass
class ArrowToTurnToward:
    """Use to set direction"""

    is_up: bool = field(default=False)
    is_down: bool = field(default=False)
    is_right: bool = field(default=False)
    is_left: bool = field(default=False)

    def set(self, direction: Arrow):
        if direction is Arrow.UP:
            self.is_up = True
        elif direction is Arrow.DOWN:
            self.is_down = True
        elif direction is Arrow.RIGHT:
            self.is_right = True
        elif direction is Arrow.LEFT:
            self.is_left = True

    def unset(self, direction: Arrow):
        if direction is Arrow.UP:
            self.is_up = False
        elif direction is Arrow.DOWN:
            self.is_down = False
        elif direction is Arrow.RIGHT:
            self.is_right = False
        elif direction is Arrow.LEFT:
            self.is_left = False

    def is_set_any(self):
        return True in set(asdict(self).values())


def path_pyinstllr(path):
    """
    Convert the given path with the sys._MEIPASS directory as its
    parent if the app is running with PyInstaller.

    Bootloader of PyInstalle creates a temp folder "sys._MEIPASS"
    and stores programs and files in it.
    """
    try:
        # PyInstaller creates a temp folder
        # and stores the programs in _MEIPASS
        path = Path(sys._MEIPASS) / path
        # path will be such as: "sys._MEIPASS/assets/imgs/example.png"
    except AttributeError:
        path = path
    return path


class AssetFilePath:
    root_dirname = "assets"
    root_dir_parent = Path(sys.argv[0]).parent
    __root = root_dir_parent / root_dirname
    root = Path(__root)
    img_dirname = "imgs"
    font_dirname = "fonts"
    sound_dirname = "sounds"

    @classmethod
    def pyinstaller_path(cls, filepath):
        try:
            # PyInstaller creates a temp folder
            # and stores the programs in _MEIPASS
            path = Path(sys._MEIPASS) / cls.root_dirname / filepath
            # path will be such as: "sys._MEIPASS/assets/imgs/example.png"
        except AttributeError:
            path = cls.root / filepath
        return path

    @classmethod
    def img(cls, filename):
        return cls.pyinstaller_path(Path(cls.img_dirname) / filename)

    @classmethod
    def font(cls, filename):
        return cls.pyinstaller_path(Path(cls.font_dirname) / filename)

    @classmethod
    def sound(cls, filename):
        return cls.pyinstaller_path(Path(cls.sound_dirname) / filename)

    @classmethod
    def set_asset_root(cls, root_dir_path: str):
        cls.__root = root_dir_path
        cls.root = Path(cls.__root)
        cls.root_dir_parent = Path(root_dir_path).parent
        cls.root_dirname = Path(root_dir_path).name


def draw_grid(screen: pygame.surface.Surface, grid_size: int, color: ColorValue):
    [
        pygame.draw.rect(
            screen, color, (x * grid_size, y * grid_size) + (grid_size, grid_size), 1
        )
        for x in range(screen.get_size()[0] // grid_size)
        for y in range(screen.get_size()[1] // grid_size)
    ]


def render_rightpointing_triangle(height, color: ColorValue) -> pygame.surface.Surface:
    polygon_points_to_draw = (
        (0, 0),
        (
            height // 2,
            height // 2,
        ),
        (
            0,
            height,
        ),
    )
    surface = pygame.surface.Surface((height // 2, height))
    pygame.draw.polygon(
        surface,
        color,
        polygon_points_to_draw,
    )
    return surface
