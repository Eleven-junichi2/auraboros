"""
Use to define global variables common use in the modules.
"""
import pygame

pygame.init()


screen: pygame.surface.Surface
TARGET_FPS: int
w_size_unscaled: tuple[int, int]
w_size: tuple[int, int]
is_init_called = False


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
    global_.is_init_called = True
