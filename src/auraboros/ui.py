from typing import Callable, Optional, Union

import pygame

from .gametext import Font2
from .utilities import (
    calc_pos_to_center,
    calc_x_to_center,
    calc_y_to_center,
    render_rightpointing_triangle,
)


class UIElement:
    pass


class UIProperty:
    pass


class UICoordinate(UIProperty):
    def __init__(self):
        super().__init__()
        self._pos = [0, 0]

    @property
    def pos(self):
        return self._pos


class UISizing(UIProperty):
    def __init__(self):
        super().__init__()
        self.padding = 0
        self.calc_min_size: Callable[..., list[int]] = None
        self.calc_real_size: Callable[..., list[int]] = None

    @property
    def min_size(self) -> list[int]:
        if self.calc_min_size is None:
            raise NotImplementedError(
                "Set 'calc_min_size: Callable[..., list[int]] function'"
                + " before getting the value."
            )
        return self.calc_min_size()

    @property
    def real_size(self) -> list[int]:
        if self.calc_real_size is None:
            raise NotImplementedError(
                "Set 'calc_real_size: Callable[..., list[int]] function'"
                + " before getting the value."
            )
        return self.calc_real_size()


class UIFontProperty(UIProperty):
    def __init__(self):
        super().__init__()
        self.font: Optional[Font2] = None


class UITextWithPages(UIProperty):
    def __init__(self):
        super().__init__()
        self._texts: list[str] = [""]
        self._current_page_id: int = 0
        self.linelength_in_px: Optional[int] = None  # None means no length limit
        self.linelength_in_char: Optional[int] = None  # None means no length limit

    @property
    def texts(self) -> list[str]:
        return self._texts

    @property
    def page_count(self) -> int:
        return len(self.texts)

    @property
    def current_page_text(self) -> str:
        return self.texts[self.current_page_id]

    @property
    def current_page_id(self) -> int:
        return self._current_page_id

    @texts.setter
    def texts(self, text_or_textlist: Union[str, list[str]]):
        if isinstance(text_or_textlist, str):
            if self.page_count == 0:
                self._texts = [text_or_textlist]
            else:
                self.rewrite_text(text_or_textlist)
        elif isinstance(text_or_textlist, list):
            self._texts = text_or_textlist
        else:
            raise ValueError(
                "text_or_textlist must be str or list[str], "
                + f"not {type(text_or_textlist)}"
            )

    def rewrite_text(self, text: str, page_id: Optional[int] = None):
        """It rewrite current page if page_id is None."""
        if page_id is None:
            page_id = self.current_page_id
        self._texts[page_id] = text

    def go_to_page(self, page_id: int):
        if page_id < 0 or page_id >= self.page_count:
            raise ValueError(f"page_id {page_id} out of range")
        self._current_page_id = page_id

    def go_to_nextpage(self):
        self.go_to_page(self.current_page_id + 1)

    def go_back_page(self):
        self.go_to_page(self.current_page_id - 1)

    def add_page(self, text: str):
        self._texts.append(text)

    def tear_up_page(self, page_id: int) -> str:
        return self._texts.pop(page_id)

    def is_linelength_enable(self):
        for linelength in (self.linelength_in_px, self.linelength_in_char):
            if linelength is not None:
                return True
        else:
            return False


class UIRect(UICoordinate, UISizing):
    def __init__(self):
        super().__init__()
        self.frameborder_width: int = 0
        self.frameborder_color = (255, 255, 255)

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

    def draw_frame(self, surface: pygame.Surface):
        pygame.draw.rect(
            surface,
            self.frameborder_color,
            self.pos + self.real_size,
            self.frameborder_width,
        )


class MsgBoxProperty(UITextWithPages, UIRect, UIFontProperty):
    pass


