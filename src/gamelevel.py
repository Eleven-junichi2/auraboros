from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Type
if TYPE_CHECKING:
    pass
    # from .eightrail import Enemy

from random import randint

import copy

import pygame

from .entity import Enemy, EnemyFactory, Entity, EntityList, DeadlyObstacle
from .gamescene import Scene
from .utilities import Arrow, open_json_file
from . import global_


class EntityListOfGameWorld(EntityList):
    def __init__(self, gameworld: Level, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gameworld = gameworld

    def kill_living_entity(self, entity: Entity):
        if isinstance(entity, Enemy):
            self.gameworld.num_of_remaining_enemies -= 1
        super().kill_living_entity(entity)

    def append(self, item: Entity):
        if isinstance(item, Enemy):
            self.gameworld.count_of_enemies_summoned += 1
        item.gameworld = self.gameworld
        item.entity_container = self
        super().append(item)


class Level:

    def __init__(self, levelfile_dir, scene=None):
        self.scene: Scene = scene

        self.levelfile_dir = levelfile_dir
        self.level_raw_data = open_json_file(self.levelfile_dir / "level.json")
        self.level_raw_pattern_data = open_json_file(
            levelfile_dir / "patterns.json")
        self.prepare_level_data()

        self._entities = EntityListOfGameWorld(self)
        self.enemy_factory = EnemyFactory()

        self.bg_surf = pygame.surface.Surface(
            (global_.w_size[0], global_.w_size[1] * 2))
        self.scroll_speed = 0.5
        self.density_of_stars_on_bg = randint(100, 500)

        self.pause = False
        self.elapsed_time_in_level = 0
        self.count_of_enemies_killed = 0
        self.count_of_enemies_summoned = 0
        self.reset_num_of_remaining_enemies()

        self.gamescore: int
        self.scoreboard = [0, ]

        self.initialize_level()

    @property
    def entities(self):
        return self._entities

    @entities.setter
    def entities(self, value):
        self._entities = value

    def reset_num_of_remaining_enemies(self):
        self.num_of_remaining_enemies = self.num_of_enemy_on_level()

    def reset_count_of_enemies_summoned(self):
        self.count_of_enemies_summoned = 0

    def entity(self, entity_type: Type[Entity]):
        """Return the entity of specified type which added first to
           entities."""
        entity_list = [
            entity for entity in self.entities
            if isinstance(entity, entity_type)]
        if entity_list:
            return entity_list[0]

    def entities_by_type(self, entity_type: Type[Entity]):
        entity_list = [
            entity for entity in self.entities
            if isinstance(entity, entity_type)]
        if entity_list:
            return entity_list

    def show_hitbox(self):
        self._visible_hitbox()

    def hide_hitbox(self):
        self._invisible_hitbox()

    def _visible_hitbox(self):
        [entity.visible_hitbox() for entity in self.entities]

    def _invisible_hitbox(self):
        [entity.invisible_hitbox() for entity in self.entities]

    def highscore(self):
        self.scoreboard.sort(reverse=True)
        return self.scoreboard[0]

    def enemies(self) -> EntityList[Enemy]:
        enemy_list = [
            enemy for enemy in self.entities if isinstance(enemy, Enemy)]
        return enemy_list

    def deadly_obstacles(self) -> EntityList[DeadlyObstacle]:
        deadly_obstacle_list = [
            deadly_obstacle for deadly_obstacle in self.entities
            if isinstance(deadly_obstacle, DeadlyObstacle)]
        return deadly_obstacle_list

    def num_of_enemy_now(self):
        return len(self.enemies())

    def prepare_level_data(self):
        level = []
        pattern_dict = self.level_raw_pattern_data
        for data in self.level_raw_data:
            decompressed = pattern_dict[data[0]]
            list_ = []
            for dict_ in decompressed:
                new_dict = copy.copy(dict_)
                new_dict["timing"] = dict_["timing"]+data[1]
                list_.append(new_dict)
            level.extend(list_)
        self.level_data = level

    def run_level(self, dt):
        if self.pause:
            return

        for data in self.level_data:
            if round(self.elapsed_time_in_level) == data["timing"]:
                enemy = self.enemy_factory[data["enemy"]]()
                pos: list[int, int] = [None, None]
                for i in range(2):
                    if isinstance(data["pos"][i], str):
                        if data["pos"][i] == "random":
                            pos[i] = randint(0, global_.w_size[i])
                        if data["pos"][i] == "right":
                            pos[i] = global_.w_size[i] - enemy.rect.width
                    else:
                        pos[i] = data["pos"][i]
                enemy.x, enemy.y = pos
                enemy.behavior_pattern = data["pattern"]
                self.entities.append(enemy)

        self.elapsed_time_in_level += 1 * dt * global_.TARGET_FPS

    def process_collision(
            self,
            player_entities: Iterable[Entity],
            weapon_entities: Iterable[Entity]) -> bool:
        for deadly_obstacle in self.deadly_obstacles():
            for weapon in weapon_entities:
                if isinstance(deadly_obstacle, Enemy):
                    if Entity.collide(weapon, deadly_obstacle):
                        self.gamescore += deadly_obstacle.gamescore
                        self.count_of_enemies_killed += 1
                else:
                    Entity.collide(weapon, deadly_obstacle, False)
            for player in player_entities:
                Entity.collide(player, deadly_obstacle)

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

    def num_of_enemy_on_level(self) -> int:
        return len(self.level_data)

    def kill_count_of_enemy(self) -> int:
        return self.count_of_enemies_killed

    # def num_of_remaining_enemy(self) -> int:
    #     return

    def reset_elapsed_time_counter(self):
        self.elapsed_time_in_level = 0

    def clear_enemies(self):
        [enemy.remove_from_container() for enemy in self.enemies()]

    def clear_entities(self):
        self.entities.clear()

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
        self.reset_num_of_remaining_enemies()
        self.reset_count_of_enemies_summoned()

    def clear_enemies_off_screen(self):
        [entity.remove_from_container() for entity in self.enemies()
         if global_.w_size[1] < entity.y or global_.w_size[0] < entity.x
            or entity.x < 0 or entity.y < 0]

    def stop_entity_from_moving_off_screen(self, entity: Entity):
        if global_.w_size[1] < entity.y + entity.rect.height:
            entity.arrow_of_move.unset(Arrow.down)
        if global_.w_size[0] < entity.x + entity.rect.width:
            entity.arrow_of_move.unset(Arrow.right)
        if entity.x < 0:
            entity.arrow_of_move.unset(Arrow.left)
        if entity.y < 0:
            entity.arrow_of_move.unset(Arrow.up)

    def set_background(self):
        [self.bg_surf.fill(
            (randint(0, 255), randint(0, 255), randint(0, 255)),
            ((randint(0, global_.w_size[0]),
              randint(0, global_.w_size[1] * 2)), (1, 1)))
         for i in range(self.density_of_stars_on_bg)]

    def set_background_for_scroll(self):
        new_background = pygame.surface.Surface(
            (global_.w_size[0], global_.w_size[1] * 2))
        new_background.blit(
            self.bg_surf,
            (0, global_.w_size[1], global_.w_size[0], global_.w_size[1]))
        randomize_density = randint(-self.density_of_stars_on_bg // 2,
                                    self.density_of_stars_on_bg // 2)
        [new_background.fill(
            (randint(0, 255), randint(0, 255), randint(0, 255)),
            ((randint(0, global_.w_size[0]), randint(0, global_.w_size[1])),
             (1, 1)))
         for i in range(self.density_of_stars_on_bg + randomize_density)]
        self.bg_surf = new_background

    def scroll(self, dt):
        for enemy in self.enemies():
            enemy.y += self.scroll_speed * 1.25 * dt * global_.TARGET_FPS
        self.bg_scroll_y += self.scroll_speed * dt * global_.TARGET_FPS
        if self.bg_scroll_y > global_.w_size[1]:
            self.bg_scroll_y = 0
            self.set_background_for_scroll()
