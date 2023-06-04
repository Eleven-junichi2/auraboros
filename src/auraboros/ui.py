from dataclasses import dataclass, field
from enum import Enum, auto
from functools import singledispatchmethod
from typing import Callable, Optional, overload
import logging

import pygame

from .gameinput import Keyboard, Mouse
from .gametext import GameText
from .utils.misc import ColorValue

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
        pos: Optional[list[int]] = None,
        fixed_size: Optional[list[int]] = None,
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

    def remove_child(self, child: "UI"):
        if isinstance(child, UI):
            self.children.remove(child)
        else:
            raise ValueError("`child` must be UI")


@dataclass
class UIParts:
    """The properties for UI"""

    pos: Optional[list[int]]
    fixed_size: Optional[list[int]]

    def __post_init__(self):
        self.func_to_calc_min_size: Optional[Callable[..., tuple[int, int]]] = None
        self.func_to_calc_real_size: Optional[Callable[..., tuple[int, int]]] = None
        if self.pos is None:
            self.pos = [0, 0]

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
        pos: list[int] = None,
        orientation: Orientation = Orientation.VERTICAL,
        spacing: int = 0,
        fixed_size: list[int] = None,
        tag: Optional[str] = None,
    ):
        super().__init__(pos=pos, fixed_size=fixed_size, tag=tag)
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
        gametext: GameText,
        pos: Optional[list[int]] = None,
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
        gametext: GameText,
        pos: Optional[list[int]] = None,
        on_press: Optional[Callable] = None,
        on_release: Optional[Callable] = None,
        on_hover: Optional[Callable] = None,
        fixed_size: Optional[list[int]] = None,
        tag: Optional[str] = None,
    ):
        super().__init__(pos=pos, gametext=gametext, fixed_size=fixed_size, tag=tag)
        self.parts = ButtonUIParts(pos=pos, fixed_size=fixed_size, gametext=gametext)
        self.mouse = Mouse()
        self._on_press_setter(on_press)
        self._on_release_setter(on_release)
        self._on_hover_setter(on_hover)

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

    @property
    def on_hover(self) -> Optional[Callable]:
        return self._on_hover

    @on_hover.setter
    def on_hover(self, func: Callable):
        self._on_hover_setter(func)

    def _on_hover_setter(self, func: Callable):
        self._on_hover: Optional[Callable] = func

    def event(self, event: pygame.event.Event):
        self.mouse.event(event)
        if self.parts.is_given_pos_in_real_size(pygame.mouse.get_pos()):
            if self.on_hover:
                self.on_hover()

    def draw(self, surface_to_blit: pygame.Surface):
        super().draw(surface_to_blit)


@dataclass
class Option:
    ui: UI | ButtonUI | TextUI
    key: str
    on_select: Optional[Callable[..., None]] = None
    on_highlight: Optional[Callable[..., None]] = None


@dataclass
class MenuDatabase:
    options: list[Option] = field(default_factory=list)

    @property
    def dict_from_options(self) -> dict[str, Option]:
        return {option.key: option for option in self.options}

    def index_for_key(self, key: str):
        return tuple(self.dict_from_options.keys()).index(key)

    @property
    def options_count(self) -> int:
        return len(self.options)


