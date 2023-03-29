"""
Use to define global variables common use in the modules.
You can reflect changes of global variables in a module to
other modules using them.
"""
import pygame

pygame.init()


def init(window_size=(960, 640), caption="", icon_filepath=None,
         pixel_scale=2):
    """This function initialize pygame and game engine.
    Where to configure settings of game system is here."""
    from . import global_
    global_.TARGET_FPS = 60
    pixel_scale = pixel_scale
    global_.w_size_unscaled = window_size
    global_.w_size = tuple([length // pixel_scale for length in window_size])
    pygame.display.set_mode(global_.w_size_unscaled)
    global_.screen = pygame.Surface(global_.w_size)
    pygame.display.set_caption(caption)
    if icon_filepath:
        icon_surf = pygame.image.load(icon_filepath)
        pygame.display.set_icon(icon_surf)
