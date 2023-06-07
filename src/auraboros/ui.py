# TODO: refactoring

from dataclasses import InitVar, dataclass, field
from enum import Enum, auto
from functools import singledispatchmethod
from typing import Callable, Optional, overload
import logging

import pygame


from .gameinput import Keyboard, Mouse
from .gametext import GameText
from .utils.coordinate import in_scaled_px

# --setup logger--
logger = logging.getLogger(__name__)
log_format_str = "%(levelname)s - %(message)s"
console_handler = logging.StreamHandler()
console_handler_formatter = logging.Formatter(log_format_str)
console_handler.setFormatter(console_handler_formatter)
logger.addHandler(console_handler)
# ----


class Orientation(Enum):
    VERTICAL = auto()
    HORIZONTAL = auto()


class FrameStyle(Enum):
    BORDER = auto()
    IMAGE = auto()


@dataclass
class Size:
    fixed: Optional[list[int]] = None
    calc_min: Optional[Callable[..., tuple[int, int]]] = None
    calc_real: Optional[Callable[..., tuple[int, int]]] = None
    is_min_frozen_after_first_calc: bool = False
    is_real_frozen_after_first_calc: bool = False

    def __post_init__(self):
        self._latest_min = None
        self._latest_real = None

    @property
    def min(self) -> tuple[int, int]:
        if self.calc_min:
            if not self.is_min_frozen_after_first_calc or self._latest_min is None:
                size = self.calc_min()
                self._latest_min = size
            else:
                size = self._latest_min
            return size
        else:
            raise AttributeError(
                "`calc_min` func is required to calculate minimum size"
            )

    @property
    def real(self) -> tuple[int, int]:
        if self.fixed:
            return tuple(self.fixed)
        if self.calc_real:
            if not self.is_real_frozen_after_first_calc or self._latest_real is None:
                size = self.calc_real()
                self._latest_real = size
            else:
                size = self._latest_real
            return size
        else:
            raise AttributeError("`calc_real` func is required to calculate real size")

    def set_func_to_calc_min(self, func: Callable[..., tuple[int, int]]):
        self.calc_min = func

    def set_func_to_calc_real(self, func: Callable[..., tuple[int, int]]):
        self.calc_real = func


class UI:
    def __init__(
        self,
        pos: Optional[list[int]] = None,
        fixed_size: Optional[list[int]] = None,
        tag: Optional[str] = None,
        on_hover: Optional[Callable] = None,
    ):
        if pos is None:
            pos = [0, 0]
        self.pos: Optional[list[int]] = pos
        self.size = Size(fixed=fixed_size)
        self.tag: str = tag
        self.on_hover = on_hover

    def event(self, event: pygame.event.Event):
        if self.on_hover:
            if self.is_givenpos_over_ui(in_scaled_px(pygame.mouse.get_pos())):
                self.on_hover()

    def update(self, dt):
        pass

    def draw(self, surface_to_blit: pygame.Surface):
        pass

    def is_givenpos_over_ui(self, pos: tuple[int, int]) -> bool:
        x = self.pos[0] <= pos[0] <= self.pos[0] + self.size.real[0]
        y = self.pos[1] <= pos[1] <= self.pos[1] + self.size.real[1]
        return x and y


@dataclass
class Frame:
    style: Optional[FrameStyle] = None
    width: int = 0
    color: pygame.Color = field(default_factory=lambda: pygame.Color(255, 255, 255))
    radius: Optional[int] = None

    def draw(self, surface_to_blit, pos, size):
        if self.style == FrameStyle.BORDER:
            if self.radius:
                radius = self.radius
            else:
                radius = -1
            pygame.draw.rect(
                surface_to_blit,
                self.color,
                (*pos, *size),
                self.width,
                radius,
            )


@dataclass
class Padding:
    top_or_all_side_size: InitVar[int] = 0
    bottom: InitVar[Optional[int]] = None
    left: InitVar[Optional[int]] = None
    right: InitVar[Optional[int]] = None

    def __post_init__(self, top_or_all_size_size, bottom, left, right):
        self.top: int = top_or_all_size_size
        if bottom:
            self.bottom: int = bottom
        else:
            self.bottom: int = top_or_all_size_size
        if left:
            self.left: int = left
        else:
            self.left: int = top_or_all_size_size
        if right:
            self.right: int = right
        else:
            self.right: int = top_or_all_size_size

    def set_size_for_all_side(self, size: int):
        self.top = size
        self.bottom = size
        self.left = size
        self.right = size


