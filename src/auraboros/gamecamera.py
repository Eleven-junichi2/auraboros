import pygame


class TopDownCamera:
    def __init__(self):
        self._offset_x = 0
        self._offset_y = 0
        self.scroll_speed = {"left": 1, "up": 1, "right": 1, "down": 1}
        self.scroll_accel = 1
        self.scroll_speed_max = 24

    @property
    def offset_x(self):
        return self._offset_x

    @offset_x.setter
    def offset_x(self, value: int):
        self._offset_x = value

    @property
    def offset_y(self):
        return self._offset_y

    @offset_y.setter
    def offset_y(self, value: int):
        self._offset_y = value

    @property
    def offset(self) -> tuple[int, int]:
        return (self.offset_x, self.offset_y)

    @offset.setter
    def offset(self, value):
        self.offset_x, self.offset_y = value[0], value[1]

    def go_up_camera(self):
        self.offset_y -= self.scroll_speed["up"]
        if self.scroll_speed["up"] < self.scroll_speed_max:
            self.scroll_speed["up"] += self.scroll_accel

    def go_down_camera(self):
        self.offset_y += self.scroll_speed["down"]
        if self.scroll_speed["down"] < self.scroll_speed_max:
            self.scroll_speed["down"] += self.scroll_accel

    def go_right_camera(self):
        self.offset_x += self.scroll_speed["right"]
        if self.scroll_speed["right"] < self.scroll_speed_max:
            self.scroll_speed["right"] += self.scroll_accel

    def go_left_camera(self):
        self.offset_x -= self.scroll_speed["left"]
        if self.scroll_speed["left"] < self.scroll_speed_max:
            self.scroll_speed["left"] += self.scroll_accel

    def projection_on_screen(
            self, screen: pygame.Surface,
            surface_to_projection: pygame.Surface,
            window_size):
        screen.blit(surface_to_projection, (0, 0),
                    (self.offset_x, self.offset_y,
                     window_size[0], window_size[1]))
