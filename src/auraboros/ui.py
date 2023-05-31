from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Optional
import logging

import pygame

from .gameinput import Mouse
from .gametext import GameText

# from .gametext import Font2, GameText
# from .utils.misc import ColorValue

# --setup logger--
logger = logging.getLogger(__name__)
log_format_str = "%(levelname)s - %(message)s"
console_handler = logging.StreamHandler()
console_handler_formatter = logging.Formatter(log_format_str)
console_handler.setFormatter(console_handler_formatter)
logger.addHandler(console_handler)
# ----


class UI:
    def __init__(
        self,
        pos: list[int],
        fixed_size: list[int] = None,
        tag: Optional[str] = None,
    ):
        self.tag = tag
        self.children: list[UI] = []
        self.parts = UIParts(pos=pos, fixed_size=fixed_size)

    def event(self, event: pygame.event.Event):
        for child in self.children:
            child.event(event)

    def update(self, dt):
        for child in self.children:
            child.update(dt)

    def draw(self, surface_to_blit: pygame.Surface):
        for child in self.children:
            child.draw(surface_to_blit)

    def add_child(self, child: "UI"):
        if isinstance(child, UI):
            self.children.append(child)
        else:
            raise ValueError("`child` must be UI")


@dataclass
class UIParts:
    """The properties for UI"""

    pos: list[int]
    fixed_size: Optional[list[int]]

    def __post_init__(self):
        self.func_to_calc_min_size: Optional[Callable[..., tuple[int, int]]] = None
        self.func_to_calc_real_size: Optional[Callable[..., tuple[int, int]]] = None

    @property
    def real_size(self) -> tuple[int, int]:
        if self.fixed_size:
            size = self.fixed_size
        else:
            if self.func_to_calc_real_size is None:
                raise AttributeError(
                    "`func_to_calc_real_size` is required to get `real_size`"
                )
            size = self.func_to_calc_real_size()
        return size

    @property
    def min_size(self) -> tuple[int, int]:
        if self.func_to_calc_min_size is None:
            raise AttributeError(
                "`func_to_calc_real_size` is required to get `real_size`"
            )
        return self.func_to_calc_min_size()

    def is_given_pos_in_real_size(self, pos: tuple[int, int]):
        x = self.pos[0] <= pos[0] <= self.pos[0] + self.real_size[0]
        y = self.pos[1] <= pos[1] <= self.pos[1] + self.real_size[1]
        return x and y


class Orientation(Enum):
    VERTICAL = auto()
    HORIZONTAL = auto()


@dataclass
class UIFlowLayoutParts(UIParts):
    orientation: Orientation
    spacing: int


class UIFlowLayout(UI):
    def __init__(
        self,
        pos: list[int],
        orientation: Orientation = Orientation.VERTICAL,
        spacing: int = 0,
        fixed_size: list[int] = None,
        tag: Optional[str] = None,
    ):
        self.tag = tag
        self.children: list[UI] = []
        self.parts = UIFlowLayoutParts(
            pos=pos, fixed_size=fixed_size, orientation=orientation, spacing=spacing
        )
        self.parts.func_to_calc_real_size = self.calc_entire_realsize

    def reposition_children(self):
        for child, new_pos in zip(self.children, self.calc_positions_for_children()):
            child.parts.pos = list(new_pos)

    def calc_positions_for_children(
        self,
    ) -> tuple[tuple[int, int], ...]:
        realsizes = [child.parts.real_size for child in self.children]
        fixed_positions = []
        fixed_positions.append((self.parts.pos[0], self.parts.pos[1]))
        for i in range(len(realsizes))[1:]:
            spacing = self.parts.spacing * i if i != len(realsizes) else 0
            if self.parts.orientation == Orientation.VERTICAL:
                fixed_positions.append(
                    (
                        self.parts.pos[0],
                        self.parts.pos[1]
                        + sum([size[1] for size in realsizes[0:i]])
                        + spacing,
                    )
                )
            elif self.parts.orientation == Orientation.HORIZONTAL:
                fixed_positions.append(
                    (
                        self.parts.pos[0]
                        + sum([size[0] for size in realsizes[0:i]])
                        + spacing,
                        self.parts.pos[1],
                    )
                )
        return tuple(fixed_positions)

    def calc_entire_realsize(self) -> tuple[int, int]:
        children_positions = self.calc_positions_for_children()
        children_realsizes = [child.parts.real_size for child in self.children]
        entire_realsize = [0, 0]
        if self.parts.orientation == Orientation.VERTICAL:
            entire_realsize[0] = max(
                [size[0] for size in children_realsizes], default=0
            )
            entire_realsize[1] = (
                children_positions[-1][1]
                + children_realsizes[-1][1]
                - children_positions[0][1]
            )
        elif self.parts.orientation == Orientation.HORIZONTAL:
            entire_realsize[1] = max(
                [size[1] for size in children_realsizes], default=0
            )
            entire_realsize[0] = (
                children_positions[-1][0]
                + children_realsizes[-1][0]
                - children_positions[0][0]
            )
        return tuple(entire_realsize)