class UIContainer(UI):
    def __init__(
        self,
        pos: Optional[list[int]] = None,
        fixed_size: Optional[list[int]] = None,
        tag: Optional[str] = None,
        padding: Padding = None,
        on_hover: Optional[Callable] = None,
    ):
        super().__init__(pos=pos, fixed_size=fixed_size, tag=tag, on_hover=on_hover)
        if padding is None:
            padding = Padding()
        self.padding = padding
        self.children: list[UI] = []

    def event(self, event: pygame.event.Event):
        super().event(event)
        for child in self.children:
            child.event(event)

    def update(self, dt):
        super().update(dt)
        for child in self.children:
            child.update(dt)

    def draw(self, surface_to_blit: pygame.Surface):
        super().draw(surface_to_blit)
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


class UIFlowLayout(UIContainer):
    def __init__(
        self,
        pos: list[int] = None,
        fixed_size: list[int] = None,
        tag: Optional[str] = None,
        padding: Padding = None,
        spacing: int = 0,
        frame: Optional[Frame] = None,
        orientation: Orientation = Orientation.VERTICAL,
        on_hover: Optional[Callable] = None,
    ):
        super().__init__(pos, fixed_size, tag, padding=padding, on_hover=on_hover)
        self.spacing = spacing
        self.orientation = orientation
        if frame is None:
            frame = Frame()
        self.frame = frame
        self.size.set_func_to_calc_min(self._calc_size_min)
        self.size.set_func_to_calc_real(self._calc_size_real)

    def relocate_children(self):
        for child, new_pos in zip(self.children, self.calc_poss_for_children()):
            child.pos = list(new_pos)

    def calc_poss_for_children(
        self,
    ) -> tuple[tuple[int, int], ...]:
        realsizes = [child.size.real for child in self.children]
        fixed_positions = []
        fixed_positions.append(
            (
                self.padding.left + self.pos[0],
                self.padding.top + self.pos[1],
            )
        )
        for i in range(len(realsizes))[1:]:
            spacing = self.spacing * i if i != len(realsizes) else 0
            if self.orientation == Orientation.VERTICAL:
                fixed_positions.append(
                    (
                        self.padding.left + self.pos[0],
                        self.padding.top
                        + self.pos[1]
                        + sum([size[1] for size in realsizes[0:i]])
                        + spacing,
                    )
                )
            elif self.orientation == Orientation.HORIZONTAL:
                fixed_positions.append(
                    (
                        self.padding.left
                        + self.pos[0]
                        + sum([size[0] for size in realsizes[0:i]])
                        + spacing,
                        self.padding.top + self.pos[1],
                    )
                )
        return tuple(fixed_positions)

    def _calc_size_min(self) -> tuple[int, int]:
        children_positions = self.calc_poss_for_children()
        if len(self.children) > 0:
            children_realsizes = [child.size.real for child in self.children]
        else:
            children_realsizes = [(0, 0)]
        min_size = [0, 0]
        if self.orientation == Orientation.VERTICAL:
            min_size[0] = max([size[0] for size in children_realsizes], default=0)
            min_size[1] = (
                children_positions[-1][1]
                + children_realsizes[-1][1]
                - children_positions[0][1]
            )
        elif self.orientation == Orientation.HORIZONTAL:
            min_size[1] = max([size[1] for size in children_realsizes], default=0)
            min_size[0] = (
                children_positions[-1][0]
                + children_realsizes[-1][0]
                - children_positions[0][0]
            )
        return tuple(min_size)

    def _calc_size_real(self) -> tuple[int, int]:
        return (
            self.padding.left + self.size.min[0] + self.padding.right,
            self.padding.top + self.size.min[1] + self.padding.bottom,
        )

    def draw(self, surface_to_blit: pygame.surface.Surface):
        super().draw(surface_to_blit)
        self.frame.draw(surface_to_blit, self.pos, self.size.real)


