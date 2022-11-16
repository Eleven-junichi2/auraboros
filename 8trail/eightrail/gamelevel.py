from __future__ import annotations
# from collections import UserList
# from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable
if TYPE_CHECKING:
    pass
    # from .eightrail import Enemy

import copy
# from dataclasses import dataclass
# import itertools
from random import randint

import pygame

from .entity import Sprite, EntityList, Enemy, EnemyFactory
from .gamescene import Scene
from .utilities import Arrow, open_json_file
from .__init__ import w_size, TARGET_FPS


# TODO: destroy garbage enemy


class EntityListOfGameWorld(EntityList):
    def __init__(self, gameworld: Level, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gameworld = gameworld

    def append(self, item: Sprite):
        item.gameworld = self.gameworld
        item.entity_container = self
        super().append(item)


class Level:

    def __init__(self, level_filepath, scene=None):
        self.scene: Scene = scene

        self.level_raw_data = open_json_file(level_filepath)
        self._set_level_data_with_tag_decompressed(
            self.read_tagged_level_data())

        self._entities = EntityListOfGameWorld(self)
        self.enemy_factory = EnemyFactory()

        self.bg_surf = pygame.surface.Surface(
            (w_size[0], w_size[1] * 2))
        self.scroll_speed = 0.5
        self.density_of_stars_on_bg = randint(100, 500)

        self.pause = False
        self.elapsed_time_in_level = 0

        self.gamescore: int
        self.scoreboard = [0, ]

        self.initialize_level()

    @property
    def entities(self):
        return self._entities

    @entities.setter
    def entities(self, value):
        self._entities = value

    def highscore(self):
        self.scoreboard.sort(reverse=True)
        return self.scoreboard[0]

    def enemies(self) -> list[Enemy]:
        enemy_list = [
            enemy for enemy in self.entities if isinstance(enemy, Enemy)]
        return enemy_list

    def run_level(self, dt):
        if self.pause:
            return

        for data in self.level:
            if round(self.elapsed_time_in_level) == data["timing"]:
                enemy = self.enemy_factory[data["enemy"]]()
                pos: list[int, int] = [None, None]
                for i in range(2):
                    if isinstance(data["pos"][i], str):
                        if data["pos"][i] == "random":
                            pos[i] = randint(0, w_size[i])
                    else:
                        pos[i] = data["pos"][i]
                enemy.x, enemy.y = pos
                enemy.behavior_pattern = data["pattern"]
                self.entities.append(enemy)
        self.elapsed_time_in_level += 1 * dt * TARGET_FPS

    def process_collision(
            self,
            player_entities: Iterable[Sprite],
            weapon_entities: Iterable[Sprite]) -> bool:
        """Return True if a player hit a enemy."""
        for enemy in self.enemies():
            for weapon in weapon_entities:
                if Sprite.collide(weapon, enemy):
                    self.gamescore += enemy.gamescore
            for player in player_entities:
                Sprite.collide(player, enemy)

    def register_gamescore(self):
        self.scoreboard.append(self.gamescore)

    def read_tagged_level_data(self):
        data_dict_by_tag = {}
        for data in self.level_raw_data:
            if isinstance(data, list):
                without_str = list(filter(
                    lambda item: not isinstance(item, list),
                    self.level_raw_data))
                data_dict_by_tag[data[0]] = [
                    item for item in without_str if item["tag"] == data[0]]
        return data_dict_by_tag

    def _set_level_data_with_tag_decompressed(self, data_dict_by_tag):
        level = []
        timing_list = []
        for data in self.level_raw_data:
            if isinstance(data, list):
                level.append(data_dict_by_tag[data[0]])
                timing_list.append(data[1])
        new_level = []
        for data_list, timing in zip(level, timing_list):
            for data in data_list:
                data_ = copy.copy(data)
                data_["timing"] += timing
                new_level.append(data_)
        self.level = new_level

    def reset_elapsed_time_counter(self):
        self.elapsed_time_in_level = 0

    def clear_enemies(self):
        [enemy.remove_from_container() for enemy in self.enemies()]

    def clear_entities(self):
        [entity.remove_from_container() for entity in self.enemies()]

    def reset_scroll(self):
        self.bg_scroll_y = 0
        self.bg_scroll_x = 0

    def summon_enemies_with_timing_resetted(self):
        self.clear_enemies()
        self.reset_elapsed_time_counter()

    def reset_score(self):
        self.gamescore = 0

    def initialize_level(self):
        self.clear_entities()
        self.reset_elapsed_time_counter()
        self.reset_scroll()
        self.reset_score()

    def clear_enemies_off_screen(self):
        [entity.remove_from_container() for entity in self.enemies()
         if w_size[1] < entity.y or w_size[0] < entity.x
            or entity.x < 0 or entity.y < 0]

    def stop_entity_from_moving_off_screen(self, entity: Sprite):
        if w_size[1] < entity.y + entity.rect.height:
            entity.direction_of_movement.unset(Arrow.down)
        if w_size[0] < entity.x + entity.rect.width:
            entity.direction_of_movement.unset(Arrow.right)
        if entity.x < 0:
            entity.direction_of_movement.unset(Arrow.left)
        if entity.y < 0:
            entity.direction_of_movement.unset(Arrow.up)

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

    def scroll(self, dt):
        for enemy in self.enemies():
            enemy.y += self.scroll_speed * 1.25 * dt * TARGET_FPS
        self.bg_scroll_y += self.scroll_speed  * dt * TARGET_FPS
        if self.bg_scroll_y > w_size[1]:
            self.bg_scroll_y = 0
            self.set_background_for_scroll()


# @dataclass
# class LevelData:
#     timing: int
#     enemy: str
#     pos: list[Union[str, int], Union[str, int]]
