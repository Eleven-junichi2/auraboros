from typing import Union, Sequence

import pygame

RGBAOutput = tuple[int, int, int, int]
ColorValue = Union[
    pygame.color.Color, int, str, tuple[int, int, int], RGBAOutput, Sequence[int]
]


def draw_grid(
    surface_to_draw: pygame.surface.Surface, grid_size: int, color: ColorValue
):
    [
        pygame.draw.rect(
            surface_to_draw,
            color,
            (x * grid_size, y * grid_size) + (grid_size, grid_size),
            1,
        )
        for x in range(surface_to_draw.get_size()[0] // grid_size)
        for y in range(surface_to_draw.get_size()[1] // grid_size)
    ]


def render_rightpointing_triangle(height, color: ColorValue) -> pygame.surface.Surface:
    polygon_points_to_draw = (
        (0, 0),
        (
            height // 2,
            height // 2,
        ),
        (
            0,
            height,
        ),
    )
    surface = pygame.surface.Surface((height // 2, height))
    pygame.draw.polygon(
        surface,
        color,
        polygon_points_to_draw,
    )
    return surface
