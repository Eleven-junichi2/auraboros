from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
import sys

import pygame

from . import global_


def test_renderln():
    # TEXT_SIZE = self.size(text)
    text = "AaBbCc\nDdEeFf\nGgHhIi"
    line_width_by_px = 48
    TEXT_SIZE = (16*len(text), 16)
    # CHAR_SIZE = TEXT_SIZE // len(text)
    CHAR_SIZE = TEXT_SIZE[0] // len(text)
    len_of_single_line = line_width_by_px // CHAR_SIZE
    texts = [text[i:i+len_of_single_line]
             for i in range(0, len(text), len_of_single_line)]
    text_lists = tuple(map(str.splitlines, texts))
    output_list = []
    for str_list in text_lists:
        for str_ in str_list:
            output_list.append(str_)
    [output_list.append(str_)]

    [text for i in text for text in texts]
    return texts


def pos_on_pixel_scale(pos) -> tuple[int, int]:
    """
    map(lambda num: num//global_.PIXEL_SCALE,
        pygame.mouse.get_pos())
    """
    return tuple(map(lambda num: num//global_.PIXEL_SCALE, pos))


def calc_x_to_center(width_of_stuff_to_be_centered: int) -> int:
    return global_.w_size[0]//2-width_of_stuff_to_be_centered//2


def calc_y_to_center(height_of_stuff_to_be_centered: int) -> int:
    return global_.w_size[1]//2-height_of_stuff_to_be_centered//2


def calc_pos_to_center(
        size_of_stuff_to_be_centered: tuple[int, int]) -> tuple[int, int]:
    return calc_x_to_center(size_of_stuff_to_be_centered[0]),\
        calc_y_to_center(size_of_stuff_to_be_centered[1])


def open_json_file(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


# class Position2d(deque):

#     def __init__(self, iterable=None):
#         super().__init__(iterable, maxlen=2)

#     def append(self):
#         raise NotImplementedError

#     @property
#     def x(self):
#         return self.


# Pos2d = Position2d
# Coordinate2d = Position2d
# Coord2d = Coordinate2d


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

    @ classmethod
    def pyinstaller_path(cls, filepath):
        try:
            # PyInstaller creates a temp folder
            # and stores the programs in _MEIPASS
            path = Path(sys._MEIPASS) / cls.root_dirname / filepath
            # path will be such as: "sys._MEIPASS/assets/imgs/example.png"
        except AttributeError:
            path = cls.root / filepath
        return path

    @ classmethod
    def img(cls, filename):
        return cls.pyinstaller_path(Path(cls.img_dirname) / filename)

    @ classmethod
    def font(cls, filename):
        return cls.pyinstaller_path(Path(cls.font_dirname) / filename)

    @ classmethod
    def sound(cls, filename):
        return cls.pyinstaller_path(Path(cls.sound_dirname) / filename)

    @ classmethod
    def set_asset_root(cls, root_dir_path: str):
        cls.__root = root_dir_path
        cls.root = Path(cls.__root)
        cls.root_dir_parent = Path(root_dir_path).parent
        cls.root_dirname = Path(root_dir_path).name


def draw_grid(
        screen: pygame.surface.Surface, grid_size: int, color: int):
    [pygame.draw.rect(
        screen, color,
        (x*grid_size, y*grid_size) + (grid_size, grid_size), 1)
        for x in range(screen.get_size()[0]//grid_size)
        for y in range(screen.get_size()[1]//grid_size)]
