from __future__ import annotations
# from abc import ABCMeta, abstractmethod
from inspect import isclass
import math
import random
from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from .gamelevel import Level

from collections import UserDict
from math import sqrt

import pygame

# from .gamescene import Scene
from .utilities import Arrow, ArrowToTurnToward
from . import global_


class Entity(pygame.sprite.Sprite):
    """
    Attributes:
            gameworld (Level):
                The game level that the entity belongs to.
            entity_container (EntityList):
                The container that holds the entity.
            arrow_of_move (ArrowToTurnToward):
                The arrow of movement for the entity.
            movement_speed (int):
                The movement speed of the entity.
            image (pygame.surface.Surface):
                The image of the entity.
            rect (pygame.Rect):
                The rectangle that encloses the entity's image.
            hitbox (pygame.Rect):
                The rectangle that encloses the entity's hitbox.
            is_visible_hitbox (bool):
                Whether the hitbox of the entity is visible or not.
            is_hitbox_on_center (bool):
                Whether the hitbox of the entity is on the center of the
                entity or not.
            invincible_to_entity (bool):
                Whether the entity is invincible to other entities or not.
            x (float):
                The x-coordinate of the entity.
            y (float):
                The y-coordinate of the entity.
            angle (float):
                The angle of the entity.
            is_moving (bool):
                Whether the entity is moving or not.
            move_dest_x (int):
                The x-coordinate of the destination of the entity's movement.
            move_dest_y (int):
                The y-coordinate of the destination of the entity's movement.
            angle_to_target (float):
                The angle to the target of the entity's movement.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gameworld: Level = None
        self.entity_container: EntityList = None
        self.arrow_of_move = ArrowToTurnToward()
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
        self.is_moving = False  # this is True when move_by func called
        self.move_dest_x = None
        self.move_dest_y = None
        self.angle_to_target = 0

    @ property
    def hitbox(self):
        return self._hitbox

    @hitbox.setter
    def hitbox(self, value):
        self._hitbox = value

    def set_hitbox_x_to_rect_center_x(self):
        self.hitbox.x = self.x + (self.rect.width - self.hitbox.width) // 2

    def set_hitbox_y_to_rect_center_y(self):
        self.hitbox.y = self.y + (self.rect.height - self.hitbox.height) // 2

    @ property
    def x(self):
        return self._x

    @ x.setter
    def x(self, value):
        self._x = round(value, 2)
        self.rect.x = self._x
        if self.is_hitbox_on_center:
            self.set_hitbox_x_to_rect_center_x()
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
            self.set_hitbox_y_to_rect_center_y()
        else:
            self.hitbox.y = self._y

    def set_move_direction(self, direction: Arrow):
        """
        Set the arrow of movement to the specified direction.

        Args:
            direction (Arrow):
                The direction to set the arrow of movement to.
        """
        self.arrow_of_move.set(direction)

    def cancel_move_direction(self, direction: Arrow):
        """
        Unset the arrow of movement from the specified direction.

        Args:
            direction (Arrow):
                The direction to unset the arrow of movement from.
        """
        self.arrow_of_move.unset(direction)

    def move_by_arrow(self):
        """
        Move the entity according to the arrow of movement.

        If the arrow of movement is set to up, down, right, or left,
        the entity moves in that direction at the speed of movement.
        If the arrow of movement is set to up and right, up and left,
        down and right, or down and left, the entity moves diagonally
        at the speed of movement divided by the square root of 2.

        The entity's position is updated accordingly, and the is_moving
        attribute is set to True if the entity is moving, or False
        otherwise.
        """
        if ((self.arrow_of_move.is_up and
            self.arrow_of_move.is_right) or
            (self.arrow_of_move.is_up and
            self.arrow_of_move.is_left) or
            (self.arrow_of_move.is_down and
            self.arrow_of_move.is_right) or
            (self.arrow_of_move.is_down and
                self.arrow_of_move.is_left)):
            # Correct the speed of diagonal movement
            movement_speed = self.movement_speed / sqrt(2)
        else:
            movement_speed = self.movement_speed
        # movement_speed = movement_speed * dt * global_.TARGET_FPS
        movement_speed = movement_speed
        if self.arrow_of_move.is_up:
            self.y -= movement_speed
        if self.arrow_of_move.is_down:
            self.y += movement_speed
        if self.arrow_of_move.is_right:
            self.x += movement_speed
        if self.arrow_of_move.is_left:
            self.x -= movement_speed
        if self.arrow_of_move.is_set_any():
            self.is_moving = True
        else:
            self.is_moving = False

    def move_by_angle(self, dt, radians):
        self.is_moving = True
        self.y += math.sin(radians)*self.movement_speed
        self.x += math.cos(radians)*self.movement_speed

    def set_x_to_center_of_screen(self):
        """Center the posistion on the screen"""
        self.x = global_.w_size[0] / 2 - self.rect.width / 2

    def set_y_to_center_of_screen(self):
        """Center the posistion on the screen"""
        self.y = global_.w_size[1] / 2 - self.rect.height / 2

    def remove_from_container(self):
        self.entity_container.kill_living_entity(self)

    def death(self):
        self.remove_from_container()

    @staticmethod
    def collide(entity_a: Entity, entity_b: Entity,
                death_a=True, death_b=True) -> bool:
        """Each entity executes death() when a collision occurs."""
        is_entity_a_alive = entity_a in entity_a.gameworld.entities
        is_entity_b_alive = entity_a in entity_b.gameworld.entities
        if (entity_a.hitbox.colliderect(entity_b.hitbox)
            and entity_b.hitbox.colliderect(entity_a.hitbox)
                and is_entity_a_alive and is_entity_b_alive):
            # if (collided(entity_a, entity_b)
            #         and is_entity_a_alive and is_entity_b_alive):
            if not entity_a.invincible_to_entity:
                if death_a:
                    entity_a.death()
            if not entity_b.invincible_to_entity:
                if death_b:
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

    def invisible_hitbox(self):
        self.is_visible_hitbox = False

    def set_arrow_random_vertical(self, dt):
        """Set arrow of movement to right or left."""
        if not self.move_dest_x:
            self.random_dest_x()
        if (self.move_dest_x - self.movement_speed
            <= self.x <=
                self.move_dest_x + self.movement_speed):
            self.arrow_of_move.unset(Arrow.right)
            self.arrow_of_move.unset(Arrow.left)
            self.random_dest_x()
        elif self.x < self.move_dest_x:
            self.arrow_of_move.set(Arrow.right)
            self.arrow_of_move.unset(Arrow.left)
        elif self.move_dest_x < self.x:
            self.arrow_of_move.set(Arrow.left)
            self.arrow_of_move.unset(Arrow.right)

    def set_arrow_random_horizontal(self, dt):
        """Set arrow of movement to up or down."""
        if not self.move_dest_y:
            self.random_dest_y()
        if (self.move_dest_y - self.movement_speed
            <= self.y <=
                self.move_dest_y + self.movement_speed):
            self.arrow_of_move.unset(Arrow.up)
            self.arrow_of_move.unset(Arrow.down)
            self.random_dest_x()
        elif self.y < self.move_dest_y:
            self.arrow_of_move.set(Arrow.down)
            self.arrow_of_move.unset(Arrow.up)
        elif self.move_dest_y < self.y:
            self.arrow_of_move.set(Arrow.down)
            self.arrow_of_move.unset(Arrow.up)

    def set_arrow_random(self, dt):
        """Set arrow of movement to up or down, right, or left."""
        v_or_h = random.randint(0, 1)
        if v_or_h == 0:
            self.set_arrow_random_vertical(dt)
        elif v_or_h == 1:
            self.set_arrow_random_horizontal(dt)

    def random_dest_x(self):
        self.move_dest_x = random.randint(0, global_.w_size[0])

    def random_dest_y(self):
        self.move_dest_y = random.randint(0, global_.w_size[1])

    def set_arrow_to_entity_as_dest(self, dt, entity_type: Entity):
        if self.set_destination_to_entity(entity_type):
            self.set_arrow_to_dest(dt)

    def set_arrow_to_dest_x(self, dt, stop_when_arrived=True):
        if self.move_dest_x:
            if (self.move_dest_x - self.movement_speed
                + self.hitbox.width
                <= self.x <=
                    self.move_dest_x + self.movement_speed
                    - self.hitbox.width) and stop_when_arrived:
                self.arrow_of_move.unset(Arrow.right)
                self.arrow_of_move.unset(Arrow.left)
            elif self.x < self.move_dest_x:
                self.arrow_of_move.set(Arrow.right)
                self.arrow_of_move.unset(Arrow.left)
            elif self.move_dest_x < self.x:
                self.arrow_of_move.set(Arrow.left)
                self.arrow_of_move.unset(Arrow.right)

    def set_arrow_to_dest_y(self, dt):
        if self.move_dest_y:
            if (self.move_dest_y - self.movement_speed
                + self.hitbox.height
                <= self.y <=
                    self.move_dest_y + self.movement_speed
                    - self.hitbox.height):
                self.arrow_of_move.unset(Arrow.up)
                self.arrow_of_move.unset(Arrow.down)
            elif self.y < self.move_dest_y:
                self.arrow_of_move.set(Arrow.down)
                self.arrow_of_move.unset(Arrow.up)
            elif self.move_dest_y < self.y:
                self.arrow_of_move.set(Arrow.up)
                self.arrow_of_move.unset(Arrow.down)

    def set_arrow_to_dest(self, dt):
        self.set_arrow_to_dest_x(dt)
        self.set_arrow_to_dest_y(dt)

    def set_destination_to_entity(self, entity_type: Entity) -> bool:
        entity_list = [
            entity for entity in self.gameworld.entities
            if isinstance(entity, entity_type)]
        if entity_list:
            self.move_dest_x = entity_list[0].hitbox.x
            self.move_dest_y = entity_list[0].hitbox.y
            return True
        else:
            return False


class EntityList(list[Entity]):
    def kill_living_entity(self, entity: Entity):
        """Do list.remove(entity) if list has it."""
        if entity in self:
            self.remove(entity)

    def append(self, item: Entity):
        if not isinstance(item, Entity):
            raise TypeError("item is not Entity")
        super().append(item)


class ShooterEntity(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shot_max_num = 1
        self.shot_interval = 1
        self.is_shot_allowed = True


class DeadlyObstacle(Entity):
    pass


class Enemy(DeadlyObstacle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action = "idle"
        self.behavior_pattern = None
        self.behavior_pattern_dict = {}
        self.behavior_pattern_dict[
            "random_vertical"] = self.set_arrow_random_vertical
        self.behavior_pattern_dict[
            "random_horizontal"] = self.set_arrow_random_horizontal
        self.behavior_pattern_dict[
            "random"] = self.set_arrow_random
        self.gamescore = 0

    def update(self, dt):
        self.do_pattern(dt)

    def do_pattern(self, dt):
        if self.behavior_pattern is not None:
            self.behavior_pattern_dict[self.behavior_pattern](dt)
            self.move_by_arrow(dt)


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
