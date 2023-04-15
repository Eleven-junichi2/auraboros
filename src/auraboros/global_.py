"""
Use to define global variables common use in the modules.
"""
import pygame

pygame.init()

display_default_vertex = """
#version 330 core

in vec2 in_vert;
in vec2 in_texcoord;
out vec2 uvs;

void main() {
    uvs = in_texcoord;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""
# display_default_fragment = """
# #version 330 core

# in vec2 uvs;
# out vec4 out_color;

# uniform sampler2D display_texture;
# uniform vec2 resolution;
# uniform float radius;
# uniform float softness;

# void main() {
#     vec4 color = texture(display_texture, uvs);

#     float dist = length(uvs - vec2(0.5));
#     float vignette = smoothstep(radius, radius - softness, dist);

#     out_color = color * vignette;
# }
# """
display_default_fragment = """
#version 330 core

uniform sampler2D display_surface;

in vec2 uvs;
out vec4 entire_screen_color;

void main() {
    entire_screen_color = vec4(
        texture(display_surface, uvs).rgb, 1.0);
}
"""

screen: pygame.surface.Surface
# shader: Shader2D


def init(window_size=(960, 640), caption="", icon_filepath=None,
         pixel_scale=2, set_mode_flags=0):
    """This function initialize pygame and game engine.
    Where to configure settings of game system is here."""
    from . import global_
    global_.TARGET_FPS = 60
    pixel_scale = pixel_scale
    global_.w_size_unscaled = window_size
    global_.w_size = tuple([length // pixel_scale for length in window_size])
    pygame.display.set_mode(global_.w_size_unscaled, set_mode_flags)
    global_.screen = pygame.Surface(global_.w_size)
    pygame.display.set_caption(caption)
    if icon_filepath:
        icon_surf = pygame.image.load(icon_filepath)
        pygame.display.set_icon(icon_surf)
    # if set_mode_flags & (pygame.DOUBLEBUF | pygame.OPENGL):
    #     Shader2D.init()
    #     global_.shader = Shader2D()