class MsgBoxUI(UIElement):
    def __init__(
        self,
        font: Font2,
        text_or_textlist: Union[str, list[str]] = "",
        frameborder_width=1,
    ):
        super().__init__()
        self.property = MsgBoxProperty()
        self.property.font = font
        self.property.texts = text_or_textlist
        self.property.calc_min_size = self._calc_min_size
        self.property.calc_real_size = self._calc_real_size
        self.property.frameborder_width = frameborder_width

    def _calc_min_size(self) -> list[int]:
        if self.property.is_linelength_enable():
            size = list(
                self.property.font.size_of_multiline_text(
                    self.property.current_page_text,
                    linelength_limit_in_px=self.property.linelength_in_px,
                    linelength_limit_in_char=self.property.linelength_in_char,
                )
            )
        else:
            size = list(self.property.font.size(self.property.current_page_text))
        return size

    def _calc_real_size(self) -> list[int]:
        return list(
            map(
                lambda w_or_h: w_or_h
                + self.property.padding * 2
                + self.property.frameborder_width * 2,
                self.property.min_size,
            )
        )

    def draw(self, screen: pygame.Surface):
        self.property.draw_frame(screen)
        text_pos = list(
            map(
                lambda pos: pos
                + self.property.padding
                + self.property.frameborder_width,
                self.property.pos,
            )
        )
        if self.property.is_linelength_enable():
            screen.blit(
                self.property.font.renderln(
                    self.property.current_page_text,
                    True,
                    (255, 255, 255),
                    linelength_in_charcount=self.property.linelength_in_char,
                    linelength_in_px=self.property.linelength_in_px,
                ),
                text_pos,
            )
        else:
            screen.blit(
                self.property.font.render(
                    self.property.current_page_text, True, (255, 255, 255)
                ),
                text_pos,
            )


class MenuInterface:
    def __init__(self):
        self.selected_index = 0
        self.option_keys: list[str] = []
        self.option_texts: list[str] = []
        self.option_actions_on_select: dict[str, Callable] = {}
        self.option_actions_on_highlight: dict[str, Callable] = {}
        self.loop_cursor = True
        self.action_on_cursor_up = lambda: None
        self.action_on_cursor_down = lambda: None

    def add_menuitem(
        self,
        option_key: str,
        action_on_select: Callable = lambda: None,
        action_on_highlight: Callable = lambda: None,
        text: str = None,
    ):
        if text is None:
            text = option_key
        self.option_keys.append(option_key)
        self.option_texts.append(text)
        self.option_actions_on_select[option_key] = action_on_select
        self.option_actions_on_highlight[option_key] = action_on_highlight

    def replace_menuitem_by_index(
        self,
        index: int,
        option_key: str,
        action_on_select: Callable = lambda: None,
        action_on_highlight: Callable = lambda: None,
        text: str = None,
    ):
        if text is None:
            text = option_key
        self.option_keys[index] = option_key
        self.option_texts[index] = text
        del self.option_actions_on_select[
            tuple(self.option_actions_on_select.keys())[index]
        ]
        del self.option_actions_on_highlight[
            tuple(self.option_actions_on_highlight.keys())[index]
        ]
        self.option_actions_on_select[option_key] = action_on_select
        self.option_actions_on_highlight[option_key] = action_on_highlight

    def replace_menuitem_by_key(
        self,
        option_key: str,
        new_option_key: str,
        action_on_select: Callable = lambda: None,
        action_on_highlight: Callable = lambda: None,
        text: str = None,
    ):
        if text is None:
            text = new_option_key
        index = self.option_keys.index(option_key)
        self.replace_menuitem_by_index(
            index=index,
            option_key=new_option_key,
            action_on_select=action_on_select,
            action_on_highlight=action_on_highlight,
            text=text,
        )

    def set_action_on_cursor_up(self, action: Callable):
        self.action_on_cursor_up = action

    def set_action_on_cursor_down(self, action: Callable):
        self.action_on_cursor_down = action

    def cursor_up(self):
        if 0 < self.selected_index:
            self.selected_index -= 1
        elif self.loop_cursor:
            self.selected_index = self.option_count - 1
        self.action_on_cursor_up()

    def cursor_down(self):
        if self.selected_index < len(self.option_keys) - 1:
            self.selected_index += 1
        elif self.loop_cursor:
            self.selected_index = 0
        self.action_on_cursor_down()

    def do_selected_action(self):
        if len(self.option_keys) == 0:
            raise AttributeError("At least one menu item is required to take action.")
        return self.option_actions_on_select[self.option_keys[self.selected_index]]()

    def do_action_on_highlight(self, do_once_each_highlighting: bool = False):
        """
        Args:
            do_once_each_highlighting (bool, optional): WIP
        """
        if len(self.option_keys) == 0:
            raise AttributeError("At least one menu item is required to take action.")
        return self.option_actions_on_highlight[self.option_keys[self.selected_index]]()

    def select_action_by_index(self, index):
        if 0 <= index < len(self.option_keys):
            self.selected_index = index
        else:
            raise ValueError("Given index is out of range in the menu.")

    @property
    def option_count(self) -> int:
        return len(self.option_keys)

    def longest_optiontext(self) -> str:
        return max(self.option_texts, key=len)


