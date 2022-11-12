from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .eightrail import Enemy

from random import randint

import pygame

from .gamescene import Scene
from .utilities import open_json_file
from .__init__ import w_size


class Level:

    def __init__(self, level_filepath, scene=None):
        self.scene: Scene = scene
        self.stage_data = open_json_file(level_filepath)
        self.enemies: list[Enemy] = []
        self.bg_surf = pygame.surface.Surface(
            (w_size[0], w_size[1] * 2))
        self.bg_scroll_y = 0
        self.bg_scroll_x = 0
        self.density_of_stars_on_bg = randint(100, 500)

    def add_enemy(self, enemy: Enemy):
        self.enemies.append(enemy)

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
            enemy.y += 1
        self.bg_scroll_y += 1
        if self.bg_scroll_y > w_size[1]:
            self.bg_scroll_y = 0
            self.set_background_for_scroll()