class TextUI(UI):
    def __init__(
        self,
        gametext: GameText,
        pos: Optional[list[int]] = None,
        fixed_size: Optional[list[int]] = None,
        tag: Optional[str] = None,
        on_hover: Optional[Callable] = None,
    ):
        super().__init__(pos=pos, fixed_size=fixed_size, tag=tag, on_hover=on_hover)
        self.gametext = gametext
        self.size.set_func_to_calc_min(self._calc_size_min)
        self.size.set_func_to_calc_real(self._calc_size_real)

    def draw(self, surface_to_blit: pygame.Surface):
        super().draw(surface_to_blit)
        text_surface = self.gametext.renderln()
        surface_to_blit.blit(
            text_surface,
            self.pos,
            (0, 0, *self.size.real),
        )

    def _calc_size_min(self) -> tuple[int, int]:
        return tuple(
            self.gametext.font.lines_and_sizes_of_multilinetext(
                self.gametext.text,
                self.gametext.linelength,
                self.gametext.is_linelength_in_px,
            )[1]
        )

    def _calc_size_real(self) -> tuple[int, int]:
        return self.size.min


class TextAlignment(Enum):
    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()


class TextButtonUI(UI):
    def __init__(
        self,
        gametext: GameText,
        pos: Optional[list[int]] = None,
        fixed_size: Optional[list[int]] = None,
        tag: Optional[str] = None,
        padding: Optional[Padding] = None,
        frame: Optional[Frame] = None,
        bg_color: pygame.Color = pygame.Color(0, 0, 0, 0),
        text_alignment: TextAlignment = TextAlignment.CENTER,
        on_hover: Optional[Callable] = None,
        on_press: Optional[Callable] = None,
        on_release: Optional[Callable] = None,
    ):
        super().__init__(
            pos=pos,
            fixed_size=fixed_size,
            tag=tag,
            on_hover=on_hover,
        )
        self.size = Size(
            fixed=fixed_size,
            calc_min=self._calc_size_min,
            calc_real=self._calc_size_real,
            is_real_frozen_after_first_calc=True,
        )
        self.gametext = gametext
        if padding is None:
            padding = Padding()
        self.padding = padding
        if frame is None:
            frame = Frame()
        self.frame = frame
        self.bg_color = bg_color
        self.text_alignment = text_alignment
        self.mouse = Mouse()
        self._on_press_setter(on_press)
        self._on_release_setter(on_release)

    def draw(self, surface_to_blit: pygame.Surface):
        radius = -1
        if self.frame.style == FrameStyle.BORDER:
            if self.frame.radius:
                radius = self.frame.radius
        pygame.draw.rect(
            surface_to_blit,
            self.bg_color,
            (*self.pos, *self.size.real),
            0,
            radius,
        )
        super().draw(surface_to_blit)
        self.gametext.color_background = self.bg_color
        text_surface = self.gametext.renderln()
        match self.text_alignment:
            case TextAlignment.CENTER:
                text_pos = (
                    self.pos[0] + self.size.real[0] // 2 - self.size.min[0] // 2,
                    self.pos[1] + self.size.real[1] // 2 - self.size.min[1] // 2,
                )
            case TextAlignment.LEFT:
                text_pos = (
                    self.pos[0] + self.padding.left + self.frame.width,
                    self.pos[1] + self.size.real[1] // 2 - self.size.min[1] // 2,
                )
            case TextAlignment.RIGHT:
                text_pos = (
                    self.pos[0]
                    + self.size.real[0]
                    - self.size.min[0]
                    - self.padding.right
                    - self.frame.width,
                    self.pos[1] + self.size.real[1] // 2 - self.size.min[1] // 2,
                )
        surface_to_blit.blit(
            text_surface,
            text_pos,
            (0, 0, *self.size.real),
        )
        self.frame.draw(surface_to_blit, self.pos, self.size.real)

    def _calc_size_min(self) -> tuple[int, int]:
        return tuple(
            self.gametext.font.lines_and_sizes_of_multilinetext(
                self.gametext.text,
                self.gametext.linelength,
                self.gametext.is_linelength_in_px,
            )[1]
        )

    def _calc_size_real(self) -> tuple[int, int]:
        return tuple(
            map(
                sum,
                zip(
                    self._calc_size_min(),
                    (
                        self.padding.left + self.padding.right + self.frame.width * 2,
                        self.padding.top + self.padding.bottom + self.frame.width * 2,
                    ),
                ),
            )
        )

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
                if self.is_givenpos_over_ui(pygame.mouse.get_pos())
                else None,
            )

    @property
    def on_release(self) -> Optional[Callable]:
        return self._on_release

    @on_release.setter
    def on_release(self, func: Optional[Callable]):
        self._on_release_setter(func)

    def _on_release_setter(self, func: Optional[Callable]):
        self._on_release: Optional[Callable] = func
        if self.on_release:
            self.mouse.register_mouseaction(
                pygame.MOUSEBUTTONUP, on_left=lambda: self.on_release()
            )

    def event(self, event: pygame.event.Event):
        super().event(event)
        self.mouse.event(event)


