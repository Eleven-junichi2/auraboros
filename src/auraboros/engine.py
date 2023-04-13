"""
"""

# from typing import TYPE_CHECKING
# if TYPE_CHECKING:

import pygame

from .global_ import init  # noqa
from .schedule import Schedule
from .gamescene import SceneManager
from . import global_


clock = pygame.time.Clock()


def run(scene_manager: SceneManager, fps_num=60):
    fps = fps_num
    running = True
    display_flags = pygame.display.get_surface().get_flags()
    while running:
        clock.tick(fps)
        Schedule.execute()
        global_.screen.fill((0, 0, 0))
        for event in pygame.event.get():
            running = scene_manager.event(event)
        if display_flags & (pygame.DOUBLEBUF | pygame.OPENGL):
            pass
        scene_manager.update()
        scene_manager.draw(global_.screen)
        pygame.transform.scale(global_.screen, global_.w_size_unscaled,
                               pygame.display.get_surface())
        if display_flags & (pygame.DOUBLEBUF | pygame.OPENGL):
            pygame.display.flip()
        else:
            pygame.display.update()
    pygame.quit()
