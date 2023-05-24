# TODO: Make menu system
from dataclasses import dataclass, field
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


class GameTextUI(UI):
    def __init__(
        self,
        gametext: GameText | str,
        parent_layout: "UILayout" = None,
        pos: list[int] = [0, 0],
        pos_hint: str = "relative",
    ):
        super().__init__(parent_layout=parent_layout, pos=pos, pos_hint=pos_hint)
        if isinstance(gametext, str):
            gametext = GameText(gametext)
        elif not isinstance(gametext, GameText):
            raise ValueError("argument `gametext` must be GameText or str")
        self.gametext = gametext
        self.calc_real_size = self._calc_real_size

    def _calc_real_size(self) -> list[int]:
        size = list(
            self.gametext.font.lines_and_sizes_of_multilinetext(
                text=self.gametext.text,
                linelength_limit=self.gametext.linelength,
                is_linelength_limit_in_px=self.gametext.is_linelength_in_px,
            )[1]
        )
        return size

    def draw(self, surface_to_blit: pygame.Surface):
        self.gametext.renderln(
            surface_to_blit=surface_to_blit, pos_for_surface_to_blit_option=self.pos
        )


class MsgboxUI(GameTextUI):
    def __init__(
        self,
        gametext: GameText | str,
        padding: int = 0,
        parent_layout: "UILayout" = None,
        pos: list[int] = [0, 0],
        pos_hint: str = "relative",
        frame_width: int = 1,
        frame_color: ColorValue = pygame.Color(255, 255, 255),
    ):
        super().__init__(
            gametext=gametext, parent_layout=parent_layout, pos=pos, pos_hint=pos_hint
        )
        self.padding = padding
        self.frame_width = frame_width
        self.frame_color = frame_color
        self.calc_real_size = self._calc_real_size

    def _calc_real_size(self) -> list[int]:
        size = list(
            map(
                sum,
                zip(
                    self.gametext.font.lines_and_sizes_of_multilinetext(
                        text=self.gametext.text,
                        linelength_limit=self.gametext.linelength,
                        is_linelength_limit_in_px=self.gametext.is_linelength_in_px,
                    )[1],
                    [self.padding * 2] * 2,
                ),
            )
        )
        return size

    def draw(self, surface_to_blit: pygame.Surface):
        self.gametext.renderln(
            surface_to_blit=surface_to_blit,
            pos_for_surface_to_blit_option=tuple(
                map(
                    sum,
                    zip(
                        self.pos,
                        [
                            self.padding,
                        ]
                        * 2,
                    ),
                )
            ),
        )
        pygame.draw.rect(
            surface=surface_to_blit,
            color=self.frame_color,
            rect=[*self.pos, *self.real_size],
            width=self.frame_width,
        )


class UILayout(UI):
    def __init__(
        self,
        parent_layout: "UILayout" = None,
        pos: list[int] = [0, 0],
        pos_hint: str = "relative",
    ):
        super().__init__(parent_layout=parent_layout, pos=pos, pos_hint=pos_hint)
        self.children: list[UI] = []

    def add_child(self, ui: UI, relocate_children_after_add=True):
        self.children.append(ui)
        if relocate_children_after_add:
            self.relocate_children()

    def relocate_children(self):
        raise NotImplementedError("`relocate_children()` is not implemented")


class UIFlowLayout(UILayout):
    def __init__(
        self,
        orientation: str = "vertical",
        spacing: int = 0,
        parent_layout: "UILayout" = None,
        pos: list[int] = [0, 0],
        pos_hint: str = "relative",
    ):
        super().__init__(parent_layout=parent_layout, pos=pos, pos_hint=pos_hint)
        self.orientation = orientation
        self.spacing = spacing

    def relocate_children(self):
        # print("relocating...")
        child_sizes = tuple(map(lambda child: child.real_size, self.children))
        # print("heights: ", [size[1] for size in child_sizes])
        for i, child in enumerate(self.children):
            if self.pos_hint == "relative":
                if i == 0:
                    child.pos = self.pos
                elif i > 0:
                    if self.orientation == "vertical":
                        child.pos[0] = self.pos[0]
                        child.pos[1] = (
                            sum([size[1] for size in child_sizes][0:i])
                            + self.spacing * i
                        )
                    elif self.orientation == "horizontal":
                        child.pos[0] = (
                            sum([size[0] for size in child_sizes][0:i])
                            + self.spacing * i
                        )
                        child.pos[1] = self.pos[1]
            elif self.pos_hint == "absolute":
                pass
            print(child.pos)

    def draw(self, surface_to_blit: pygame.Surface):
        for child in self.children:
            child.draw(surface_to_blit)


