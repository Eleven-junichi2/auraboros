from typing import Union
import pygame


class UIElement:
    def __init__(self, surface: pygame.surface.Surface = None, ):
        self._container = None
        self._x = 0
        self._y = 0
        if surface is None:
            self.surface = pygame.surface.Surface((0, 0))
        else:
            self.surface = surface
        self.rect = self.surface.get_rect()
        self._width = self.rect.width
        self._height = self.rect.height

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self.rect.x = self._x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self.rect.y = self._y

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self.rect.width = self._width
        self.surface = pygame.surface.Surface((self.width, self.height))

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        self.rect.height = self._height
        self.surface = pygame.surface.Surface((self.width, self.height))

    @property
    def container(self) -> Union[None, "UILayoutBase"]:
        return self._container

    @container.setter
    def container(self, value: "UILayoutBase"):
        self._container = value

    def update(self, dt):
        pass

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.surface, self.rect)


class UILayoutBase(UIElement):
    def __init__(self):
        super().__init__()
        self.layout = list[UIElement]()
        self.margin_top = 0
        self.margin_bottom = 0
        self.margin_right = 0
        self.margin_left = 0
        self.padding_top = 0
        self.padding_bottom = 0
        self.padding_right = 0
        self.padding_left = 0

#     def set_ui_element(self, ui_element: UIElement, row_index, column_index):
#         row_size_min = row_index + 1
#         column_size_min = column_index + 1
#         if len(self.layout) <= row_size_min:
#             # print(row_size_min - len(self.layout))
#             for i in range(row_size_min - len(self.layout)):
#                 self.layout.append([])
#             for i in range(len(self.layout)):
#                 if len(self.layout[i]) <= column_size_min:
#                     self.layout[i].extend(
#                         [None for j in range(
#                             column_size_min - len(self.layout[i]))])
#         self.layout[row_index][column_index] = ui_element

#     def resize_rect_by_entire_elements(self):
#         heights = []
#         widths = []
#         for row in self.layout:
#             # heights
#             for column in row:
#                 if column is None:
#                     continue
#                 heights.append(column.height)
#                 widths.append(column.width)
#         print("h w:", heights, widths)
#         self.print_layout()

#     def print_layout(self):
#         print(*self.layout, sep="\n")

#     def draw(self, screen: pygame.surface.Surface):
#         for row in self.layout:
#             for column in row:
#                 if column is not None:
#                     # need surface size to draw
#                     self.image = pygame.surface.Surface((100, 100))
#                     self.image.blit(column.image, column.rect)
#                     self.rect = self.image.get_rect()
#         screen.blit(self.image, self.rect)
#         # super().draw(screen)


class UIBoxLayout(UILayoutBase):
    def __init__(self):
        super().__init__()
        self.orientation = "vertical"  # vertical | horizontal

    def add_ui_element(self, ui_element: UIElement):
        self.layout.append(ui_element)

    def stretch_to_fit_entire(self):
        if self.orientation == "vertical":
            height = 0
            widths = list[int]()
            for element in self.layout:
                height += element.rect.height
                widths.append(element.width)
            self.height = height
            self.width = max(widths)

    def draw(self, screen: pygame.surface.Surface):
        self.stretch_to_fit_entire()
        if self.orientation == "vertical":
            for element in self.layout:
                self.surface.blit(element.surface, element.rect)
        screen.blit(self.surface, self.rect)


# uilayout = UILayout()
# uilayout.set_ui_element(UIElement(), 6, 5)
# print(uilayout.layout)
