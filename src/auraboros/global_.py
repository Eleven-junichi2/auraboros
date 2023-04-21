"""
Use to define global variables common use in the modules.
"""
from functools import wraps

import pygame

pygame.init()


screen: pygame.surface.Surface
TARGET_FPS: int
w_size_unscaled: tuple[int, int]
w_size: tuple[int, int]
is_init_called = False


class IntOfMousePosForDrawToScaledScrn(int):
    """engine.init時のpixel_scale>=2の場合、マウスの座標をpixel_scale倍にしてdraw系関数に
    渡すことで、描画時のマウスの位置とのズレを防ぐことができるため、マウスの座標であると認識
    させる名前のためのint継承クラス。"""
    def __new__(cls, num):
        return super().__new__(cls, num)

    def __add__(self, other):
        return IntOfMousePosForDrawToScaledScrn(super().__add__(other))

    def __sub__(self, other):
        return IntOfMousePosForDrawToScaledScrn(super().__sub__(other))

    def __mul__(self, other):
        return IntOfMousePosForDrawToScaledScrn(super().__mul__(other))

    def __truediv__(self, other):
        return IntOfMousePosForDrawToScaledScrn(super().__truediv__(other))

    def __floordiv__(self, other):
        return IntOfMousePosForDrawToScaledScrn(super().__floordiv__(other))

    def __mod__(self, other):
        return IntOfMousePosForDrawToScaledScrn(super().__mod__(other))

    def __divmod__(self, other):
        return tuple(
            map(IntOfMousePosForDrawToScaledScrn, super().__divmod__(other)))

    def __pow__(self, other, modulo=None):
        return IntOfMousePosForDrawToScaledScrn(super().__pow__(other, modulo))


def _fix_dislodge_between_givenpos_and_drawpos(
        func_which_has_pos_as_return):
    """decorator"""
    @wraps(func_which_has_pos_as_return)
    def wrapper(*args, **kwargs):
        pos = func_which_has_pos_as_return(*args, **kwargs)
        x = IntOfMousePosForDrawToScaledScrn(pos[0])
        y = IntOfMousePosForDrawToScaledScrn(pos[1])
        # isinstance(x, IntOfMousePosForDrawToScaledScrn) -> True
        # isinstance(1, IntOfMousePosForDrawToScaledScrn -> False
        # return pos, tuple(map(lambda num: num//pixel_scale, pos))
        return (x, y)
    return wrapper


def _decorate_draw(func, pixel_scale):
    """decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        new_args = list(map(lambda arg: list(
            arg) if isinstance(arg, tuple) else arg, args))
        let_fix_pos = False
        is_kwargs_set = False
        if func.__name__ == "rect" or func.__name__ == "ellipse":
            if isinstance(args[2][0], IntOfMousePosForDrawToScaledScrn):
                let_fix_pos = True
            if "rect" in kwargs:
                if isinstance(kwargs["rect"][0],
                              IntOfMousePosForDrawToScaledScrn):
                    let_fix_pos = True
                    is_kwargs_set = True
            if isinstance(args[2][1], IntOfMousePosForDrawToScaledScrn):
                let_fix_pos = True
            if "rect" in kwargs:
                if isinstance(kwargs["rect"][1],
                              IntOfMousePosForDrawToScaledScrn):
                    let_fix_pos = True
                    is_kwargs_set = True
            if let_fix_pos:
                new_args[2][0] = args[2][0]//pixel_scale
                new_args[2][1] = args[2][1]//pixel_scale
                if is_kwargs_set:
                    kwargs["rect"][0] = new_args[2][0]
                    kwargs["rect"][1] = new_args[2][1]
        elif func.__name__ == "line":
            if isinstance(args[2][0], IntOfMousePosForDrawToScaledScrn):
                let_fix_pos = True
            if "start_pos" in kwargs:
                if kwargs["start_pos"][0]:
                    let_fix_pos = True
                    is_kwargs_set = True
            if isinstance(args[2][1], IntOfMousePosForDrawToScaledScrn):
                let_fix_pos = True
            if "start_pos" in kwargs:
                if kwargs["start_pos"][1]:
                    let_fix_pos = True
                    is_kwargs_set = True
            if let_fix_pos:
                new_args[2][0] = args[2][0]//pixel_scale
                new_args[2][1] = args[2][1]//pixel_scale
                if is_kwargs_set:
                    kwargs["start_pos"][0] = new_args[2][0]
                    kwargs["start_pos"][1] = new_args[2][1]
            let_fix_pos = False
            is_kwargs_set = False
            if isinstance(args[3][0], IntOfMousePosForDrawToScaledScrn):
                let_fix_pos = True
            if is_kwargs_set:
                if kwargs["end_pos"][0]:
                    let_fix_pos = True
                    is_kwargs_set = True
            if isinstance(args[3][1], IntOfMousePosForDrawToScaledScrn):
                let_fix_pos = True
            if is_kwargs_set:
                if kwargs["end_pos"][1]:
                    let_fix_pos = True
                    is_kwargs_set = True
            if let_fix_pos:
                new_args[3][0] = args[3][0]//pixel_scale
                new_args[3][1] = args[3][1]//pixel_scale
                if is_kwargs_set:
                    kwargs["end_pos"][0] = new_args[3][0]
                    kwargs["end_pos"][1] = new_args[3][1]
        new_args = list(map(lambda arg: tuple(
            arg) if isinstance(arg, list) else arg, new_args))
        return func(*new_args, **kwargs)
    return wrapper


def init(window_size=(960, 640), caption="", icon_filepath=None,
         pixel_scale=1, set_mode_flags=0,
         decorate_pygame_draw_for_pixel_scale=False):
    """This function initialize pygame and game engine.
    Where to configure settings of game system is here."""
    from . import global_
    global_.TARGET_FPS = 60
    global_.PIXEL_SCALE = pixel_scale
    global_.w_size_unscaled = window_size
    global_.w_size = tuple(
        [length // global_.PIXEL_SCALE for length in window_size])
    pygame.display.set_mode(global_.w_size_unscaled, set_mode_flags)
    global_.screen = pygame.Surface(global_.w_size)
    pygame.display.set_caption(caption)
    if icon_filepath:
        icon_surf = pygame.image.load(icon_filepath)
        pygame.display.set_icon(icon_surf)
    global_.is_init_called = True
    if decorate_pygame_draw_for_pixel_scale and global_.PIXEL_SCALE > 1:
        pygame.mouse.get_pos = _fix_dislodge_between_givenpos_and_drawpos(
            pygame.mouse.get_pos)
        pygame.draw.rect = _decorate_draw(
            pygame.draw.rect, global_.PIXEL_SCALE)
        pygame.draw.ellipse = _decorate_draw(
            pygame.draw.ellipse, global_.PIXEL_SCALE)
        pygame.draw.line = _decorate_draw(
            pygame.draw.line, global_.PIXEL_SCALE)
        # pygame.surface.Surface.blit = _decorate_draw(
        #     pygame.surface.Surface.blit, pixel_scale)