# @dataclass
# class Option:
#     ui: UI | ButtonUI | TextUI
#     key: str
#     on_select: Optional[Callable[..., None]] = None
#     on_highlight: Optional[Callable[..., None]] = None


# @dataclass
# class MenuDatabase:
#     options: list[Option] = field(default_factory=list)

#     @property
#     def dict_from_options(self) -> dict[str, Option]:
#         return {option.key: option for option in self.options}

#     def index_for_key(self, key: str):
#         return tuple(self.dict_from_options.keys()).index(key)

#     @property
#     def options_count(self) -> int:
#         return len(self.options)


# @dataclass
# class MenuInterface:
#     def __init__(
#         self,
#         database: Optional[MenuDatabase] = None,
#         func_on_cursor_up: Optional[Callable] = None,
#         func_on_cursor_down: Optional[Callable] = None,
#         loop_cursor: bool = True,
#     ):
#         if database is None:
#             database = MenuDatabase()
#         self.database: MenuDatabase = database
#         self.selected_index: int = 0
#         self.loop_cursor: bool = loop_cursor
#         self.func_on_cursor_up: Optional[Callable] = func_on_cursor_up
#         self.func_on_cursor_down: Optional[Callable] = func_on_cursor_down

#     def add_option(
#         self, option: Option, set_func_on_menu_updates_for_ui_event: bool = True
#     ):
#         if set_func_on_menu_updates_for_ui_event:
#             if hasattr(option.ui, "on_hover"):
#                 if option.ui.on_hover is not None:
#                     logger.warning(
#                         f"{option.ui}'s on_hover() was set to "
#                         + "`lambda: self.move_cursor(option.key)`"
#                         + " by `set_func_on_menu_updates_for_ui_event` flag"
#                     )
#                 option.ui.on_hover = lambda: self.move_cursor(option.key)
#             if hasattr(option.ui, "on_press"):
#                 if option.ui.on_press is not None:
#                     logger.warning(
#                         f"{option.ui}'s on_press() was set to `self.do_func_on_select`"
#                         + " by `set_func_on_menu_updates_for_ui_event` flag"
#                     )
#                 option.ui.on_press = self.do_func_on_select
#         self.database.options.append(option)

#     @singledispatchmethod
#     def _remove_option(self, arg):
#         raise ValueError(f"Type {type(arg)} cannot be used with remove_option()")

#     @_remove_option.register
#     def _(self, index: int):
#         del self.database.options[index]

#     @_remove_option.register
#     def _(self, key: str):
#         del self.database.options[self.database.index_for_key(key)]

#     @_remove_option.register
#     def _(self, option: Option):
#         self.database.options.remove(option)

#     @overload
#     def remove_option(self, index: int):
#         ...

#     @overload
#     def remove_option(self, key: str):
#         ...

#     @overload
#     def remove_option(self, option: Option):
#         ...

#     def remove_option(self, *arg):
#         self._remove_option(*arg)

#     @singledispatchmethod
#     def _move_cursor(self, arg):
#         raise ValueError(f"Type {type(arg)} cannot be used with remove_option()")

