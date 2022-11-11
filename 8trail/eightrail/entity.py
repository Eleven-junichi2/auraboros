from collections import deque
from math import sqrt

import pygame

from .gamescene import Scene
from .utilities import ArrowToTurnToward
from .__init__ import TARGET_FPS, w_size


class Sprite(pygame.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene: Scene
        self.direction_of_movement = ArrowToTurnToward()
        self.movement_speed = 1
        self._x = 0
        self._y = 0

    @ property
    def x(self):
        return self._x

    @ x.setter
    def x(self, value):
        self._x = round(value, 2)
        self.rect.x = self._x

    @ property
    def y(self):
        return self._y

    @ y.setter
    def y(self, value):
        self._y = round(value, 2)
        self.rect.y = self._y

    def move_on(self, dt):
        # diagonal movement
        if ((self.direction_of_movement.is_up and
            self.direction_of_movement.is_right) or
            (self.direction_of_movement.is_up and
            self.direction_of_movement.is_left) or
            (self.direction_of_movement.is_down and
            self.direction_of_movement.is_right) or
            (self.direction_of_movement.is_down and
                self.direction_of_movement.is_left)):
            # Correct the speed of diagonal movement
            movement_speed = self.movement_speed / sqrt(2)
        else:
            movement_speed = self.movement_speed
        movement_speed = movement_speed * dt * TARGET_FPS
        if self.direction_of_movement.is_up:
            self.y -= movement_speed
        if self.direction_of_movement.is_down:
            self.y += movement_speed
        if self.direction_of_movement.is_right:
            self.x += movement_speed
        if self.direction_of_movement.is_left:
            self.x -= movement_speed

    def center_x_on_screen(self):
        """Center the posistion on the screen"""
        self.x = w_size[0] / 2 - self.rect.width

    def center_y_on_screen(self):
        """Center the posistion on the screen"""
        self.y = w_size[1] / 2 - self.rect.height


class ShooterSprite(Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shot_max_num = 1
        self.shot_que: deque = deque()
        self.shot_interval = 1
        self.is_shot_allowed = True
