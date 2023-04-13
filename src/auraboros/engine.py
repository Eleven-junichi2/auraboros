from array import array

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
        vertex_shader = """
        #version 330 core

        in vec2 in_vert;
        in vec2 in_texcoord;
        out vec2 uvs;

        void main() {
            uvs = in_texcoord;
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
        """
        fragment_shader = """
        #version 330 core

        uniform sampler2D entire_screen_texture;

        in vec2 uvs;
        out vec4 entire_screen_color;

        void main() {
            entire_screen_color = vec4(
                texture(entire_screen_texture, uvs).rgb, 1.0);
        }
        """
        shader2d.compile_and_register_program(
            vertex_shader, fragment_shader, "display")
        # ---
    else:
        opengl_is_used = False

    running = True

    while running:
        Schedule.execute()
        global_.screen.fill((0, 0, 0))
        if opengl_is_used:
            pass
        for event in pygame.event.get():
            running = scene_manager.event(event)
        scene_manager.update()
        scene_manager.draw(global_.screen)
        pygame.transform.scale(global_.screen, global_.w_size_unscaled,
                               pygame.display.get_surface())
        if opengl_is_used:
            shader2d.register_surface_as_texture(global_.screen, "display")
            shader2d.render("display", "display", "entire_screen_texture")
            pygame.display.flip()
        else:
            pygame.display.update()
        clock.tick(fps)
    pygame.quit()
