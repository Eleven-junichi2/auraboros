from ..core import Global


def window_size_in_scaled_px():
    """Get the window size, but multiply the pixel size by base_px_scale."""
    return in_scaled_px(Global.screen_size_in_unscaled_px)


def window_size():
    """Get the window size"""
    return Global.screen_size_in_unscaled_px


def in_scaled_px(coordinate) -> tuple[int, int]:
    """
    map(lambda num: num//Global.base_px_scale, pygame.mouse.get_pos())
    """
    return tuple(map(lambda num: num // Global.base_px_scale, coordinate))


def calc_x_to_center(width_of_stuff_to_be_centered: int) -> int:
    return window_size_in_scaled_px()[0] // 2 - width_of_stuff_to_be_centered // 2


def calc_y_to_center(height_of_stuff_to_be_centered: int) -> int:
    return window_size_in_scaled_px()[1] // 2 - height_of_stuff_to_be_centered // 2


def calc_pos_to_center(
    size_of_stuff_to_be_centered: tuple[int, int]
) -> tuple[int, int]:
    return calc_x_to_center(size_of_stuff_to_be_centered[0]), calc_y_to_center(
        size_of_stuff_to_be_centered[1]
    )