@dataclass
class TextUIParts(UIParts):
    gametext: GameText

    def __post_init__(self):
        super().__post_init__()
        self.func_to_calc_min_size = self.calc_min_size
        self.func_to_calc_real_size = self.calc_real_size

    def calc_min_size(self) -> tuple[int, int]:
        return tuple(
            self.gametext.font.lines_and_sizes_of_multilinetext(
                self.gametext.text,
                self.gametext.linelength,
                self.gametext.is_linelength_in_px,
            )[1]
        )

    def calc_real_size(self) -> tuple[int, int]:
        return tuple(self.calc_min_size())


class TextUI(UI):
    def __init__(
        self,
        pos: list[int],
        gametext: GameText,
        fixed_size: Optional[list[int]] = None,
        tag: Optional[str] = None,
    ):
        super().__init__(pos=pos, fixed_size=fixed_size, tag=tag)
        self.parts = TextUIParts(pos=pos, fixed_size=fixed_size, gametext=gametext)

    def draw(self, surface_to_blit: pygame.Surface):
        super().draw(surface_to_blit)
        text_surface = self.parts.gametext.renderln()
        surface_to_blit.blit(
            text_surface, self.parts.pos, (0, 0, *self.parts.real_size)
        )


@dataclass
class ButtonUIParts(TextUIParts):
    pass


class ButtonUI(TextUI):
    def __init__(
        self,
        pos: list[int],
        gametext: GameText,
        on_press: Optional[Callable] = None,
        on_release: Optional[Callable] = None,
        fixed_size: Optional[list[int]] = None,
        tag: Optional[str] = None,
    ):
        super().__init__(pos=pos, gametext=gametext, fixed_size=fixed_size, tag=tag)
        self.parts = ButtonUIParts(pos=pos, fixed_size=fixed_size, gametext=gametext)
        self.mouse = Mouse()
        self._on_press_setter(on_press)
        self._on_release_setter(on_release)

    @property
    def on_press(self) -> Optional[Callable]:
        return self._on_press

    @on_press.setter
    def on_press(self, func: Callable):
        self._on_press_setter(func)

    def _on_press_setter(self, func: Callable):
        self._on_press: Optional[Callable] = func
        if self.on_press:
            self.mouse.register_mouseaction(
                pygame.MOUSEBUTTONDOWN,
                on_left=lambda: self.on_press()
                if self.parts.is_given_pos_in_real_size(pygame.mouse.get_pos())
                else None,
            )

    @property
    def on_release(self) -> Optional[Callable]:
        return self._on_release

    @on_release.setter
    def on_release(self, func: Callable):
        self._on_release_setter(func)

    def _on_release_setter(self, func: Callable):
        self._on_release: Optional[Callable] = func
        if self.on_release:
            self.mouse.register_mouseaction(
                pygame.MOUSEBUTTONUP,
                on_left=lambda: self.on_release()
                if self.parts.is_given_pos_in_real_size(pygame.mouse.get_pos())
                else None,
            )

    def event(self, event: pygame.event.Event):
        self.mouse.event(event)

    def draw(self, surface_to_blit: pygame.Surface):
        super().draw(surface_to_blit)
