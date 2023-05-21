from typing import Callable, Optional

import pygame

from .gametext import GameText

# from .gameinput import TextInput
from .utils.coordinate import (
    calc_pos_to_center,
    calc_x_to_center,
    calc_y_to_center,
)


class UIProperty:
    pass


class Coordinate(UIProperty):
    def __init__(self):
        super().__init__()
        self._pos: list[int, int] = [0, 0]

    @property
    def pos(self):
        return self._pos


class Size(UIProperty):
    """This class represents the size of the UI element.

    Attributes:
        padding (int):
            The padding of the UI element.
        min_size (list[int, int]):
            The description is included in `calc_min_size`.
        calc_min_size (Callable[..., list[int, int]]):
            min_size, the size of the contents is calculated by this.
            This func is needed to be set for getting it.
        real_size (list[int, int]):
            The description is included in `calc_real_size`.
        calc_real_size (Callable[..., list[int, int]]):
            real_size, the entire size of the ui element (including the border line,
            padding, etc.) is calculated by this.
            This func is needed to be set for getting it.
        fixed_size (Optional[list[int, int]]):
            The size to set the fixed size of the UI element.
            If fixed_size is set, min_size is ignored and fixed_size act as real_size.
    """

    def __init__(self):
        super().__init__()
        self.padding: int = 0
        self.calc_min_size: Callable[..., list[int, int]] = None
        self.calc_real_size: Callable[..., list[int, int]] = None
        self.fixed_size: Optional[list[int, int]] = None

    @property
    def min_size(self) -> list[int, int]:
        if self.calc_min_size is None:
            raise NotImplementedError(
                "Set 'calc_min_size: Callable[..., list[int]] function'"
                + " before getting the value."
            )
        return self.calc_min_size()

    @property
    def real_size(self) -> list[int, int]:
        if self.calc_real_size is None:
            raise NotImplementedError(
                "Set 'calc_real_size: Callable[..., list[int]] function'"
                + " before getting the value."
            )
        real_size = self.calc_real_size()
        if self.fixed_size:
            if self.fixed_size[0]:
                real_size[0] = self.fixed_size[0]
            if self.fixed_size[1]:
                real_size[1] = self.fixed_size[1]
        return real_size


class Rect(Coordinate, Size):
    def __init__(self):
        super().__init__()
        self.frame_width: Optional[int] = None
        self.frame_color = pygame.Color(255, 255, 255)
        self.frame_left_surface: Optional[pygame.surface.Surface] = None
        self.frame_top_surface: Optional[pygame.surface.Surface] = None
        self.frame_right_surface: Optional[pygame.surface.Surface] = None
        self.frame_bottom_surface: Optional[pygame.surface.Surface] = None
        self.frame_topleft_corner_surface: Optional[pygame.surface.Surface] = None
        self.frame_topright_corner_surface: Optional[pygame.surface.Surface] = None
        self.frame_bottomleft_corner_surface: Optional[pygame.surface.Surface] = None
        self.frame_bottomright_corner_surface: Optional[pygame.surface.Surface] = None

    def is_given_x_on_ui(self, x):
        return self.pos[0] <= x <= self.pos[0] + self.real_size[0]

    def is_given_y_on_ui(self, y):
        return self.pos[1] <= y <= self.pos[1] + self.real_size[1]

    def is_givenpos_on_ui(self, pos):
        return self.is_given_x_on_ui(pos[0]) and self.is_given_y_on_ui(pos[1])

    def do_func_if_pos_is_on_ui(self, pos, func: Callable):
        if self.is_givenpos_on_ui(pos):
            return func()

    def set_x_to_center(self):
        self._pos[0] = calc_x_to_center(self.real_size[0])

    def set_y_to_center(self):
        self._pos[1] = calc_y_to_center(self.real_size[1])

    def set_pos_to_center(self):
        self._pos = list(calc_pos_to_center(self.real_size))

    def draw_frame(self, surface_to_blit: pygame.Surface):
        if self.frame_width:
            pygame.draw.rect(
                surface_to_blit,
                self.frame_color,
                (*self.pos, *self.real_size),
                self.frame_width,
            )


