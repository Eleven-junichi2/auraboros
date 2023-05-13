from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
import sys
from typing import Sequence, Union
import unicodedata

import pygame

from . import global_

RGBAOutput = tuple[int, int, int, int]
ColorValue = Union[
    pygame.color.Color, int, str, tuple[int, int, int], RGBAOutput, Sequence[int]
]


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
    return sum(2 if is_char_fullwidth(char) else 1 for char in str_)


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