#     @_move_cursor.register
#     def _(self, index: int):
#         self.selected_index = index

#     @_move_cursor.register
#     def _(self, key: str):
#         self.selected_index = self.database.index_for_key(key)

#     @overload
#     def move_cursor(self, option_index: int):
#         ...

#     @overload
#     def move_cursor(self, option_key: str):
#         ...

#     def move_cursor(self, *arg):
#         prev_selected = self.selected_index
#         self._move_cursor(*arg)
#         if not prev_selected != self.selected_index:
#             return
#         if self.loop_cursor:
#             if prev_selected == self.database.options_count - 1:
#                 # when cursor down with selected last option
#                 if self.func_on_cursor_down:
#                     self.func_on_cursor_down()
#                 return
#             elif prev_selected == 0:
#                 # when cursor up with selected first option
#                 if self.func_on_cursor_up:
#                     self.func_on_cursor_up()
#                 return
#         if self.selected_index > prev_selected:
#             # when cursor down
#             if self.func_on_cursor_down:
#                 self.func_on_cursor_down()
#         elif self.selected_index < prev_selected:
#             # when cursor up
#             if self.func_on_cursor_up:
#                 self.func_on_cursor_up()

#     def set_func_on_cursor_up(self, func: Callable):
#         self.func_on_cursor_up = func

#     def set_func_on_cursor_down(self, func: Callable):
#         self.func_on_cursor_down = func

#     def up_cursor(self):
#         if 0 < self.selected_index:
#             self.selected_index -= 1
#         elif self.loop_cursor:
#             self.selected_index = self.database.options_count - 1
#         if self.func_on_cursor_up:
#             self.func_on_cursor_up()

#     def down_cursor(self):
#         if self.selected_index < self.database.options_count - 1:
#             self.selected_index += 1
#         elif self.loop_cursor:
#             self.selected_index = 0
#         if self.func_on_cursor_down:
#             self.func_on_cursor_down()

#     def do_func_on_select(self):
#         if self.database.options[self.selected_index].on_select:
#             return self.database.options[self.selected_index].on_select()

#     def do_func_on_highlight(self):
#         if self.database.options[self.selected_index].on_highlight:
#             return self.database.options[self.selected_index].on_highlight()

#     @property
#     def current_selected(self):
#         return self.database.options[self.selected_index]


# class HighlightStyle(Enum):
#     CURSOR = auto()
#     FILL_BG = auto()
#     FRAME_BG = auto()
#     RECOLOR_GAMETEXT_FG = auto()


# @dataclass
# class MenuParts(UIFlowLayoutParts):
#     highlight_fg_color: ColorValue
#     highlight_bg_color: ColorValue
#     color_for_recoloring_gametext: ColorValue
#     highlight_style: HighlightStyle
#     cursor_char: str


# class MenuUI(UIFlowLayout):
#     def __init__(
#         self,
#         pos: Optional[list[int]] = None,
#         interface: Optional[MenuInterface] = None,
#         orientation: Orientation = Orientation.VERTICAL,
#         spacing: int = 0,
#         highlight_fg_color: ColorValue = pygame.Color(144, 144, 144),
#         highlight_bg_color: ColorValue = pygame.Color(78, 78, 78),
#         highlight_style: HighlightStyle = HighlightStyle.FILL_BG,
#         fixed_size: list[int] = None,
#         padding: int = 0,
#         frame_style: Optional[FrameStyle] = None,
#         frame_color: Optional[ColorValue] = None,
#         frame_width: int = 1,
#         frame_radius: Optional[int] = None,
#         color_for_recoloring_gametext: Optional[ColorValue] = None,
#         cursor_char: str = "▶",
#         tag: Optional[str] = None,
#     ):
#         """
#         Args:
#             color_for_recoloring_gametext (Optional[ColorValue], optional):
#                 `highlight_style`に`HighlightStyle.RECOLOR_GAMETEXT_FG`を指定した際の色として使われる。
#                 Noneの場合、その色は`GameText.color_foreground`を反転したものを使う。
#         """
#         super().__init__(
#             pos=pos,
#             fixed_size=fixed_size,
#             tag=tag,
#             orientation=orientation,
#             spacing=spacing,
#             padding=padding,
#             frame_width=frame_width,
#             frame_color=frame_color,
#             frame_style=frame_style,
#             frame_radius=frame_radius,
#         )
#         self.parts = MenuParts(
#             pos=pos,
#             fixed_size=fixed_size,
#             orientation=orientation,
#             spacing=spacing,
#             highlight_fg_color=highlight_fg_color,
#             highlight_bg_color=highlight_bg_color,
#             highlight_style=highlight_style,
#             padding=padding,
#             frame_width=frame_width,
#             frame_style=frame_style,
#             frame_color=frame_color,
#             frame_radius=frame_radius,
#             color_for_recoloring_gametext=color_for_recoloring_gametext,
#             cursor_char=cursor_char,
#         )
#         self.parts.func_to_calc_real_size = self.calc_entire_realsize
#         if interface:
#             self.interface = interface
#         else:
#             self.interface = MenuInterface(database=MenuDatabase())
#         self.keyboard = Keyboard()

