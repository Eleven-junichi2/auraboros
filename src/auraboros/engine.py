from typing import Callable
import pygame


from .core import init  # noqa
from .core import Global, scale_px_of_pygame_get_surface_display
from .gamescene import SceneManager
from .schedule import Schedule, Stopwatch
from .shader import Shader2D

DeltaTime = float
PygameEvent = pygame.event.Event


def run(
    scene_manager: SceneManager,
    mod_for_mainloop: Callable = None,
    mod_for_eventloop: Callable = None,
):
    """
    Args:
        scene_manager (SceneManager): _description_
        mod_for_mainloop (Callable, optional):
            Append and do given func for mainloop.
            this is useful to provide the engine mainloop section for thirdparty
            pygame package.
        mod_for_eventloop (Callable, optional):
            Append and do given func for eventloop.
            this is useful to provide the engine eventloop section for thirdparty
            pygame package.
    """
    clock = pygame.time.Clock()

    if Global.use_opengl_display:
        shader2d = Shader2D()

    running_flag = True
    while running_flag:
        # -control FPS and return delta time-
        dt = clock.tick(Global.fps)
        # --
        # -update timers-
        Stopwatch.update_all_stopwatch(dt)
        Schedule.execute()
        # --
        # -clear screen surface-
        Global.screen.fill((0, 0, 0))
        # --
        # -game scene-
        for event in pygame.event.get():
            # -process pygame events in all of scenes-
            running_flag = scene_manager.event(event)
            if func := mod_for_eventloop:
                func(event)
            #  --
        if func := mod_for_mainloop:
            func(dt)
        scene_manager.update(dt)
        scene_manager.draw(Global.screen)
        # --
        scale_px_of_pygame_get_surface_display()
        if Global.use_opengl_display:
            # -render opengl-
            shader2d.register_surface_as_texture(
                Global.screen, Global.texture_name_for_pygame_display
            )
            shader2d.use_texture(Global.texture_name_for_pygame_display, 0)
            shader2d.render()
            # --
            # -update display-
            pygame.display.flip()
            # --
        else:
            pygame.display.update()

    pygame.quit()
