from typing import Callable
import abc

import pygame

from .gametext import TextSurfaceFactory
from . import global_
from .utilities import calc_pos_to_center, calc_x_to_center, calc_y_to_center


class MenuHasNoItemError(Exception):
    pass


class GameMenuSystem:
    def __init__(self):
        self.menu_selected_index = 0
        self.menu_option_keys: list[str] = []
        self.menu_option_texts: list[str] = []
        self.option_actions_on_select: dict[str, Callable] = {}
        self.option_actions_on_highlight: dict[str, Callable] = {}
        self.loop_cursor = True
        self.action_on_cursor_up = lambda: None
        self.action_on_cursor_down = lambda: None

    def add_menu_item(
            self, option_key: str,
            action_on_select: Callable = lambda: None,
            action_on_highlight: Callable = lambda: None, text: str = None):
        if text is None:
            text = option_key
        self.menu_option_keys.append(option_key)
        self.menu_option_texts.append(text)
        self.option_actions_on_select[option_key] = action_on_select
        self.option_actions_on_highlight[option_key] = action_on_highlight

    def replace_menu_item_by_index(
            self, index: int, option_key: str,
            action_on_select: Callable = lambda: None,
            action_on_highlight: Callable = lambda: None, text: str = None):
        if text is None:
            text = option_key
        self.menu_option_keys[index] = option_key
        self.menu_option_texts[index] = text
        del self.option_actions_on_select[
            tuple(self.option_actions_on_select.keys())[index]]
        del self.option_actions_on_highlight[
            tuple(self.option_actions_on_highlight.keys())[index]]
        self.option_actions_on_select[option_key] = action_on_select
        self.option_actions_on_highlight[option_key] = action_on_highlight

    def replace_menu_item_by_key(
            self, option_key: str, new_option_key: str,
            action_on_select: Callable = lambda: None,
            action_on_highlight: Callable = lambda: None, text: str = None):
        if text is None:
            text = new_option_key
        index = self.menu_option_keys.index(option_key)
        self.replace_menu_item_by_index(
            index=index,
            option_key=new_option_key,
            action_on_select=action_on_select,
            action_on_highlight=action_on_highlight, text=text)

    def set_action_on_cursor_up(self, action: Callable):
        self.action_on_cursor_up = action

    def set_action_on_cursor_down(self, action: Callable):
        self.action_on_cursor_down = action

    def menu_cursor_up(self):
        if 0 < self.menu_selected_index:
            self.menu_selected_index -= 1
        elif self.loop_cursor:
            self.menu_selected_index = self.count_menu_items() - 1
        self.action_on_cursor_up()

    def menu_cursor_down(self):
        if self.menu_selected_index < len(self.menu_option_keys)-1:
            self.menu_selected_index += 1
        elif self.loop_cursor:
            self.menu_selected_index = 0
        self.action_on_cursor_down()

    def do_selected_action(self):
        if len(self.menu_option_keys) == 0:
            raise MenuHasNoItemError(
                "At least one menu item is required to take action.")
        return self.option_actions_on_select[
            self.menu_option_keys[self.menu_selected_index]]()

    def action_on_highlight(self):
        if len(self.menu_option_keys) == 0:
            raise MenuHasNoItemError(
                "At least one menu item is required to take action.")
        return self.option_actions_on_highlight[
            self.menu_option_keys[self.menu_selected_index]]()

    def select_action_by_index(self, index):
        if 0 <= index < len(self.menu_option_keys):
            self.menu_selected_index = index
        else:
            raise ValueError("Given index is out of range in the menu.")

    def count_menu_items(self) -> int:
        return len(self.menu_option_keys)

    def max_option_text_length(self) -> int:
        return max([len(i) for i in self.menu_option_texts])

    def update(self):
        self.action_on_highlight()


class UIElement(metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwargs):
        self.padding = 0
        # self.enable_mouse = True

    @staticmethod
    def sum_sizes(sizes: tuple[tuple[int, int]]) -> tuple[int, int]:
        return tuple(map(sum, zip(*sizes)))

    @property
    @abc.abstractmethod
    def pos(self) -> list[int, int]:
        """return self._pos"""
        pass

    @pos.setter
    @abc.abstractmethod
    def pos(self, value):
        """self._pos = value"""
        pass

    @property
    @abc.abstractmethod
    def min_size(self) -> list[int, int]:
        """
        self.resize_min_size_to_suit()
        return self.__min_size
        """
        pass

    @abc.abstractmethod
    def resize_min_size_to_suit(self):
        """self.__min_size = [ calc size here ]"""

    @property
    @abc.abstractmethod
    def real_size(self) -> list[int, int]:
        """return calc size here"""


