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

    def set_ui_element(self, ui_element: UIElement, row, column):
        # is column prepared
        if len(self.layout) >= column:
            if len(self.layout[0]) >= row:
                pass
        self.layout[column][row] = ui_element
