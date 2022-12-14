from typing import Union
import pygame


class UIElement:
    def __init__(self, image: pygame.surface.Surface = None, ):
        self._container = None
        self._x = 0
        self._y = 0
        if image is None:
            self.image = pygame.surface.Surface((0, 0))
        else:
            self.image = image
        self.rect = self.image.get_rect()
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

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        self.rect.height = self._height

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
    # TODO resize rect to be drawable
    def __init__(self):
        super().__init__()
        self.layout = [[]]

        self.margin_top = 0
        self.margin_bottom = 0
        self.margin_right = 0
        self.margin_left = 0
        self.padding_top = 0
        self.padding_bottom = 0
        self.padding_right = 0
        self.padding_left = 0
        # "left" "right" "top" "bottom"
        self.anchor = "left"

    def set_ui_element(self, ui_element: UIElement, row_index, column_index):
        row_size_min = row_index + 1
        column_size_min = column_index + 1
        if len(self.layout) <= row_size_min:
            # print(row_size_min - len(self.layout))
            for i in range(row_size_min - len(self.layout)):
                self.layout.append([])
            for i in range(len(self.layout)):
                if len(self.layout[i]) <= column_size_min:
                    self.layout[i].extend(
                        [None for j in range(
                            column_size_min - len(self.layout[i]))])
        self.layout[row_index][column_index] = ui_element

    def resize_rect_by_entire_elements(self):
        heights = []
        widths = []
        for row in self.layout:
            # heights
            for column in row:
                if column is None:
                    continue
                heights.append(column.height)
                widths.append(column.width)
        print("h w:", heights, widths)
        self.print_layout()

    def print_layout(self):
        print(*self.layout, sep="\n")

    def draw(self, screen: pygame.surface.Surface):
        for row in self.layout:
            for column in row:
                if column is not None:
                    # need surface size to draw
                    self.image = pygame.surface.Surface((100, 100))
                    self.image.blit(column.image, column.rect)
                    self.rect = self.image.get_rect()
        screen.blit(self.image, self.rect)
        # super().draw(screen)


class UIBoxLayout(UILayout):
    def __init__(self):
        super().__init__()
        self.orientation = "vertical"  # vertical | horizontal


uilayout = UILayout()
uilayout.set_ui_element(UIElement(), 6, 5)
print(uilayout.layout)
