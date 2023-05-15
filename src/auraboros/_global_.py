"""
This module is DEPRECATED
"""

import os

import pygame

os.environ["SDL_IME_SHOW_UI"] = "1"

pygame.init()


screen: pygame.surface.Surface
TARGET_FPS: int
w_size_unscaled: tuple[int, int]
w_size: tuple[int, int]
is_init_called = False


def init(
    window_size=(960, 640),
    caption="",
    icon_filepath=None,
    pixel_scale=1,
    set_mode_flags=0,
    stop_handling_textinput_events_at_init=True,
):
    """
    This function initialize pygame and game engine.
    Where to configure settings of game system is here.

    Args:
        start_handling_textinput_events_at_init (bool):
            pygame.key.stop_text_input() if True,
            pygame.key.start_text_input() if False.

    """
    from . import global_

    if stop_handling_textinput_events_at_init:
        pygame.key.stop_text_input()
    else:
        pygame.key.start_text_input()

    global_.TARGET_FPS = 60
    global_.PIXEL_SCALE = pixel_scale
    global_.w_size_unscaled = window_size
    global_.w_size = tuple([length // global_.PIXEL_SCALE for length in window_size])
    pygame.display.set_mode(global_.w_size_unscaled, set_mode_flags)
    global_.screen = pygame.Surface(global_.w_size)
    pygame.display.set_caption(caption)
    if icon_filepath:
        icon_surf = pygame.image.load(icon_filepath)
        pygame.display.set_icon(icon_surf)
    global_.is_init_called = True