class UIElementInterface(Coordinate, Size):
    pass


class UIElement:
    def __init__(self):
        self.s = UIElementInterface()

    def draw(self, surface: pygame.surface.Surface):
        raise NotImplementedError


class GameTextWithPages(UIProperty):
    def __init__(self):
        super().__init__()
        self._pages: list[GameText] = []
        self._current_page_id: int = 0

    @property
    def current_page_id(self) -> int:
        return self._current_page_id

    @property
    def pages(self) -> list[GameText]:
        return self._pages

    def rewrite(self, text: str | GameText, page_id: Optional[int] = None):
        """
        Arguments:
            text (str | GameText):
            page_id (int): this method rewrite current page if page_id is None.
        """
        if page_id is None:
            page_id = self.current_page_id
        if isinstance(text, str):
            if self._pages[page_id].text != text:
                self._pages[page_id].text = text
        elif isinstance(text, GameText):
            if self._pages[page_id] != text:
                self._pages[page_id] = text
        else:
            raise ValueError("argument `text` must be a str")

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def current_page(self):
        return self.pages[self.current_page_id]

    gametext = current_page  # alias

    @property
    def current_page_text(self):
        return self.pages[self.current_page_id].text

    text = current_page_text  # alias

    @pages.setter
    def pages(self, gametexts: GameText | list[GameText]):
        error = ValueError(
            "gametexts must be GameText or list[GameText], " + f"not {type(gametexts)}"
        )
        if isinstance(gametexts, GameText):
            if self.page_count == 0:
                self._pages.append(gametexts)
            else:
                self.rewrite(gametexts)
        elif isinstance(gametexts, list):
            if all([isinstance(gametext, GameText) for gametext in gametexts]):
                self._pages = gametexts
            else:
                raise error
        else:
            try:
                self._pages = list(gametexts)
            except TypeError:
                raise error

    def go_to_page(self, page_id: int):
        if page_id < 0 or page_id >= self.page_count:
            raise ValueError(f"page_id {page_id} out of range")
        self._current_page_id = page_id

    def go_to_nextpage(self):
        self.go_to_page(self.current_page_id + 1)

    def go_back_page(self):
        self.go_to_page(self.current_page_id - 1)

    def append_page(self, gametext: GameText):
        self.pages.append(gametext)

    def tear_up_page(self, page_id: int) -> str:
        return self.pages.pop(page_id)


class LabelInterface(Rect, GameTextWithPages):
    pass


class LabelUI(UIElement):
    def __init__(self, gametexts: GameText | list[GameText]):
        self.s = LabelInterface()  # self.s = LabelUI's
        self.s.calc_min_size = self._calc_min_size
        self.s.calc_real_size = self._calc_real_size
        self.s.pages = gametexts

    def _calc_min_size(self) -> list[int, int]:
        # size = list(self.s.gametext.font.size(self.s.current_page_text))
        linelength = None
        if self.s.fixed_size:
            linelength = self.s.fixed_size[0]
        size = self.s.current_page.font.lines_and_sizes_of_multilinetext(
            self.s.current_page_text, linelength_limit=linelength
        )[1]
        return size

    def _calc_real_size(self) -> list[int, int]:
        return list(
            map(
                lambda w_or_h: w_or_h + self.s.padding * 2 + self.s.frame_width * 2,
                self.s.min_size,
            )
        )

    def draw(self, screen: pygame.Surface):
        text_pos = list(
            map(
                lambda pos: pos + self.s.padding + self.s.frame_width,
                self.s.pos,
            )
        )
        screen.blit(
            self.s.current_page.renderln(linelength=self.s.real_size[0]),
            text_pos,
            (0, 0, *self.s.real_size),
        )


class MsgboxProperty(LabelInterface):
    def __init__(self):
        super().__init__()
        self.frame_width = 1


class MsgboxUI(LabelUI):
    def __init__(self, gametexts: GameText | list[GameText]):
        self.s = MsgboxProperty()
        self.s.calc_min_size = self._calc_min_size
        self.s.calc_real_size = self._calc_real_size
        self.s.pages = gametexts

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        self.s.draw_frame(screen)


