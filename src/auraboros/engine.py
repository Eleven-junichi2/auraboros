"""
"""

# from typing import TYPE_CHECKING
# if TYPE_CHECKING:

import pygame

from .global_ import init  # noqa
from .schedule import IntervalCounter
from .gamescene import SceneManager
from . import global_


clock = pygame.time.Clock()


def run(scene_manager: SceneManager, fps_num=60):
    fps = fps_num
    running = True
    while running:
        dt = clock.tick(fps)/1000  # dt means delta time

        global_.screen.fill((0, 0, 0))
        for event in pygame.event.get():
            running = scene_manager.event(event)

        scene_manager.update(dt)
        scene_manager.draw(global_.screen)
        pygame.transform.scale(global_.screen, global_.w_size_unscaled,
                               pygame.display.get_surface())
        pygame.display.update()
        IntervalCounter.tick(dt)
    pygame.quit()
