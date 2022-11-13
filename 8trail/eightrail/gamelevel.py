from __future__ import annotations
from typing import TYPE_CHECKING, Any, Union
if TYPE_CHECKING:
    from .eightrail import Enemy

from dataclasses import dataclass
from random import randint

import pygame

from .entity import Sprite, EntityList
from .gamescene import Scene
from .utilities import open_json_file
from .__init__ import w_size

# TODO: destroy garbage enemy


class EntityListOfGameWorld(EntityList):
    def __init__(self, gameworld: Level, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gameworld = gameworld

    def append(self, item: Sprite):
        item.entity_container = self
        super().append(item)


class EnemyList(EntityListOfGameWorld):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def append(self, item):
        self.gameworld.entities.append(item)
        super().append(item)

    def remove(self, item):
        self.gameworld.entities.remove(item)
        super().remove(item)


class Level:

    def __init__(self, level_filepath, scene=None):
        self.scene: Scene = scene
        self.level = open_json_file(level_filepath)
        self._entities = EntityListOfGameWorld(self)
        self.enemy_factory: dict[Any, Enemy] = {}
        self._enemies: EnemyList[Enemy] = EnemyList(self)
        self.bg_surf = pygame.surface.Surface(
            (w_size[0], w_size[1] * 2))
        self.scroll_speed = 0.5
        self.density_of_stars_on_bg = randint(100, 500)
        self.reset_level()

    @property
    def entities(self):
        return self._entities

    @entities.setter
    def entities(self, value):
        self._entities = value

    @property
    def enemies(self):
        return self._enemies

    @enemies.setter
    def enemies(self, value):
        self._enemies = value

    def run_level(self):
        for data in self.level:
            if self.elapsed_time_in_level == data["timing"]:
                enemy = self.enemy_factory[data["enemy"]]()
                pos: list[int, int] = [None, None]
                for i in range(2):
                    if isinstance(data["pos"][i], str):
                        if data["pos"][i] == "random":
                            pos[i] = randint(0, w_size[i])
                    else:
                        pos[i] = data["pos"][i]
                enemy.x, enemy.y = pos
                enemy.scene = self.scene
                # enemy.entity_container = self.entities
                self.enemies.append(enemy)
        self.elapsed_time_in_level += 1

    def reset_level(self):
        self.elapsed_time_in_level = 0
        self.bg_scroll_y = 0
        self.bg_scroll_x = 0

    # def add_enemy(self, enemy: Enemy):
    #     self.enemies.append(enemy)
        # self.scene.sprites.add(enemy)

    def set_background(self):
        [self.bg_surf.fill(
            (randint(0, 255), randint(0, 255), randint(0, 255)),
            ((randint(0, w_size[0]), randint(0, w_size[1] * 2)), (1, 1)))
         for i in range(self.density_of_stars_on_bg)]

    def set_background_for_scroll(self):
        new_background = pygame.surface.Surface((w_size[0], w_size[1] * 2))
        new_background.blit(
            self.bg_surf, (0, w_size[1], w_size[0], w_size[1]))
        randomize_density = randint(-self.density_of_stars_on_bg // 2,
                                    self.density_of_stars_on_bg // 2)
        [new_background.fill(
            (randint(0, 255), randint(0, 255), randint(0, 255)),
            ((randint(0, w_size[0]), randint(0, w_size[1])),
             (1, 1)))
         for i in range(self.density_of_stars_on_bg + randomize_density)]
        self.bg_surf = new_background

    def scroll(self):
        for enemy in self.enemies:
            enemy.y += self.scroll_speed * 1.25
        self.bg_scroll_y += self.scroll_speed
        if self.bg_scroll_y > w_size[1]:
            self.bg_scroll_y = 0
            self.set_background_for_scroll()


@dataclass
class LevelData:
    timing: int
    enemy: str
    pos: list[Union[str, int], Union[str, int]]