class UILayoutInterface(Coordinate):
    def __init__(self):
        super().__init__()
        self.children: list[UIElement] = []


class UILayout(UIElement):
    def __init__(self):
        self.s = UILayoutInterface()

    def draw(self, screen: pygame.surface.Surface):
        for child in self.s.children:
            child.s.pos[0] += self.s.pos[0]
            child.s.pos[1] += self.s.pos[1]
            child.draw(screen)


class UIFlowLayoutInterface(UILayoutInterface):
    def __init__(self):
        super().__init__()
        self.direction = "vertical"  # or "horizontal"


class UIFlowLayout(UILayout):
    def __init__(self):
        self.s = UIFlowLayoutInterface()

    def draw(self, screen: pygame.surface.Surface):
        # TODO: implement this method
        if self.s.direction == "vertical":
            for child in self.s.children:
                child.draw(screen)
        elif self.s.direction == "horizontal":
            for child in self.s.children:
                child.draw(screen)


# class MenuInterface(UIInterface):
#     def __init__(self):
#         super().__init__()
#         self.selected_index = 0
#         self.option_keys: list[str] = []
#         self.option_texts: list[str] = []
#         self.option_actions_on_select: dict[str, Callable] = {}
#         self.option_actions_on_highlight: dict[str, Callable] = {}
#         self.loop_cursor = True
#         self.action_on_cursor_up = lambda: None
#         self.action_on_cursor_down = lambda: None

#     def add_menuitem(
#         self,
#         option_key: str,
#         action_on_select: Callable = lambda: None,
#         action_on_highlight: Callable = lambda: None,
#         text: str = None,
#     ):
#         if text is None:
#             text = option_key
#         self.option_keys.append(option_key)
#         self.option_texts.append(text)
#         self.option_actions_on_select[option_key] = action_on_select
#         self.option_actions_on_highlight[option_key] = action_on_highlight

#     def replace_menuitem_by_index(
#         self,
#         index: int,
#         option_key: str,
#         action_on_select: Callable = lambda: None,
#         action_on_highlight: Callable = lambda: None,
#         text: str = None,
#     ):
#         if text is None:
#             text = option_key
#         self.option_keys[index] = option_key
#         self.option_texts[index] = text
#         del self.option_actions_on_select[
#             tuple(self.option_actions_on_select.keys())[index]
#         ]
#         del self.option_actions_on_highlight[
#             tuple(self.option_actions_on_highlight.keys())[index]
#         ]
#         self.option_actions_on_select[option_key] = action_on_select
#         self.option_actions_on_highlight[option_key] = action_on_highlight

#     def replace_menuitem_by_key(
#         self,
#         option_key: str,
#         new_option_key: str,
#         action_on_select: Callable = lambda: None,
#         action_on_highlight: Callable = lambda: None,
#         text: str = None,
#     ):
#         if text is None:
#             text = new_option_key
#         index = self.option_keys.index(option_key)
#         self.replace_menuitem_by_index(
#             index=index,
#             option_key=new_option_key,
#             action_on_select=action_on_select,
#             action_on_highlight=action_on_highlight,
#             text=text,
#         )

#     def set_action_on_cursor_up(self, action: Callable):
#         self.action_on_cursor_up = action

#     def set_action_on_cursor_down(self, action: Callable):
#         self.action_on_cursor_down = action

#     def cursor_up(self):
#         if 0 < self.selected_index:
#             self.selected_index -= 1
#         elif self.loop_cursor:
#             self.selected_index = self.option_count - 1
#         self.action_on_cursor_up()

#     def cursor_down(self):
#         if self.selected_index < len(self.option_keys) - 1:
#             self.selected_index += 1
#         elif self.loop_cursor:
#             self.selected_index = 0
#         self.action_on_cursor_down()

#     def do_selected_action(self):
#         if len(self.option_keys) == 0:
#             raise AttributeError("At least one menu item is required to take action.")
#         return self.option_actions_on_select[self.option_keys[self.selected_index]]()

