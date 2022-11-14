from __future__ import annotations
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .gamelevel import Level

from collections import deque
from math import sqrt

import pygame

# from .gamescene import Scene
from .utilities import Arrow, ArrowToTurnToward
from .__init__ import TARGET_FPS, w_size


class Sprite(pygame.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.scene: Scene
        self.gameworld: Level = None
        self.entity_container: EntityList = None
        self.direction_of_movement = ArrowToTurnToward()
        self.movement_speed = 1
        self._x = 0
        self._y = 0
        self.angle = 0
        self.is_moving = False  # this is True when move_on called
        self.move_target_x = None
        self.move_target_y = None

    # @property
    # def entity_container(self):
    #     return self._entity_container

    # @entity_container.setter
    # def entity_container(self, value):
    #     self._entity_container = value

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
        self.is_moving = True
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

    def remove_from_container(self):
        self.entity_container.kill_living_entity(self)


class ShooterSprite(Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shot_max_num = 1
        self.shot_que: deque = deque()
        self.shot_interval = 1
        self.is_shot_allowed = True


class EntityList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def kill_living_entity(self, entity: Sprite):
        """Do list.remove(entity) if list has it."""
        if entity in self:
            self.remove(entity)

    def append(self, item):
        if not isinstance(item, Sprite):
            raise TypeError("item is not Entity")
        # append the item to itself (the list)
        super().append(item)


class Enemy(Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action = "idle"
        self.behavior_pattern = None
        self.behavior_pattern_dict = {}
        self.behavior_pattern_dict[
            "random_vertical"] = self.move_random_vertical
        self.behavior_pattern_dict[
            "random_horizontal"] = self.move_random_horizontal

    def update(self, dt):
        self.do_pattern(dt)
        if self.is_moving:
            self.action = "move"
        else:
            self.action = "idle"

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)

    def do_pattern(self, dt):
        if self.behavior_pattern is not None:
            self.behavior_pattern_dict[self.behavior_pattern](dt)

    def move_random_vertical(self, dt):
        if not self.move_target_x:
            self.random_destination_x()
        if (self.move_target_x - self.movement_speed
            <= self.x <=
                self.move_target_x + self.movement_speed):
            self.direction_of_movement.unset(Arrow.right)
            self.direction_of_movement.unset(Arrow.left)
            self.random_destination_x()
        elif self.x < self.move_target_x:
            self.direction_of_movement.set(Arrow.right)
            self.direction_of_movement.unset(Arrow.left)
        elif self.move_target_x < self.x:
            self.direction_of_movement.set(Arrow.left)
            self.direction_of_movement.unset(Arrow.right)
        self.move_on(dt)

    def move_random_horizontal(self, dt):
        if not self.move_target_y:
            self.random_destination_y()
        if (self.move_target_y - self.movement_speed
            <= self.y <=
                self.move_target_y + self.movement_speed):
            self.direction_of_movement.unset(Arrow.up)
            self.direction_of_movement.unset(Arrow.down)
            self.random_destination_x()
        elif self.y < self.move_target_y:
            self.direction_of_movement.set(Arrow.down)
            self.direction_of_movement.unset(Arrow.up)
        elif self.move_target_y < self.y:
            self.direction_of_movement.set(Arrow.down)
            self.direction_of_movement.unset(Arrow.up)
        self.move_on(dt)

    def random_destination_x(self):
        self.move_target_x = random.randint(0, w_size[0])

    def random_destination_y(self):
        self.move_target_y = random.randint(0, w_size[1])

    def move_strike_to_entity(self, dt, entity: Sprite):
        if not (self.move_target_x and self.move_target_y):
            self.set_destination_to_entity(entity)
        if (self.move_target_x - self.movement_speed
            <= self.x <=
                self.move_target_x + self.movement_speed):
            self.direction_of_movement.unset(Arrow.right)
            self.direction_of_movement.unset(Arrow.left)
            self.set_destination_to_entity(entity)
        elif self.x < self.move_target_x:
            self.direction_of_movement.set(Arrow.right)
            self.direction_of_movement.unset(Arrow.left)
        elif self.move_target_x < self.x:
            self.direction_of_movement.set(Arrow.left)
            self.direction_of_movement.unset(Arrow.right)
        if (self.move_target_y - self.movement_speed
            <= self.y <=
                self.move_target_y + self.movement_speed):
            self.direction_of_movement.unset(Arrow.up)
            self.direction_of_movement.unset(Arrow.down)

        elif self.y < self.move_target_y:
            self.direction_of_movement.set(Arrow.down)
            self.direction_of_movement.unset(Arrow.up)
        elif self.move_target_y < self.y:
            self.direction_of_movement.set(Arrow.up)
            self.direction_of_movement.unset(Arrow.down)
        self.move_on(dt)

    def set_destination_to_entity(self, entity_type: Sprite):
        entity_list = [
            entity for entity in self.gameworld.entities
            if isinstance(entity, entity_type)]
        self.move_target_x = entity_list[0].x
        self.move_target_y = entity_list[0].y

    def death(self):
        self.remove_from_container()

    def remove_from_container(self):
        self.entity_container.kill_living_entity(self)

    def collide(self, entity: Sprite) -> bool:
        """Return true if a collison occur."""
        if pygame.sprite.collide_rect(entity, self):
            self.death()
            return True
        else:
            return False
