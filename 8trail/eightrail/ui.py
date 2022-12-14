from typing import Union
import pygame

from .gametext import TextSurfaceFactory


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
        self.spacing = 0


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
                height += element.rect.height + self.spacing
                widths.append(element.width)
            self.height = height
            self.width = max(widths)

    def draw(self, screen: pygame.surface.Surface):
        self.stretch_to_fit_entire()
        if self.orientation == "vertical":
            i = 0
            next_y = 0
            for element in self.layout:
                rect = element.rect
                if i < 1:
                    next_y += rect.height + self.spacing
                if 1 <= i:
                    rect.y = next_y
                    next_y += rect.height
                self.surface.blit(element.surface, rect)
                i += 1
        screen.blit(self.surface, self.rect)


class UIGameText(UIElement):
    def __init__(self, font: pygame.font.Font, text: str):
        super().__init__()
        self.font = font
        self._text = text
        self.do_reset_surface_and_rect_when_update_text = True
        self._update_surface_and_rect_by_new_text()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value
        if self.do_reset_surface_and_rect_when_update_text:
            self._update_surface_and_rect_by_new_text()

    def _update_surface_and_rect_by_new_text(self):
        self.surface = self.font.render(self.text, True, (255, 255, 255))
        self.rect = self.surface.get_rect()

    def draw(self, screen: pygame.surface.Surface, *args, **kwargs):
        screen.blit(self.surface, self.rect)

# uilayout = UILayout()
# uilayout.set_ui_element(UIElement(), 6, 5)
# print(uilayout.layout)