class MenuUIProperty(UIRect, UIFontProperty):
    def __init__(self):
        super().__init__()
        self.option_highlight_style: str
        self.option_highlight_fg_color = (222, 222, 222)
        self.option_highlight_bg_color = (127, 127, 127)
        self.cursor_size: int
        self.locate_cursor_inside_frame = True
        self.padding_between_cursor_n_menu = 0

    def is_givenpos_on_option(self, pos: tuple[int, int], index: int):
        is_on_y = (
            self.pos[1] + self.font.get_height() * index
            <= pos[1]
            <= self.pos[1] + self.font.get_height() * (index + 1)
        )
        return self.is_given_x_on_ui(pos[0]) and is_on_y


class MenuUI(UIElement):
    def __init__(
        self,
        font: Font2,
        interface: MenuInterface = MenuInterface(),
        frameborder_width: int = 1,
        option_highlight_style: str = "filled-box",
        locate_cursor_inside_frame: bool = True,
    ):
        super().__init__()
        self.interface = interface
        self.property = MenuUIProperty()
        self.property.font = font
        self.property.calc_min_size = self._calc_min_size
        self.property.calc_real_size = self._calc_real_size
        self.property.frameborder_width = frameborder_width
        self.property.option_highlight_style = option_highlight_style
        self.property.locate_cursor_inside_frame = locate_cursor_inside_frame
        self.property.cursor_size = self.property.font.get_height()

    def _calc_min_size(self) -> list[int]:
        size = list(
            self.property.font.size(self.interface.longest_optiontext()),
        )
        size[1] *= self.interface.option_count
        return size

    def _calc_real_size(self) -> list[int]:
        size = list(
            map(
                lambda w_or_h: w_or_h
                + self.property.padding * 2
                + self.property.frameborder_width * 2,
                self.property.min_size,
            )
        )
        size[0] += self.property.cursor_size
        return size

    def highlight_option_on_givenpos(self, pos):
        for i in range(len(self.interface.option_keys)):
            if self.property.is_givenpos_on_option(pos, i):
                self.interface.select_action_by_index(i)

    def draw(self, screen: pygame.Surface):
        self.property.draw_frame(screen)
        if self.property.option_highlight_style == "filled-box":
            pygame.draw.rect(
                screen,
                self.property.option_highlight_bg_color,
                (
                    (
                        self.property.pos[0]
                        + self.property.padding
                        + self.property.frameborder_width,
                        self.property.pos[1]
                        + self.property.padding
                        + self.property.frameborder_width
                        + self.property.font.get_height()
                        * self.interface.selected_index,
                    ),
                    (self.property.min_size[0], self.property.font.get_height()),
                ),
            )
        elif self.property.option_highlight_style == "cursor":
            if self.property.locate_cursor_inside_frame:
                cursor_surface = render_rightpointing_triangle(
                    self.property.cursor_size, self.property.option_highlight_fg_color
                )
                cursor_surface.set_colorkey((0, 0, 0))
                screen.blit(
                    cursor_surface,
                    (
                        self.property.pos[0] + self.property.cursor_size // 4,
                        self.property.pos[1]
                        + self.property.cursor_size * self.interface.selected_index,
                    ),
                )
            else:
                pass
        for index, menutext in enumerate(self.interface.option_texts):
            if self.property.option_highlight_style == "cursor":
                cursor_space_size = self.property.cursor_size
            else:
                cursor_space_size = 0
            screen.blit(
                self.property.font.render(menutext, True, (255, 255, 255)),
                tuple(
                    map(
                        sum,
                        zip(
                            (
                                cursor_space_size
                                + self.property.padding_between_cursor_n_menu,
                                0,
                            ),
                            [self.property.frameborder_width] * 2,
                            [self.property.padding] * 2,
                            self.property.pos,
                            (0, index * self.property.font.get_height()),
                        ),
                    )
                ),
            )


# class UIElementBase(metaclass=abc.ABCMeta):
#     def __init__(self):
#         self.padding = 0
#         self._pos = [0, 0]
#         self._min_size = [0, 0]

#     @staticmethod
#     def sum_sizes(sizes: tuple[tuple[int, int]]) -> tuple[int, int]:
#         return tuple(map(sum, zip(*sizes)))

