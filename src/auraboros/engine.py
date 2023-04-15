import moderngl
import pygame

from .global_ import init  # noqa
from .gamescene import SceneManager
from .schedule import Schedule
from .shader import Shader2D
from . import global_

clock = pygame.time.Clock()


def surface_to_texture(ctx: moderngl.Context, surface: pygame.surface.Surface):
    texture = ctx.texture(surface.get_size(), 4)
    texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
    # texture.swizzle = "BGRA" if windows
    return texture


def run(scene_manager: SceneManager, fps=60):
    display_flags = pygame.display.get_surface().get_flags()
    if display_flags & (pygame.DOUBLEBUF | pygame.OPENGL):
        shader2d = Shader2D()
        opengl_is_used = True
        # - prepare for convert display surface to opengl texture -
        shader2d.compile_and_register_program(
            global_.base_display_vertex,
            global_.base_display_fragment, "display")
        # ---
    else:
        opengl_is_used = False

    running = True

    while running:
        dt = clock.tick(fps)
        Schedule.execute()
        global_.screen.fill((0, 0, 0))
        if opengl_is_used:
            pass
        for event in pygame.event.get():
            running = scene_manager.event(event)
        scene_manager.update(dt)
        scene_manager.draw(global_.screen)
        pygame.transform.scale(global_.screen, global_.w_size_unscaled,
                               pygame.display.get_surface())
        if opengl_is_used:
            shader2d.set_uniform("display", "radius", 0.8)
            shader2d.set_uniform("display", "softness", 0.5)
            shader2d.register_surface_as_texture(global_.screen, "display")
            shader2d.use_texture("display", 0)
            shader2d.render("display", "display_texture")
            pygame.display.flip()
        else:
            pygame.display.update()
        
    pygame.quit()