#     @property
#     def database(self) -> MenuDatabase:
#         return self.interface.database

#     def update_children_on_menu(self):
#         # TODO: improve performance
#         self.children.clear()
#         [self.add_child(option.ui) for option in self.interface.database.options]

#     def event(self, event: pygame.event.Event):
#         super().event(event)
#         self.keyboard.event(event)

#     def draw(self, surface_to_blit: pygame.Surface):
#         recolor_gametext_fg_flag = False
#         highlight_with_cursor_flag = False
#         # -draw highlighting-
#         match self.parts.highlight_style:
#             case HighlightStyle.FILL_BG:
#                 pygame.draw.rect(
#                     surface_to_blit,
#                     self.parts.highlight_bg_color,
#                     (
#                         *self.children[self.interface.selected_index].parts.pos,
#                         *self.children[self.interface.selected_index].parts.real_size,
#                     ),
#                 )
#             case HighlightStyle.FRAME_BG:
#                 pygame.draw.rect(
#                     surface_to_blit,
#                     self.parts.highlight_bg_color,
#                     (
#                         *self.children[self.interface.selected_index].parts.pos,
#                         *self.children[self.interface.selected_index].parts.real_size,
#                     ),
#                     width=1,
#                 )
#             case HighlightStyle.RECOLOR_GAMETEXT_FG:
#                 if hasattr(
#                     self.children[self.interface.selected_index].parts, "gametext"
#                 ):
#                     recolor_gametext_fg_flag = True
#                     gametext_color = self.children[
#                         self.interface.selected_index
#                     ].parts.gametext.color_foreground
#                     if self.parts.color_for_recoloring_gametext is None:
#                         # invert color
#                         gametext_color = pygame.Color(gametext_color)
#                         self.parts.color_for_recoloring_gametext = pygame.Color(
#                             abs(255 - gametext_color.r),
#                             abs(255 - gametext_color.g),
#                             abs(255 - gametext_color.b),
#                         )
#                     self.children[
#                         self.interface.selected_index
#                     ].parts.gametext.color_foreground = (
#                         self.parts.color_for_recoloring_gametext
#                     )
#             case HighlightStyle.CURSOR:
#                 highlight_with_cursor_flag = True
#                 if hasattr(
#                     self.children[self.interface.selected_index].parts, "gametext"
#                 ):
#                     self.children[self.interface.selected_index].parts.gametext.text = (
#                         self.parts.cursor_char
#                         + self.children[
#                             self.interface.selected_index
#                         ].parts.gametext.text
#                     )
#         # ---
#         super().draw(surface_to_blit)
#         # -post-processing for highlight drawing-
#         if recolor_gametext_fg_flag:
#             # process to undo recoloring
#             self.children[
#                 self.interface.selected_index
#             ].parts.gametext.color_foreground = gametext_color
#         if highlight_with_cursor_flag:
#             # process to undo editing gametext's text for show cursor
#             self.children[
#                 self.interface.selected_index
#             ].parts.gametext.text = self.children[
#                 self.interface.selected_index
#             ].parts.gametext.text[
#                 len(self.parts.cursor_char) :
#             ]
#         # ---