#     @property
#     def pos(self) -> list[int, int]:
#         """return self._pos"""
#         return self._pos

#     @pos.setter
#     def pos(self, value):
#         """self._pos = value"""
#         self._pos = value

#     @property
#     def min_size(self) -> list[int, int]:
#         self.resize_min_size_to_suit()
#         return self._min_size

#     @abc.abstractmethod
#     def resize_min_size_to_suit(self):
#         """self._min_size = [ calc size here ]"""

#     @property
#     @abc.abstractmethod
#     def real_size(self) -> list[int, int]:
#         """return calc size here"""

#     def set_x_to_center(self):
#         self.pos[0] = calc_x_to_center(self.real_size[0])

#     def set_y_to_center(self):
#         self.pos[1] = calc_y_to_center(self.real_size[1])

#     def set_pos_to_center(self):
#         self.pos = list(calc_pos_to_center(self.real_size))

#     def is_given_x_on_ui(self, x):
#         return self.pos[0] <= x <= self.pos[0] + self.real_size[0]

#     def is_given_y_on_ui(self, y):
#         return self.pos[1] <= y <= self.pos[1] + self.real_size[1]

#     def is_givenpos_on_ui(self, pos):
#         return self.is_given_x_on_ui(pos[0]) and self.is_given_y_on_ui(pos[1])

#     def do_func_if_pos_is_on_ui(self, pos, func: Callable):
#         if self.is_givenpos_on_ui(pos):
#             return func()


# class GameMenuUI(UIElementBase):
#     """
#     option_highlight_style = "cursor" or "filled_box"
#     "cursor" is default
#     anchor(WIP) = "top_left" or "center_fixed" or "center"
#     "top_left" is default
#     """

#     def __init__(
#         self,
#         menu_system: GameMenuSystem,
#         font: Font2,
#         option_highlight_style="cursor",
#     ):
#         super().__init__()
#         self.system = menu_system
#         self.font = font
#         self.resize_min_size_to_suit()
#         self._pos = [0, 0]
#         self.frame_color = (255, 255, 255)
#         self.option_highlight_color = (222, 222, 222)
#         self.option_highlight_bg_color = (122, 122, 122)
#         self.cursor_size = font.size(" ")
#         self.reposition_cursor()
#         self.option_highlight_style = option_highlight_style
#         self.locate_cursor_inside_window = True
#         # self.anchor = "top-left"

#     @property
#     def pos(self):
#         return super().pos

#     @pos.setter
#     def pos(self, value):
#         self._pos = value
#         self.reposition_cursor()

#     def resize_min_size_to_suit(self):
#         self._min_size = [
#             self.system.max_option_text_length() * self.font.size(" ")[0],
#             self.system.count_menu_items() * self.font.size(" ")[1],
#         ]

#     @property
#     def real_size(self):
#         if self.option_highlight_style == "cursor" and \
#               self.locate_cursor_inside_window:
#             size = [
#                 self.min_size[0] + self.padding * 3 + self.cursor_size[0],
#                 self.min_size[1] + self.padding * 2,
#             ]
#         else:
#             size = [
#                 self.min_size[0] + self.padding * 2,
#                 self.min_size[1] + self.padding * 2,
#             ]
#         return size

#     def reposition_cursor(self):
#         self.cursor_pos = [self.pos[0] - self.cursor_size[0], self.pos[1]]

#     def set_x_to_center(self):
#         super().set_x_to_center()
#         self.reposition_cursor()

#     def set_y_to_center(self):
#         super().set_y_to_center()
#         self.reposition_cursor()

#     def set_pos_to_center(self):
#         super().set_pos_to_center()
#         self.reposition_cursor()

#     def is_given_x_on_ui(self, x):
#         return self.pos[0] <= x <= self.pos[0] + self.real_size[0]

#     def is_given_y_on_ui(self, y):
#         return self.pos[1] <= y <= self.pos[1] + self.real_size[1]

#     def is_givenpos_on_ui(self, pos):
#         return self.is_given_x_on_ui(pos[0]) and self.is_given_y_on_ui(pos[1])

#     def is_givenpos_on_option(self, pos, index):
#         is_on_y = (
#             self.pos[1] + self.cursor_size[1] * index
#             <= pos[1]
#             <= self.pos[1] + self.cursor_size[1] * (index + 1)
#         )
#         return self.is_given_x_on_ui(pos[0]) and is_on_y

