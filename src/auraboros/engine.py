import pygame


from .core import init  # noqa
from .core import Global, scale_px_of_pygame_get_surface_display
from .gamescene import SceneManager
from .schedule import Schedule, Stopwatch
from .shader import Shader2D
from .old_ui import UIManager, UI
from .gameinput import KeyboardManager, MouseManager


def run(scene_manager: SceneManager):
    ui_manager = UIManager()
    keyboard_manager = KeyboardManager()
    mouse_manager = MouseManager()
    UI._ui_manager = ui_manager

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
            ui_manager.event(event)
            keyboard_manager.event(event)
            mouse_manager.event(event)
            #  --
        scene_manager.update(dt)
        scene_manager.draw(Global.screen)
        # --
        scale_px_of_pygame_get_surface_display()
        if Global.use_opengl_display:
            # -render opengl-
            shader2d.register_surface_as_texture(Global.screen, "display_surface")
            shader2d.use_texture("display_surface", 0)
            shader2d.render()
            # --
            # -update display-
            pygame.display.flip()
            # --
        else:
            pygame.display.update()

    pygame.quit()
