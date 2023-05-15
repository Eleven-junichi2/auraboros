import pygame

from ..core import Global


def window_size():
    """pygame.display.get_window_size()"""
    return pygame.display.get_window_size()


def in_base_px_scale(pos) -> tuple[int, int]:
    """
    map(lambda num: num//Global.base_px_scale,
        pygame.mouse.get_pos())
    """
    return tuple(map(lambda num: num // Global.base_px_scale, pos))


def calc_x_to_center(width_of_stuff_to_be_centered: int) -> int:
    return Global.base_px_scale[0] // 2 - width_of_stuff_to_be_centered // 2


def calc_y_to_center(height_of_stuff_to_be_centered: int) -> int:
    return Global.base_px_scale[1] // 2 - height_of_stuff_to_be_centered // 2


def calc_pos_to_center(
    size_of_stuff_to_be_centered: tuple[int, int]
) -> tuple[int, int]:
    return calc_x_to_center(size_of_stuff_to_be_centered[0]), calc_y_to_center(
        size_of_stuff_to_be_centered[1]
    )