#     def do_option_if_givenpos_on_ui(self, pos):
#         if self.is_givenpos_on_ui(pos):
#             self.system.do_selected_action()

#     def highlight_option_on_givenpos(self, pos):
#         for i in range(len(self.system.menu_option_keys)):
#             if self.is_givenpos_on_option(pos, i):
#                 self.system.select_action_by_index(i)

#     def draw(self, screen: pygame.surface.Surface):
#         pygame.draw.rect(screen, self.frame_color, self.pos + self.real_size, 1)
#         if self.option_highlight_style == "cursor":
#             if (
#                 self.option_highlight_style == "cursor"
#                 and self.locate_cursor_inside_window
#             ):
#                 cursor_polygon_points = (
#                     (
#                         self.cursor_pos[0] + self.cursor_size[0] + self.padding,
#                         self.cursor_pos[1]
#                         + self.cursor_size[1] * self.system.menu_selected_index
#                         + self.padding,
#                     ),
#                     (
#                         self.cursor_pos[0] + self.cursor_size[0] * 2 + self.padding,
#                         (self.cursor_pos[1] + self.cursor_size[1] // 2)
#                         + self.cursor_size[1] * self.system.menu_selected_index
#                         + self.padding,
#                     ),
#                     (
#                         self.cursor_pos[0] + self.cursor_size[0] + self.padding,
#                         (self.cursor_pos[1] + self.cursor_size[1])
#                         + self.cursor_size[1] * self.system.menu_selected_index
#                         + self.padding,
#                     ),
#                 )
#             else:
#                 cursor_polygon_points = (
#                     (
#                         self.cursor_pos[0],
#                         self.cursor_pos[1]
#                         + self.cursor_size[1] * self.system.menu_selected_index
#                         + self.padding,
#                     ),
#                     (
#                         self.cursor_pos[0] + self.cursor_size[0],
#                         (self.cursor_pos[1] + self.cursor_size[1] // 2)
#                         + self.cursor_size[1] * self.system.menu_selected_index
#                         + self.padding,
#                     ),
#                     (
#                         self.cursor_pos[0],
#                         (self.cursor_pos[1] + self.cursor_size[1])
#                         + self.cursor_size[1] * self.system.menu_selected_index
#                         + self.padding,
#                     ),
#                 )
#             pygame.draw.polygon(
#                 screen, self.option_highlight_color, cursor_polygon_points
#             )
#         elif self.option_highlight_style == "filled_box":
#             pygame.draw.rect(
#                 screen,
#                 self.option_highlight_bg_color,
#                 (
#                     (
#                         self.pos[0] + self.padding,
#                         self.pos[1]
#                         + self.cursor_size[1] * self.system.menu_selected_index
#                         + self.padding,
#                     ),
#                     (self.min_size[0], self.cursor_size[1]),
#                 ),
#             )
#             pass
#             # self.textfactory.render(key, screen)
#         for i, text in enumerate(self.system.menu_option_texts):
#             if (
#                 self.option_highlight_style == "cursor"
#                 and self.locate_cursor_inside_window
#             ):
#                 text_pos = (
#                     self.pos[0] + self.padding + self.cursor_size[0] + self.padding,
#                     self.pos[1] + self.font.size(" ")[1] * i + self.padding,
#                 )
#             else:
#                 text_pos = (
#                     self.pos[0] + self.padding,
#                     self.pos[1] + self.font.size(" ")[1] * i + self.padding,
#                 )
#             screen.blit(self.font.render(text, True, (255, 255, 255)), text_pos)


# class MsgWindow(UIElementBase):
#     """
#     Attributes:
#         text (str): text of current showing
#         ...
#     """