StrAsOptionKey = str
StrToDisplayOption = str


@dataclass
class MenuDatabase:
    options: dict[StrAsOptionKey, StrToDisplayOption] = field(default_factory=dict)
    funcs_on_select: dict[StrAsOptionKey, Optional[Callable]] = field(
        default_factory=dict
    )
    funcs_on_highlight: dict[StrAsOptionKey, Callable] = field(default_factory=dict)

    @property
    def option_count(self) -> int:
        return len(self.options)


class MenuInterface:
    def __init__(
        self,
        database: Optional[MenuDatabase] = None,
        func_on_cursor_up: Optional[Callable] = None,
        func_on_cursor_down: Optional[Callable] = None,
        loop_cursor: bool = True,
    ):
        if database is None:
            database = MenuDatabase()
        self.database: MenuDatabase = database
        self.selected_index: int = 0
        self.loop_cursor: bool = loop_cursor
        self.func_on_cursor_up: Optional[Callable] = func_on_cursor_up
        self.func_on_cursor_down: Optional[Callable] = func_on_cursor_down

    @property
    def options_count(self) -> int:
        return len(self.database.options)

    def add_option(
        self,
        key_str_to_identify_option: str,
        text_to_display: Optional[str] = None,
        func_on_select: Optional[Callable] = None,
        func_on_highlight: Optional[Callable] = None,
    ):
        if text_to_display is None:
            text_to_display = key_str_to_identify_option
        self.database.options[key_str_to_identify_option] = text_to_display
        if func_on_select:
            self.database.funcs_on_select[key_str_to_identify_option] = func_on_select
        if func_on_highlight:
            self.database.funcs_on_highlight[
                key_str_to_identify_option
            ] = func_on_highlight

    def set_func_on_cursor_up(self, func: Callable):
        self.func_on_cursor_up = func

    def set_func_on_cursor_down(self, func: Callable):
        self.func_on_cursor_down = func

    def up_cursor(self):
        if 0 < self.selected_index:
            self.selected_index -= 1
        elif self.loop_cursor:
            self.selected_index = self.options_count - 1
        if self.func_on_cursor_up:
            self.func_on_cursor_up()

    def down_cursor(self):
        print("self.database.option_count", self.database.option_count)
        if self.selected_index < self.database.option_count - 1:
            self.selected_index += 1
        elif self.loop_cursor:
            self.selected_index = 0
        if self.func_on_cursor_down:
            self.func_on_cursor_down()
        print("selected: ", self.selected_index)

    def get_option_key_for_index(self, index: int) -> StrAsOptionKey:
        return tuple(self.database.options.keys())[index]

    def do_func_on_select(self):
        if len(self.database.options) == 0:
            raise AttributeError("At least one menu item is required to take action.")
        func = self.database.funcs_on_select[
            self.get_option_key_for_index(self.selected_index)
        ]
        if func:
            return func()

    def do_func_on_highlight(self):
        if len(self.database.options) == 0:
            raise AttributeError("At least one menu item is required to take action.")
        func = self.database.funcs_on_highlight[
            self.get_option_key_for_index(self.selected_index)
        ]
        if func:
            return func()

    def longest_option_text(self) -> str:
        return max(self.database.options.values(), key=len)

    def get_option_text(self, key_or_current_selected: Optional[str] = None) -> str:
        """
        Args:
        """
        if key_or_current_selected:
            key = key_or_current_selected
        else:
            key = self.get_option_key_for_index(self.selected_index)
        return self.database.options[key]


class OptionsUI(UIFlowLayout):
    def __init__(
        self,
        orientation: str = "vertical",
        spacing: int = 0,
        menusystem_interface: MenuInterface = MenuInterface(),
        parent_layout: "UILayout" = None,
        pos: list[int] = [0, 0],
        pos_hint: str = "relative",
    ):
        super().__init__(
            orientation=orientation,
            spacing=spacing,
            parent_layout=parent_layout,
            pos=pos,
            pos_hint=pos_hint,
        )
        self.interface = menusystem_interface