class GameMenuUI(UIElement):
    """
    option_highlight_style = "cursor" or "filled_box"
    "cursor" is default
    anchor(unused) = "top_left" or "center_fixed" or "center"
    "top_left" is default
    """

    def __init__(self, menu_system: GameMenuSystem,
                 textfactory: TextSurfaceFactory,
                 option_highlight_style="cursor", *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("child")
        self.system = menu_system
        self.textfactory = textfactory
        self.resize_min_size_to_suit()
        self._pos = [0, 0]
        self.frame_color = (255, 255, 255)
        self.option_highlight_color = (222, 222, 222)
        self.option_highlight_bg_color = (122, 122, 122)
        self.cursor_size = textfactory.char_size()
        self.reposition_cursor()
        self.option_highlight_style = option_highlight_style
        self.locate_cursor_inside_window = True
        # self.anchor = "top-left"

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value
        self.reposition_cursor()

    @property
    def min_size(self):
        self.resize_min_size_to_suit()
        return self.__min_size

    def resize_min_size_to_suit(self):
        self.__min_size = [
            self.system.max_option_text_length(
            )*self.textfactory.char_size()[0],
            self.system.count_menu_items()*self.textfactory.char_size()[1]]

    @property
    def real_size(self):
        if (self.option_highlight_style == "cursor" and
                self.locate_cursor_inside_window):
            size = [self.min_size[0]+self.padding*3+self.cursor_size[0],
                    self.min_size[1]+self.padding*2]
        else:
            size = [self.min_size[0]+self.padding*2,
                    self.min_size[1]+self.padding*2]
        return size

    def reposition_cursor(self):
        self.cursor_pos = [
            self.pos[0]-self.cursor_size[0],
            self.pos[1]]

    def set_x_to_center(self):
        self.pos[0] = calc_x_to_center(self.real_size[0])
        self.reposition_cursor()

    def set_y_to_center(self):
        self.pos[1] = calc_y_to_center(self.real_size[1])
        self.reposition_cursor()

    def set_pos_to_center(self):
        self.pos = list(calc_pos_to_center(self.real_size))
        self.reposition_cursor()

    def is_given_x_on_ui(self, x):
        return self.pos[0] <= x <= self.pos[0] + self.real_size[0]

    def is_given_y_on_ui(self, y):
        return self.pos[1] <= y <= self.pos[1] + self.real_size[1]

    def is_givenpos_on_ui(self, pos):
        return self.is_given_x_on_ui(pos[0]) and self.is_given_y_on_ui(pos[1])

    def is_givenpos_on_option(self, pos, index):
        is_on_y = \
            self.pos[1] + self.cursor_size[1]*index\
            <= pos[1] <=\
            self.pos[1] + self.cursor_size[1]*(index+1)
        return self.is_given_x_on_ui(pos[0]) and is_on_y

    def do_option_if_givenpos_on_ui(self, pos):
        if self.is_givenpos_on_ui(pos):
            self.system.do_selected_action()

    def highlight_option_on_givenpos(self, pos):
        for i in range(len(self.system.menu_option_keys)):
            if self.is_givenpos_on_option(pos, i):
                self.system.select_action_by_index(i)

    def draw(self, screen):
        pygame.draw.rect(
            screen, self.frame_color,
            self.pos + self.real_size, 1)
        for i, (key, text) in enumerate(
            zip(self.system.menu_option_keys,
                self.system.menu_option_texts)):
            if (self.option_highlight_style == "cursor" and
                    self.locate_cursor_inside_window):
                text_pos = (
                    self.pos[0]+self.padding+self.cursor_size[0]+self.padding,
                    self.pos[1]+self.textfactory.char_size()[1]*i+self.padding)
            else:
                text_pos = (
                    self.pos[0]+self.padding,
                    self.pos[1]+self.textfactory.char_size()[1]*i+self.padding)
            self.textfactory.register_text(
                key, text, text_pos)
        if self.option_highlight_style == "cursor":
            if (self.option_highlight_style == "cursor" and
                    self.locate_cursor_inside_window):
                cursor_polygon_points = ((
                    self.cursor_pos[0]+self.cursor_size[0]+self.padding,
                    self.cursor_pos[1]+self.cursor_size[1]
                    * self.system.menu_selected_index+self.padding),
                    (self.cursor_pos[0]+self.cursor_size[0]*2+self.padding,
                     (self.cursor_pos[1]+self.cursor_size[1]//2)
                     + self.cursor_size[1]*self.system.menu_selected_index
                     + self.padding),
                    (self.cursor_pos[0]+self.cursor_size[0]+self.padding,
                     (self.cursor_pos[1]+self.cursor_size[1])
                     + self.cursor_size[1]*self.system.menu_selected_index
                     + self.padding))
            else:
                cursor_polygon_points = ((
                    self.cursor_pos[0],
                    self.cursor_pos[1]+self.cursor_size[1]
                    * self.system.menu_selected_index+self.padding),
                    (self.cursor_pos[0]+self.cursor_size[0],
                     (self.cursor_pos[1]+self.cursor_size[1]//2)
                     + self.cursor_size[1]*self.system.menu_selected_index
                     + self.padding),
                    (self.cursor_pos[0],
                     (self.cursor_pos[1]+self.cursor_size[1])
                     + self.cursor_size[1]*self.system.menu_selected_index
                     + self.padding))
            pygame.draw.polygon(
                screen, self.option_highlight_color,
                cursor_polygon_points)
        elif self.option_highlight_style == "filled_box":
            pygame.draw.rect(
                screen, self.option_highlight_bg_color,
                ((self.pos[0]+self.padding, self.pos[1]+self.cursor_size[1]
                  * self.system.menu_selected_index+self.padding),
                 (self.min_size[0], self.cursor_size[1])))
            pass
        for key in self.system.menu_option_keys:
            self.textfactory.render(key, screen)


class MsgWindow(UIElement):
    """
    type_of_sizing = "min"(default) or "fixed"
    text_anchor = "left" or "center(default)"
    anchor(unused) = "top_left" or "center_fixed" or "center"
    "top_left" is default
    """

    def __init__(self, font: pygame.font.Font,
                 type_of_sizing="min", text_anchor="center"):
        self.text = ""
        # self.textfactory = textfactory
        self.font = font
        self.resize_min_size_to_suit()
        # self.resize_window_to_suit_text()
        self._pos = [0, 0]
        self.frame_color = (255, 255, 255)
        self.type_of_sizing = type_of_sizing
        self.text_anchor = text_anchor
        self._size = [0, 0]
        self.resize_on_type_of_sizing()
        self.padding = 0

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value

    @property
    def min_size(self):
        self.resize_min_size_to_suit()
        return self.__min_size

    def resize_min_size_to_suit(self):
        self.__min_size = list(self.font.size(self.text))

    @property
    def size(self):
        self.resize_on_type_of_sizing()
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self.resize_on_type_of_sizing()

    def resize_on_type_of_sizing(self):
        if self.type_of_sizing == "fixed":
            if self.min_size[0] > self._size[0]:
                self._size[0] = self.min_size[0]
            if self.min_size[1] > self._size[1]:
                self._size[1] = self.min_size[1]
        elif self.type_of_sizing == "min":
            self._size = self.min_size

    @property
    def real_size(self):
        return self.calc_real_size()

    def calc_real_size(self) -> list[int, int]:
        return list(map(sum, zip(self.size, [self.padding*2, self.padding*2])))

    def rewrite_text(self, text):
        self.text = text

    def set_x_to_center(self):
        self.pos[0] = global_.w_size[0]//2-self.real_size[0]//2

    def set_y_to_center(self):
        self.pos[1] = global_.w_size[1]//2-self.real_size[1]//2

    def set_pos_to_center(self):
        self.set_x_to_center()
        self.set_y_to_center()

    def set_height_by_line_num(self, textline_num):
        """WIP"""
        text_height = self.font.size(self.text)[1]
        self.size[1] = text_height * textline_num

    def draw(self, screen: pygame.surface.Surface):
        frame_rect = self.pos + self.real_size
        pygame.draw.rect(
            screen, self.frame_color,
            frame_rect, 1)
        text_size = self.font.size(self.text)
        if self.text_anchor == "center":
            text_pos = tuple(map(sum, zip(
                map(
                    sum, zip(
                        map(lambda num: num//2, self.real_size),
                        map(lambda num: -num//2, text_size))
                ),
                self.pos)))
        elif self.text_anchor == "left":
            text_pos = tuple(map(sum, zip(
                self.pos, [self.padding, self.padding])))
        print(text_pos)
        screen.blit(self.font.render(
            self.text, True, (255, 255, 255)),
            text_pos)


# class UIElement:
#     def __init__(self, surface: pygame.surface.Surface = None, ):
#         self._container = None
#         self._x = 0
#         self._y = 0
#         if surface is None:
#             self.surface = pygame.surface.Surface((0, 0))
#         else:
#             self.surface = surface
#         self.rect = self.surface.get_rect()
#         self._width = self.rect.width
#         self._height = self.rect.height

#     @property
#     def x(self):
#         return self._x

#     @x.setter
#     def x(self, value):
#         self._x = value
#         self.rect.x = self._x

#     @property
#     def y(self):
#         return self._y

#     @y.setter
#     def y(self, value):
#         self._y = value
#         self.rect.y = self._y

#     @property
#     def width(self):
#         return self._width

#     @width.setter
#     def width(self, value):
#         self._width = value
#         self.rect.width = self._width
#         self.surface = pygame.surface.Surface((self.width, self.height))

#     @property
#     def height(self):
#         return self._height

#     @height.setter
#     def height(self, value):
#         self._height = value
#         self.rect.height = self._height
#         self.surface = pygame.surface.Surface((self.width, self.height))

#     @property
#     def container(self) -> Union[None, "UILayoutBase"]:
#         return self._container

#     @container.setter
#     def container(self, value: "UILayoutBase"):
#         self._container = value

#     def update(self, dt):
#         pass

#     def draw(self, screen: pygame.surface.Surface):
#         screen.blit(self.surface, self.rect)


# class UILayoutBase(UIElement):
#     def __init__(self):
#         super().__init__()
#         self.layout = list[UIElement]()
#         self.margin_top = 0
#         self.margin_bottom = 0
#         self.margin_right = 0
#         self.margin_left = 0
#         self.padding_top = 0
#         self.padding_bottom = 0
#         self.padding_right = 0
#         self.padding_left = 0
#         self.spacing = 0


# class UIBoxLayout(UILayoutBase):
#     def __init__(self):
#         super().__init__()
#         self.orientation = "vertical"  # vertical | horizontal

#     def add_ui_element(self, ui_element: UIElement):
#         self.layout.append(ui_element)

#     def stretch_to_fit_entire(self):
#         if self.orientation == "vertical":
#             height = 0
#             widths = list[int]()
#             for element in self.layout:
#                 height += element.rect.height + self.spacing
#                 widths.append(element.width)
#             self.height = height
#             self.width = max(widths)

#     def draw(self, screen: pygame.surface.Surface):
#         self.stretch_to_fit_entire()
#         if self.orientation == "vertical":
#             i = 0
#             next_y = 0
#             for element in self.layout:
#                 rect = element.rect
#                 if i < 1:
#                     next_y += rect.height + self.spacing
#                 if 1 <= i:
#                     rect.y = next_y
#                     next_y += rect.height
#                 self.surface.blit(element.surface, rect)
#                 i += 1
#         screen.blit(self.surface, self.rect)


# class UIGameText(UIElement):
#     def __init__(self, font: pygame.font.Font, text: str):
#         super().__init__()
#         self.font = font
#         self._text = text
#         self.do_reset_surface_and_rect_when_update_text = True
#         self._update_surface_and_rect_by_new_text()

#     @property
#     def text(self):
#         return self._text

#     @text.setter
#     def text(self, value: str):
#         self._text = value
#         if self.do_reset_surface_and_rect_when_update_text:
#             self._update_surface_and_rect_by_new_text()

#     def _update_surface_and_rect_by_new_text(self):
#         self.surface = self.font.render(self.text, True, (255, 255, 255))
#         self.rect = self.surface.get_rect()

#     def draw(self, screen: pygame.surface.Surface, *args, **kwargs):
#         screen.blit(self.surface, self.rect)

# uilayout = UILayout()
# uilayout.set_ui_element(UIElement(), 6, 5)
# print(uilayout.layout)
