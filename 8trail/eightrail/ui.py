from typing import Union
import pygame


class UIElement:
    def __init__(self):
        self._container = None
        self.width = 0
        self.height = 0
        self._x = 0
        self._y = 0
        self.image = pygame.surface.Surface((self.width, self.height))
        self.rect = pygame.rect.Rect(self._x, self._y, self.width, self.height)

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
    def container(self) -> Union[None, "UILayout"]:
        return self._container

    @container.setter
    def container(self, value: "UILayout"):
        self._container = value

    def update(self, dt):
        pass

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)


class UILayout(UIElement):
    def __init__(self):
        self.layout = [[]]

        self.margin_top = 0
        self.margin_bottom = 0
        self.margin_right = 0
        self.margin_left = 0
        self.padding_top = 0
        self.padding_bottom = 0
        self.padding_right = 0
        self.padding_left = 0

    def set_ui_element(self, ui_element: UIElement, row_index, column_index):
        row_size_min = row_index + 1
        column_size_min = column_index + 1
        if len(self.layout) <= row_size_min:
            print(row_size_min - len(self.layout))
            for i in range(row_size_min - len(self.layout)):
                self.layout.append([])
            for i in range(len(self.layout)):
                if len(self.layout[i]) <= column_size_min:
                    self.layout[i].extend(
                        [None for j in range(
                            column_size_min - len(self.layout[i]))])

        new_width = 0
        new_height = 0
        self.layout[row_index][column_index] = ui_element

    # def draw(self, screen: pygame.surface.Surface):
    #     surface =
        # screen.blit()


uilayout = UILayout()
uilayout.set_ui_element(UIElement(), 6, 5)
print(uilayout.layout)