@dataclass
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

    def add_option(
        self, option: Option, set_func_on_menu_updates_for_ui_event: bool = True
    ):
        if set_func_on_menu_updates_for_ui_event:
            if hasattr(option.ui, "on_hover"):
                if option.ui.on_hover is not None:
                    logger.warning(
                        f"{option.ui}'s on_hover() was set to "
                        + "`lambda: self.move_cursor(option.key)`"
                        + " by `set_func_on_menu_updates_for_ui_event` flag"
                    )
                option.ui.on_hover = lambda: self.move_cursor(option.key)
            if hasattr(option.ui, "on_press"):
                if option.ui.on_press is not None:
                    logger.warning(
                        f"{option.ui}'s on_press() was set to `self.do_func_on_select`"
                        + " by `set_func_on_menu_updates_for_ui_event` flag"
                    )
                option.ui.on_press = self.do_func_on_select

        self.database.options.append(option)

    @singledispatchmethod
    def _remove_option(self, arg):
        raise ValueError(f"Type {type(arg)} cannot be used with remove_option()")

    @_remove_option.register
    def _(self, index: int):
        del self.database.options[index]

    @_remove_option.register
    def _(self, key: str):
        del self.database.options[self.database.index_for_key(key)]

    @_remove_option.register
    def _(self, option: Option):
        self.database.options.remove(option)

    @overload
    def remove_option(self, index: int):
        ...

    @overload
    def remove_option(self, key: str):
        ...

    @overload
    def remove_option(self, option: Option):
        ...

    def remove_option(self, *arg):
        self._remove_option(*arg)

    @singledispatchmethod
    def _move_cursor(self, arg):
        raise ValueError(f"Type {type(arg)} cannot be used with remove_option()")

    @_move_cursor.register
    def _(self, index: int):
        self.selected_index = index

    @_move_cursor.register
    def _(self, key: str):
        self.selected_index = self.database.index_for_key(key)

    @overload
    def move_cursor(self, option_index: int):
        ...

    @overload
    def move_cursor(self, option_key: str):
        ...

    def move_cursor(self, *arg):
        prev_selected = self.selected_index
        self._move_cursor(*arg)
        if not prev_selected != self.selected_index:
            return
        if self.loop_cursor:
            if prev_selected == self.database.options_count - 1:
                # when cursor down with selected last option
                if self.func_on_cursor_down:
                    self.func_on_cursor_down()
                return
            elif prev_selected == 0:
                # when cursor up with selected first option
                if self.func_on_cursor_up:
                    self.func_on_cursor_up()
                return
        if self.selected_index > prev_selected:
            # when cursor down
            if self.func_on_cursor_down:
                self.func_on_cursor_down()
        elif self.selected_index < prev_selected:
            # when cursor up
            if self.func_on_cursor_up:
                self.func_on_cursor_up()

    def set_func_on_cursor_up(self, func: Callable):
        self.func_on_cursor_up = func

    def set_func_on_cursor_down(self, func: Callable):
        self.func_on_cursor_down = func

    def up_cursor(self):
        if 0 < self.selected_index:
            self.selected_index -= 1
        elif self.loop_cursor:
            self.selected_index = self.database.options_count - 1
        if self.func_on_cursor_up:
            self.func_on_cursor_up()

    def down_cursor(self):
        if self.selected_index < self.database.options_count - 1:
            self.selected_index += 1
        elif self.loop_cursor:
            self.selected_index = 0
        if self.func_on_cursor_down:
            self.func_on_cursor_down()

    def do_func_on_select(self):
        if self.database.options[self.selected_index].on_select:
            return self.database.options[self.selected_index].on_select()

    def do_func_on_highlight(self):
        if self.database.options[self.selected_index].on_highlight:
            return self.database.options[self.selected_index].on_highlight()

    @property
    def current_selected(self):
        return self.database.options[self.selected_index]


class HighlightStyle(Enum):
    CURSOR = auto()
    FILL_BG = auto()
    FRAME_BG = auto()


@dataclass
class MenuParts(UIFlowLayoutParts):
    highlight_fg_color: ColorValue
    highlight_bg_color: ColorValue
    highlight_style: HighlightStyle


class MenuUI(UIFlowLayout):
    def __init__(
        self,
        pos: Optional[list[int]] = None,
        interface: Optional[MenuInterface] = None,
        orientation: Orientation = Orientation.VERTICAL,
        spacing: int = 0,
        highlight_fg_color: ColorValue = pygame.Color(220, 220, 220),
        highlight_bg_color: ColorValue = pygame.Color(78, 78, 78),
        highlight_style: HighlightStyle = HighlightStyle.FILL_BG,
        fixed_size: list[int] = None,
        tag: Optional[str] = None,
    ):
        super().__init__(
            pos=pos,
            fixed_size=fixed_size,
            tag=tag,
            orientation=orientation,
            spacing=spacing,
        )
        self.parts = MenuParts(
            pos=pos,
            fixed_size=fixed_size,
            orientation=orientation,
            spacing=spacing,
            highlight_fg_color=highlight_fg_color,
            highlight_bg_color=highlight_bg_color,
            highlight_style=highlight_style,
        )
        self.parts.func_to_calc_real_size = self.calc_entire_realsize
        if interface:
            self.interface = interface
        else:
            self.interface = MenuInterface(database=MenuDatabase())
        self.keyboard = Keyboard()

    @property
    def database(self) -> MenuDatabase:
        return self.interface.database

    def update_children_on_menu(self):
        # TODO: improve performance
        self.children.clear()
        [self.add_child(option.ui) for option in self.interface.database.options]

    def event(self, event: pygame.event.Event):
        super().event(event)
        self.keyboard.event(event)

    def draw(self, surface_to_blit: pygame.Surface):
        if self.parts.highlight_style == HighlightStyle.FILL_BG:
            pygame.draw.rect(
                surface_to_blit,
                self.parts.highlight_bg_color,
                (
                    *self.children[self.interface.selected_index].parts.pos,
                    *self.children[self.interface.selected_index].parts.real_size,
                ),
            )
        elif self.parts.highlight_style == HighlightStyle.FRAME_BG:
            pygame.draw.rect(
                surface_to_blit,
                self.parts.highlight_bg_color,
                (
                    *self.children[self.interface.selected_index].parts.pos,
                    *self.children[self.interface.selected_index].parts.real_size,
                ),
                width=1,
            )
        elif self.parts.highlight_style == HighlightStyle.CURSOR:
            # TODO: implement this block
            pass
        super().draw(surface_to_blit)