#     def do_action_on_highlight(self):
#         """
#         Args:
#             do_once_each_highlighting (bool, optional): WIP
#         """
#         if len(self.option_keys) == 0:
#             raise AttributeError("At least one menu item is required to take action.")
#         return self.option_actions_on_highlight[self.option_keys[self.selected_index]]()

#     def select_action_by_index(self, index):
#         if 0 <= index < len(self.option_keys):
#             self.selected_index = index
#         else:
#             raise ValueError("Given index is out of range in the menu.")

#     @property
#     def option_count(self) -> int:
#         return len(self.option_keys)

#     def longest_optiontext(self) -> str:
#         return max(self.option_texts, key=len)


# class MenuUIProperty(UIRect, UIFontProperty):
#     def __init__(self):
#         super().__init__()
#         self.option_highlight_style: str
#         self.option_highlight_fg_color = (222, 222, 222)
#         self.option_highlight_bg_color = (127, 127, 127)
#         self.cursor_size: list
#         # self.locate_cursor_inside_frame = True
#         self.padding_between_cursor_n_menu = 0

#     def is_givenpos_on_option(self, pos: tuple[int, int], index: int):
#         is_on_y = (
#             self.pos[1] + self.font.get_height() * index
#             <= pos[1]
#             <= self.pos[1] + self.font.get_height() * (index + 1)
#         )
#         return self.is_given_x_on_ui(pos[0]) and is_on_y


# class MenuUI(UIElement):
#     def __init__(
#         self,
#         font: Font2,
#         interface: MenuInterface = MenuInterface(),
#         frameborder_width: int = 1,
#         option_highlight_style: str = "filled-box",
#         cursor_character: str = "▶"
#         # locate_cursor_inside_frame: bool = True,
#     ):
#         super().__init__()
#         self.interface = interface
#         self.property = MenuUIProperty()
#         self.property.font = font
#         self.property.calc_min_size = self._calc_min_size
#         self.property.calc_real_size = self._calc_real_size
#         self.property.frameborder_width = frameborder_width
#         self.property.option_highlight_style = option_highlight_style
#         # self.property.locate_cursor_inside_frame = locate_cursor_inside_frame
#         self.cursor_char = cursor_character
#         self.property.cursor_size = list(self.property.font.size(self.cursor_char))

#     def _calc_min_size(self) -> list[int]:
#         size = list(
#             self.property.font.size(self.interface.longest_optiontext()),
#         )
#         size[1] *= self.interface.option_count
#         return size

#     def _calc_real_size(self) -> list[int]:
#         size = list(
#             map(
#                 lambda w_or_h: w_or_h
#                 + self.property.padding * 2
#                 + self.property.frameborder_width * 2,
#                 self.property.min_size,
#             )
#         )
#         size[0] += self.property.cursor_size[0]
#         return size

#     def highlight_option_on_givenpos(self, pos):
#         for i in range(len(self.interface.option_keys)):
#             if self.property.is_givenpos_on_option(pos, i):
#                 self.interface.select_action_by_index(i)

#     def draw(self, screen: pygame.Surface):
#         self.property.draw_frame(screen)
#         if self.property.option_highlight_style == "filled-box":
#             pygame.draw.rect(
#                 screen,
#                 self.property.option_highlight_bg_color,
#                 (
#                     (
#                         self.property.pos[0]
#                         + self.property.padding
#                         + self.property.frameborder_width,
#                         self.property.pos[1]
#                         + self.property.padding
#                         + self.property.frameborder_width
#                         + self.property.cursor_size[1] * self.interface.selected_index,
#                     ),
#                     (self.property.min_size[0], self.property.cursor_size[1]),
#                 ),
#             )
#         elif self.property.option_highlight_style == "cursor-char":
#             cursor_surface = self.property.font.render(
#                 self.cursor_char, True, self.property.option_highlight_fg_color
#             )
#             screen.blit(
#                 cursor_surface,
#                 (
#                     self.property.frameborder_width
#                     + self.property.padding
#                     + self.property.pos[0],
#                     self.property.frameborder_width
#                     + self.property.padding
#                     + self.property.pos[1]
#                     + self.property.cursor_size[1] * self.interface.selected_index,
#                 ),
#             )
#         for index, menutext in enumerate(self.interface.option_texts):
#             if self.property.option_highlight_style == "cursor-char":
#                 cursor_space_size = self.property.cursor_size
#             else:
#                 cursor_space_size = [0, 0]
#             screen.blit(
#                 self.property.font.render(menutext, True, (255, 255, 255)),
#                 tuple(
#                     map(
#                         sum,
#                         zip(
#                             (
#                                 cursor_space_size[0]
#                                 + self.property.padding_between_cursor_n_menu,
#                                 0,
#                             ),
#                             [self.property.frameborder_width] * 2,
#                             [self.property.padding] * 2,
#                             self.property.pos,
#                             (0, index * self.property.font.get_height()),
#                         ),
#                     )
#                 ),
#             )


