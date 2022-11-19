from __future__ import annotations
from inspect import isclass
import random
from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from .gamelevel import Level

from collections import UserDict
from math import sqrt

import pygame

# from .gamescene import Scene
from .utilities import Arrow, ArrowToTurnToward
from .__init__ import TARGET_FPS, w_size


class EntityList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def kill_living_entity(self, entity: Sprite):
        """Do list.remove(entity) if list has it."""
        if entity in self:
            self.remove(entity)

    def append(self, item: Sprite):
        if not isinstance(item, Sprite):
            raise TypeError("item is not Entity")
        super().append(item)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.scene: Scene
        self.gameworld: Level = None
        self.entity_container: EntityList = None
        self.direction_of_movement = ArrowToTurnToward()
        self.movement_speed = 1
        self.image = pygame.surface.Surface((0, 0))
        self.rect = self.image.get_rect()
        self._hitbox = self.image.get_rect()
        self.is_visible_hitbox = False
        self.is_hitbox_on_center = True
        self.invincible_to_entity = False
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
    def hitbox(self):
        return self._hitbox

    @hitbox.setter
    def hitbox(self, value):
        self._hitbox = value

    def center_hitbox_x(self):
        self.hitbox.x = self.x + (self.rect.width - self.hitbox.width) // 2

    def center_hitbox_y(self):
        self.hitbox.y = self.y + (self.rect.height - self.hitbox.height) // 2

    @ property
    def x(self):
        return self._x

    @ x.setter
    def x(self, value):
        self._x = round(value, 2)
        self.rect.x = self._x
        if self.is_hitbox_on_center:
            self.center_hitbox_x()
        else:
            self.hitbox.x = self._x

    @ property
    def y(self):
        return self._y

    @ y.setter
    def y(self, value):
        self._y = round(value, 2)
        self.rect.y = self._y
        self.hitbox.y = self._y
        if self.is_hitbox_on_center:
            self.center_hitbox_y()
        else:
            self.hitbox.y = self._y

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

    def death(self):
        self.remove_from_container()

    @staticmethod
    def collide(entity_a: Sprite, entity_b: Sprite,
                collided=pygame.sprite.collide_rect) -> bool:
        """Each entity executes death() when a collision occurs."""
        is_entity_a_alive = entity_a in entity_a.gameworld.entities
        is_entity_b_alive = entity_a in entity_b.gameworld.entities
        if (entity_a.hitbox.colliderect(entity_b.hitbox)
            and entity_b.hitbox.colliderect(entity_a.hitbox)
                and is_entity_a_alive and is_entity_b_alive):
            # if (collided(entity_a, entity_b)
            #         and is_entity_a_alive and is_entity_b_alive):
            if not entity_a.invincible_to_entity:
                entity_a.death()
            if not entity_b.invincible_to_entity:
                entity_b.death()
            return True
        else:
            return False

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)
        if self.is_visible_hitbox:
            self.draw_hitbox(screen)

    def draw_hitbox(self, screen: pygame.surface.Surface):
        screen.fill((255, 0, 0), self.hitbox)

    def visible_hitbox(self):
        self.is_visible_hitbox = True

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

    def move_random(self, dt):
        v_or_h = random.randint(0, 1)
        if v_or_h == 0:
            self.move_random_vertical(dt)
        elif v_or_h == 1:
            self.move_random_horizontal(dt)

    def random_destination_x(self):
        self.move_target_x = random.randint(0, w_size[0])

    def random_destination_y(self):
        self.move_target_y = random.randint(0, w_size[1])

    def move_strike_to_entity(self, dt, entity_type: Sprite):
        if self.set_destination_to_entity(entity_type):
            self.move_to_destination(dt)

    def move_to_dest_x(self, dt, stop_when_arrived=True):
        if self.move_target_x:
            if (self.move_target_x - self.movement_speed
                + self.hitbox.width
                <= self.x <=
                    self.move_target_x + self.movement_speed
                    - self.hitbox.width) and stop_when_arrived:
                self.direction_of_movement.unset(Arrow.right)
                self.direction_of_movement.unset(Arrow.left)
            elif self.x < self.move_target_x:
                self.direction_of_movement.set(Arrow.right)
                self.direction_of_movement.unset(Arrow.left)
            elif self.move_target_x < self.x:
                self.direction_of_movement.set(Arrow.left)
                self.direction_of_movement.unset(Arrow.right)

    def move_to_dest_y(self, dt, stop_when_arrived=True):
        if self.move_target_y:
            if (self.move_target_y - self.movement_speed
                + self.hitbox.height
                <= self.y <=
                    self.move_target_y + self.movement_speed
                    - self.hitbox.height):
                self.direction_of_movement.unset(Arrow.up)
                self.direction_of_movement.unset(Arrow.down)
            elif self.y < self.move_target_y:
                self.direction_of_movement.set(Arrow.down)
                self.direction_of_movement.unset(Arrow.up)
            elif self.move_target_y < self.y:
                self.direction_of_movement.set(Arrow.up)
                self.direction_of_movement.unset(Arrow.down)

    def move_to_destination(self, dt):
        self.move_to_dest_x(dt)
        self.move_to_dest_y(dt)

    def set_destination_to_entity(self, entity_type: Sprite) -> bool:
        entity_list = [
            entity for entity in self.gameworld.entities
            if isinstance(entity, entity_type)]
        if entity_list:
            self.move_target_x = entity_list[0].hitbox.x
            self.move_target_y = entity_list[0].hitbox.y
            return True
        else:
            return False


class ShooterSprite(Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shot_max_num = 1
        self.shot_interval = 1
        self.is_shot_allowed = True


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
        self.behavior_pattern_dict[
            "random"] = self.move_random
        self.gamescore = 0

    def update(self, dt):
        self.do_pattern(dt)
        if self.is_moving:
            self.action = "move"
        else:
            self.action = "idle"

    def do_pattern(self, dt):
        if self.behavior_pattern is not None:
            self.behavior_pattern_dict[self.behavior_pattern](dt)
            self.move_on(dt)


class EnemyFactory(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, item: Enemy):
        if isclass(item):
            self.data[key] = item
        else:
            raise TypeError("The value must not be instance.")

    def __getitem__(self, key) -> Type[Enemy]:
        return super().__getitem__(key)
