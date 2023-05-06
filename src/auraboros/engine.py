import pygame


from .global_ import init  # noqa
from .gamescene import SceneManager
from .schedule import Schedule, Stopwatch
from . import global_
from .shader import Shader2D

clock = pygame.time.Clock()


def run(scene_manager: SceneManager, fps=60):
    display_flags = pygame.display.get_surface().get_flags()
    if display_flags & (pygame.DOUBLEBUF | pygame.OPENGL):
        opengl_is_used = True
        shader2d = Shader2D()
    else:
        opengl_is_used = False

    running = True

    while running:
        # -control FPS and return delta time-
        dt = clock.tick(fps)
        # ---
        # -update timers of all stopwatch instances-
        Stopwatch.update_all_stopwatch(dt)
        # ---
        Schedule.execute()
        global_.screen.fill((0, 0, 0))
        if opengl_is_used:
            pass
        for event in pygame.event.get():
            running = scene_manager.event(event)
        scene_manager.update(dt)
        scene_manager.draw(global_.screen)
        pygame.transform.scale(
            global_.screen,
            global_.w_size_unscaled,
            pygame.display.get_surface(),
        )
        if opengl_is_used:
            shader2d.register_surface_as_texture(
                global_.screen, "display_surface"
            )
            shader2d.use_texture("display_surface", 0)
            shader2d.render()
            pygame.display.flip()
        else:
            pygame.display.update()

    pygame.quit()
