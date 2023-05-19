import pygame


from .core import init  # noqa
from .core import Global, scale_px_of_display_from_pygame_get_surface
from .gamescene import SceneManager
from .schedule import Schedule, Stopwatch
from .shader import Shader2D


def run(scene_manager: SceneManager):
    clock = pygame.time.Clock()

    if Global.use_opengl_display:
        shader2d = Shader2D()

    running = True

    while running:
        # -control FPS and return delta time-
        dt = clock.tick(Global.fps)
        # ---
        # -update timers of all stopwatch instances-
        Stopwatch.update_all_stopwatch(dt)
        # ---
        Schedule.execute()
        Global.screen.fill((0, 0, 0))
        for event in pygame.event.get():
            running = scene_manager.event(event)
        scene_manager.update(dt)
        scene_manager.draw(Global.screen)
        scale_px_of_display_from_pygame_get_surface()
        if Global.use_opengl_display:
            shader2d.register_surface_as_texture(Global.screen, "display_surface")
            shader2d.use_texture("display_surface", 0)
            shader2d.render()
            pygame.display.flip()
        else:
            pygame.display.update()

    pygame.quit()
