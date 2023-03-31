from typing import Callable
import pygame

from .gametext import TextSurfaceFactory


class MenuHasNoItemError(Exception):
    pass


class GameMenuSystem:
    def __init__(self):
        self.menu_selected_index = 0
        self.menu_option_keys = []
        self.menu_option_texts = []
        self.option_actions = {}

    def add_menu_item(self, option_key, action: Callable, text: str = None):
        if text is None:
            text = option_key
        self.menu_option_keys.append(option_key)
        self.menu_option_texts.append(text)
        self.option_actions[option_key] = action

    def menu_cursor_up(self):
        if 0 < self.menu_selected_index:
            self.menu_selected_index -= 1

    def menu_cursor_down(self):
        if self.menu_selected_index < len(self.menu_option_keys)-1:
            self.menu_selected_index += 1

    def do_selected_action(self):
        if len(self.menu_option_keys) == 0:
            raise MenuHasNoItemError(
                "At least one menu item is required to take action.")
        return self.option_actions[
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


class GameMenuUI:
    def __init__(self, menu_system: GameMenuSystem,
                 textfactory: TextSurfaceFactory):
        self.system = menu_system
        self.textfactory = textfactory
        self.resize_menu_to_suit()
        self._pos = [0, 0]
        self.frame_color = (255, 255, 255)
        self.cursor_size = textfactory.char_size()
        self.reposition_cursor()

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value
        self.reposition_cursor()

    def reposition_cursor(self):
        self.cursor_pos = [
            self.pos[0]-self.cursor_size[0],
            self.pos[1]]

    def resize_menu_to_suit(self):
        self.size = [
            self.system.max_option_text_length(
            )*self.textfactory.char_size()[0],
            self.system.count_menu_items()*self.textfactory.char_size()[1]]

    def draw(self, screen):
        pygame.draw.rect(
            screen, self.frame_color,
            self.pos + self.size, 1)
        for i, (key, text) in enumerate(
            zip(self.system.menu_option_keys,
                self.system.menu_option_texts)):
            self.textfactory.register_text(
                key, text,
                (self.pos[0],
                 self.pos[1]+self.textfactory.char_size()[1]*i))
        for key in self.system.menu_option_keys:
            self.textfactory.render(key, screen)
        pygame.draw.polygon(
            screen, self.frame_color,
            ((self.cursor_pos[0],
              self.cursor_pos[1]+self.cursor_size[1]
              * self.system.menu_selected_index),
             (self.cursor_pos[0]+self.cursor_size[0],
              (self.cursor_pos[1]+self.cursor_size[1]//2)
              + self.cursor_size[1]*self.system.menu_selected_index),
             (self.cursor_pos[0],
              (self.cursor_pos[1]+self.cursor_size[1])
              + self.cursor_size[1]*self.system.menu_selected_index)))


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
