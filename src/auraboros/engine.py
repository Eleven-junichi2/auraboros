from array import array

import moderngl
import pygame

from .global_ import init  # noqa
from .gamescene import SceneManager
from .schedule import Schedule
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
        opengl_is_used = True
        # - prepare for convert pygame surface to opengl texture -
        ctx = moderngl.create_context()
        buffer = ctx.buffer(data=array("f", [
            # x, y, u ,v
            -1.0, 1.0, 0.0, 0.0,  # top left
            1.0, 1.0, 1.0, 0.0,  # top right
            -1.0, -1.0, 0.0, 1.0,  # bottom left
            1.0, -1.0, 1.0, 1.0,  # bottom right
        ]))
        vertex_shader = """
        #version 330 core

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            gl_Position = vec4(vert, 0.0, 1.0);
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
        program = ctx.program(
            vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        vao = ctx.vertex_array(
            program, [(buffer, "2f 2f", "vert", "texcoord")])
        texture: moderngl.Texture = None
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
            if texture is None:
                texture = surface_to_texture(ctx, global_.screen)
            else:
                texture.write(global_.screen.get_view("1"))
            texture.use(0)
            program["entire_screen_texture"].value = 0
            vao.render(mode=moderngl.TRIANGLE_STRIP)
            pygame.display.flip()
        else:
            pygame.display.update()
        clock.tick(fps)
    pygame.quit()
