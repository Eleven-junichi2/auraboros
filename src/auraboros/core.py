import os

import pygame

os.environ["SDL_IME_SHOW_UI"] = "1"


class Global:
    """
    Where to configure the game engine settings and store as global data.

    Attributes:
        is_initialized:
            This attr means whether the 'core.init' function has been called,
            NOT ABOUT THIS CLASS.
    """

    fps: int = None
    screen: pygame.surface.Surface = None
    base_px_scale: float = None
    is_initialized: bool = False
    use_opengl_display: bool = False
    screen_size_in_unscaled_px: tuple[int, int] = None
    shrinked_screen_size_for_scale_px: tuple[int, int] = None
    is_scale_px_of_display_from_pygame_get_surface_called: bool = False
    texture_name_for_pygame_display: str = "pygame_display"

    def __init__(self):
        raise Exception("Global cannot be instantiated.")


def init(
    window_size=(960, 640),
    caption="",
    icon_filepath=None,
    fps: int = 60,
    base_pixel_scale: float = 1.0,
    display_set_mode_flags=0,
    stop_handling_textinput_events_at_init=True,
):
    """
    This function initialize pygame and the game engine.

    Args:
        start_handling_textinput_events_at_init (bool):
            pygame.key.stop_text_input() if True,
            pygame.key.start_text_input() if False.
        display_set_mode_flags (int):
            pygame.display.set_mode(flags=display_set_mode_flags)
    """
    pygame.init()

    # --configure fps--
    Global.fps = fps

    # --configure text input events--
    if stop_handling_textinput_events_at_init:
        pygame.key.stop_text_input()
    else:
        pygame.key.start_text_input()
    # ----

    # --configure global screen surface--
    if display_set_mode_flags & pygame.OPENGL:
        Global.use_opengl_display = True
    else:
        Global.use_opengl_display = False

    Global.base_px_scale = base_pixel_scale
    Global.screen_size_in_unscaled_px = window_size
    Global.screen = pygame.Surface(Global.screen_size_in_unscaled_px)
    Global.shrinked_screen_size_for_scale_px = tuple(
        [length // Global.base_px_scale for length in Global.screen_size_in_unscaled_px]
    )
    pygame.display.set_mode(Global.screen_size_in_unscaled_px, display_set_mode_flags)
    pygame.display.set_caption(caption)
    if icon_filepath:
        icon_surface = pygame.image.load(icon_filepath)
        pygame.display.set_icon(icon_surface)
    # ----
    Global.is_initialized = True


def scale_px_of_pygame_get_surface_display():
    if not Global.is_scale_px_of_display_from_pygame_get_surface_called:
        Global.screen = pygame.Surface(Global.shrinked_screen_size_for_scale_px)
        Global.is_scale_px_of_display_from_pygame_get_surface_called = True
    pygame.transform.scale(
        Global.screen,
        Global.screen_size_in_unscaled_px,
        pygame.display.get_surface(),
    )
