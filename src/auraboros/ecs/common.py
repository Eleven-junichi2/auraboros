from typing import Callable

import pygame

from .world import component


@component
class Position:
    pos: list[int] = [0, 0, 0]

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    @property
    def z(self):
        return self.pos[2]


@component
class Sizing:
    size: list[int] = [0, 0]

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]


@component
class Rect(Position, Sizing):
    def is_given_x_on_rect(self, x) -> bool:
        return self.pos[0] <= x <= self.pos[0] + self.size[0]

    def is_given_y_on_rect(self, y) -> bool:
        return self.pos[1] <= y <= self.pos[1] + self.size[1]

    def is_givenpos_on_rect(self, pos) -> bool:
        return self.is_given_x_on_rect(pos[0]) and self.is_given_y_on_rect(pos[1])

    def do_func_if_pos_is_on_rect(self, pos, func: Callable):
        if self.is_givenpos_on_rect(pos):
            return func()


@component
class Surface:
    surface: pygame.surface.Surface