#     def __init__(
#         self,
#         font: Font2,
#         text_or_textlist: Union[str, list[str]] = "",
#         singleline_length: Optional[int] = None,
#         sizing_style="min",
#         text_anchor="center",
#         frame_width=1,
#     ):
#         """
#         Args:
#             font: (Font2):
#             singleline_length (:obj:`int`, optional):
#             sizing_style (str): "min"(default) or "fixed_if_larger_than_min"
#             text_anchor (str):= "left" or "center(default)"
#             anchor(unused) = "top_left(default)" or "center_fixed" or "center"
#         """
#         super().__init__()
#         self.id_current_text = 0
#         self._texts: list[str] = []
#         if isinstance(text_or_textlist, str):
#             self._texts.append(text_or_textlist)
#         elif isinstance(text_or_textlist, list):
#             self._texts = text_or_textlist
#         self.font = font
#         self.resize_min_size_to_suit()
#         self._pos = [0, 0]
#         self.frame_color = (255, 255, 255)
#         self.__sizing_styles: dict = {
#             "min": self.__resize_on_min_style,
#             "fixed_if_larger_than_min": self.__resize_on_fixed_if_larger_min_style,
#         }
#         if sizing_style in self.__sizing_styles.keys():
#             self.sizing_style = sizing_style
#         else:
#             raise ValueError("given sizing_style is invalid")
#         self.text_anchor = text_anchor
#         self._size = [0, 0]
#         self._fixed_size = [0, 0]
#         self.resize_on_sizing_style()
#         self.padding = 0
#         self.frame_width = frame_width
#         self._singleline_length: int = None
#         self.update_singleline_length(singleline_length)

#     def update_singleline_length(self, singleline_length: Optional[int] = None):
#         MAX_SINGLELINE_LENGTH = self.font.textwidth_by_px_into_charcount(
#             global_.w_size[0]
#         )
#         if singleline_length:
#             if singleline_length >= MAX_SINGLELINE_LENGTH:
#                 self._singleline_length = MAX_SINGLELINE_LENGTH
#             else:
#                 self._singleline_length = singleline_length

#     @property
#     def singleline_length(self):
#         return self._singleline_length

#     @singleline_length.setter
#     def singleline_length(self, value: Optional[int] = None):
#         self.update_singleline_length(value)

#     @property
#     def texts(self) -> list:
#         return self._texts

#     @property
#     def text(self) -> str:
#         return self.texts[self.id_current_text]

#     @text.setter
#     def text(self, value: str):
#         self.update_singleline_length()
#         self._texts[self.id_current_text] = value

#     def resize_min_size_to_suit(self):
#         if hasattr(self, "_singleline_length"):
#             if self.singleline_length:
#                 self._min_size = [
#                     self.font.textwidth_by_charcount_into_px(self.singleline_length),
#                     line_count_of_multiline_text(self.text, self.singleline_length)
#                     * self.font.get_linesize(),
#                 ]
#             else:
#                 self._min_size = self.font.size(self.text)
#         else:
#             self._min_size = [0, 0]

#     @property
#     def size(self):
#         self.resize_on_sizing_style()
#         return self._size

#     @property
#     def fixed_size(self):
#         return self._fixed_size

#     @fixed_size.setter
#     def fixed_size(self, value):
#         self._fixed_size = value
#         self.resize_on_sizing_style()

#     def resize_on_sizing_style(self):
#         self.__sizing_styles[self.sizing_style]()

#     def __resize_on_fixed_if_larger_min_style(self):
#         if self.min_size[0] > self.fixed_size[0]:
#             self._size[0] = self.min_size[0]
#         else:
#             self._size[0] = self._fixed_size[0]
#         if self.min_size[1] > self.fixed_size[1]:
#             self._size[1] = self.min_size[1]
#         else:
#             self._size[1] = self._fixed_size[1]

#     def __resize_on_min_style(self):
#         self._size = self.min_size

#     @property
#     def real_size(self):
#         return list(map(sum, zip(self.size, [self.padding * 2, self.padding * 2])))

#     def rewrite_text(self, text: str, id: Union[int, None] = None):
#         if id:
#             self._texts[id] = text
#         else:
#             self.text = text

#     def set_current_text_by_id(self, id: int):
#         self.id_current_text = id

#     def change_text_to_next(self, loop_text_list=False):
#         if self.id_current_text < len(self.texts) - 1:
#             self.id_current_text += 1
#         else:
#             if loop_text_list:
#                 self.id_current_text = 0

#     def rewind_text(self, loop_text_list=False):
#         if self.id_current_text > 0:
#             self.id_current_text -= 1
#         else:
#             if loop_text_list:
#                 self.id_current_text = len(self.texts) - 1

#     def set_x_to_center(self):
#         self.pos[0] = global_.w_size[0] // 2 - self.real_size[0] // 2

#     def set_y_to_center(self):
#         self.pos[1] = global_.w_size[1] // 2 - self.real_size[1] // 2

#     def set_pos_to_center(self):
#         self.set_x_to_center()
#         self.set_y_to_center()

