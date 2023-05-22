from typing import Callable, Optional

import pygame

from .gametext import GameText
from .utils.misc import ColorValue


class UI:
    def __init__(
        self,
        parent_layout: "UILayout" = None,
        pos: list[int] = [0, 0],
        pos_hint: str = "relative",
    ):
        self.parent_layout: Optional["UILayout"] = parent_layout
        self.pos: list[int] = pos
        self.pos_hint: str = pos_hint
        self.calc_real_size: Callable[..., list[int]] = None

    @property
    def real_size(self):
        if self.calc_real_size is None:
            raise NotImplementedError("calc_real_size is not implemented")
        return self.calc_real_size()

    def draw(self, surface_to_blit: pygame.Surface):
        raise NotImplementedError("draw is not implemented")


class UILayout(UI):
    def __init__(
        self,
        parent_layout: "UILayout" = None,
        pos: list[int] = [0, 0],
        pos_hint: str = "relative",
    ):
        super().__init__(parent_layout=parent_layout, pos=pos, pos_hint=pos_hint)
        self.children: list[UI] = []

    def add_child(self, ui: UI):
        self.children.append(ui)
        self.relocate_children()

    def relocate_children():
        raise NotImplementedError("`relocate_children()` is not implemented")

    def draw(self, surface_to_blit: pygame.Surface):
        for ui in self.children:
            ui.draw(surface_to_blit)


class UIFlowLayout(UILayout):
    def __init__(
        self,
        orientation: str = "vertical",
        parent_layout: "UILayout" = None,
        pos: list[int] = [0, 0],
        pos_hint: str = "relative",
    ):
        super().__init__(parent_layout=parent_layout, pos=pos, pos_hint=pos_hint)
        self.orientation: str = orientation  # or horizontal
        self.spacing_between_children: int = 0

    def relocate_children(self):
        child_sizes = [child.real_size for child in self.children]
        child_heights = [size[1] for size in child_sizes]
        child_widths = [size[0] for size in child_sizes]
        new_child_positions = []
        for i, child in enumerate(self.children):
            if child.pos_hint == "absolute":
                new_child_positions.append(child.pos)
                continue
            if i == 0:
                new_child_positions.append(self.pos)
                child.pos = self.pos
            elif i > 0:
                if self.orientation == "vertical":
                    new_child_positions.append(
                        [self.pos[0], sum(child_heights[1 : i + 1])]
                    )
                elif self.orientation == "horizontal":
                    new_child_positions.append(
                        [sum(child_widths[1 : i + 1]), self.pos[1]]
                    )
        for i, child in enumerate(self.children):
            child.pos = new_child_positions[i]

    def add_child(self, ui: UI):
        self.children.append(ui)
        self.relocate_children()

    def draw(self, surface_to_blit: pygame.Surface):
        for ui in self.children:
            ui.draw(surface_to_blit)


class GameTextUI(UI):
    def __init__(
        self,
        gametext: GameText,
        padding: int = 0,
        parent_layout: "UILayout" = None,
        pos: list[int] = [0, 0],
        pos_hint: str = "relative",
    ):
        super().__init__(parent_layout=parent_layout, pos=pos, pos_hint=pos_hint)
        self.gametext = gametext
        self.padding = padding
        self.calc_real_size = self._calc_real_size

    def _calc_real_size(self) -> list[int]:
        size = list(
            self.gametext.font.lines_and_sizes_of_multilinetext(
                text=self.gametext.text,
                linelength_limit=self.gametext.linelength,
                is_linelength_limit_in_px=self.gametext.is_linelength_in_px,
            )[1]
        )
        size = list(map(lambda w_or_h: w_or_h + self.padding * 2, size))
        return size

    def draw(self, surface_to_blit: pygame.Surface):
        self.gametext.renderln(
            surface_to_blit=surface_to_blit,
            pos_for_surface_to_blit_option=tuple(
                map(sum, zip(self.pos, (self.padding, self.padding)))
            ),
        )


class MsgboxUI(GameTextUI):
    def __init__(
        self,
        gametext: GameText,
        parent_layout: "UILayout" = None,
        pos: list[int] = [0, 0],
        pos_hint: str = "relative",
        frame_width: int = 1,
        frame_color: ColorValue = pygame.Color(255, 255, 255),
    ):
        super().__init__(
            gametext=gametext, parent_layout=parent_layout, pos=pos, pos_hint=pos_hint
        )
        self.frame_width = frame_width
        self.frame_color = frame_color

    def draw(self, surface_to_blit: pygame.Surface):
        super().draw(surface_to_blit)
        pygame.draw.rect(
            surface=surface_to_blit,
            color=self.frame_color,
            rect=[*self.pos, *self.real_size],
            width=self.frame_width,
        )