# class TextInputProperty(MsgBoxProperty):
#     pass


# class TextInputInterface(TextInput):
#     pass


# class TextInputUI(MsgBoxUI):
#     def __init__(
#         self,
#         font: Font2,
#         interface: TextInputInterface = TextInputInterface(),
#         text_or_textlist: Union[str, list[str]] = "",
#         frameborder_width=1,
#         linelength_in_char: Optional[int] = None,
#         linelength_in_px: Optional[int] = None,
#         use_window_width_as_default_linelength_if_it_is_None=True,
#     ):
#         self.property = TextInputProperty()
#         if use_window_width_as_default_linelength_if_it_is_None and not (
#             linelength_in_char and linelength_in_px
#         ):
#             linelength_in_px = window_size()[0]
#         super().__init__(
#             font=font,
#             text_or_textlist=text_or_textlist,
#             frameborder_width=frameborder_width,
#             linelength_in_char=linelength_in_char,
#             linelength_in_px=linelength_in_px,
#         )
#         self.interface = interface

#     def _calc_column_num_at_linewrap(self):
#         self.interface.column_num_at_line_wrap = (
#             self.property.font.size_of_multiline_text(
#                 self.property.current_page_text,
#                 self.property.linelength_in_px,
#                 getsize_in_charcount=True,
#             )[0]
#         )

#     def draw(self, screen: pygame.Surface):
#         self.property.rewrite_text(self.interface.text)
#         self._calc_column_num_at_linewrap()
#         # print(self.interface.column_num_at_line_wrap)
#         super().draw(screen)
#         caret_start_pos = [
#             self.interface.caret_column_num
#             * self.property.font.halfwidth_charsize()[0],
#             self.interface.caret_line_num * self.property.font.halfwidth_charsize()[1],
#         ]
#         caret_end_pos = [
#             caret_start_pos[0],
#             caret_start_pos[1] + self.property.font.halfwidth_charsize()[1],
#         ]
#         # caret pos on line wrapping
#         if self.interface.column_num_at_line_wrap is not None:
#             if (
#                 self.interface.caret_column_num
#                 > self.interface.column_num_at_line_wrap
#                 > 0
#             ):
#                 fixed_caret_x = (
#                     self.interface.caret_column_num
#                     % self.interface.column_num_at_line_wrap
#                 )
#                 caret_start_pos[0] = (
#                     fixed_caret_x * self.property.font.halfwidth_charsize()[0]
#                 )
#                 caret_end_pos[0] = caret_start_pos[0]
#                 fixed_caret_y = (
#                     self.interface.caret_column_num
#                     // self.interface.column_num_at_line_wrap
#                 )
#                 caret_start_pos[1] = (
#                     fixed_caret_y * self.property.font.halfwidth_charsize()[1]
#                 )
#                 caret_end_pos[1] = (
#                     caret_start_pos[1] + self.property.font.halfwidth_charsize()[1]
#                 )
#                 # print(
#                 #     f"fixed_caret_x: {fixed_caret_x} | fixed_caret_y: {fixed_caret_y}"
#                 #     + " | "
#                 #     + f"column_numatlinewrap {self.interface.column_num_at_line_wrap}"
#                 #     + " | "
#                 #     + f"caret_column_num {self.interface.caret_column_num}"
#                 # )
#         if self.interface.is_active:
#             pygame.draw.line(screen, (255, 255, 255), caret_start_pos, caret_end_pos)