#     def draw(self, screen: pygame.surface.Surface):
#         frame_rect = self.pos + self.real_size
#         pygame.draw.rect(screen, self.frame_color, frame_rect, self.frame_width)
#         if self.singleline_length:
#             text_size = (
#                 self.font.textwidth_by_charcount_into_px(self.singleline_length),
#                 line_count_of_multiline_text(self.text, self.singleline_length)
#                 * self.font.get_linesize(),
#             )
#         else:
#             text_size = self.font.size(self.text)
#         if self.text_anchor == "center":
#             text_pos = tuple(
#                 map(
#                     sum,
#                     zip(
#                         map(
#                             sum,
#                             zip(
#                                 map(lambda num: num // 2, self.real_size),
#                                 map(lambda num: -num // 2, text_size),
#                             ),
#                         ),
#                         self.pos,
#                     ),
#                 )
#             )
#         elif self.text_anchor == "left":
#             text_pos = tuple(map(sum, zip(self.pos, [self.padding, self.padding])))
#         if self.singleline_length:
#             text_surface = self.font.renderln(
#                 self.text,
#                 True,
#                 (255, 255, 255),
#                 line_width_by_char_count=self.singleline_length,
#             )
#         else:
#             text_surface = self.font.render(self.text, True, (255, 255, 255))
#         screen.blit(text_surface, text_pos)


# class StopwatchUI(UIElementBase):
#     def __init__(self):
#         pass

#     def resize_min_size_to_suit(self):
#         pass
#         """self._min_size = [ calc size here ]"""

#     @property
#     def real_size(self) -> list[int, int]:
#         """return calc size here"""
#         pass

#     def draw(self, screen: pygame.surface.Surface):
#         pass


# class TextInputUI(UIElementBase):
#     def __init__(
#         self,
#         font: Font2,
#         textinput: TextInput,
#         singleline_length: Optional[int] = None,
#         cursor_style="i-beam",
#     ):
#         """
#         Args:
#             font (Font2):
#             textinput (TextInput):
#             cursor_style (str):
#                 "i-beam" or "underline", "block". "i-beam" is default.
#         """
#         super().__init__()
#         self.font = font
#         self.textinput_system = textinput
#         self.cursor_style = cursor_style  # or box, underline
#         self._singleline_length: int = None
#         self.update_singleline_length(singleline_length)

#     def update_singleline_length(self, singleline_length: Optional[int] = None):
#         MAX_SINGLELINE_LENGTH = self.font.textwidth_by_px_into_charcount(
#             global_.w_size[0]
#         )
#         if singleline_length:
#             if singleline_length >= MAX_SINGLELINE_LENGTH:
#                 self._singleline_length = MAX_SINGLELINE_LENGTH
#             else:
#                 self._singleline_length = singleline_length

#     @property
#     def singleline_length(self):
#         return self._singleline_length

#     @singleline_length.setter
#     def singleline_length(self, value: Optional[int] = None):
#         self.update_singleline_length(value)

#     def resize_min_size_to_suit(self):
#         """self._min_size = [ calc size here ]"""
#         if hasattr(self, "_singleline_length"):
#             if self.singleline_length:
#                 self._min_size = [
#                     self.font.size(self.textinput_system.text)[0],
#                     line_count_of_multiline_text(
#                         self.textinput_system.text, self.singleline_length
#                     )
#                     * self.font.get_linesize(),
#                 ]
#             else:
#                 self._min_size = self.font.size(self.textinput_system.text)
#         else:
#             self._min_size = [0, 0]

#     @property
#     def real_size(self) -> list[int, int]:
#         """return calc size here"""
#         return list(
#             map(
#                 lambda w_or_h: w_or_h + self.padding * 2,
#                 self.min_size,
#             )
#         )

#     def draw(self, screen: pygame.surface.Surface):
#         screen.blit(
#             self.font.renderln(
#                 self.textinput_system.text,
#                 True,
#                 (255, 255, 255),
#                 line_width_by_px=self.min_size[0],
#             ),
#             self.pos,
#         )
#         if self.cursor_style == "i-beam":
#             cursor_char = "|"
#         elif self.cursor_style == "underline":
#             cursor_char = "_"
#         elif self.cursor_style == "block":
#             cursor_char = "█"
#         print(self.min_size)
#         screen.blit(
#             self.font.render(
#                 cursor_char,
#                 True,
#                 (255, 255, 255),
#             ),
#             self.min_size,
#         )
