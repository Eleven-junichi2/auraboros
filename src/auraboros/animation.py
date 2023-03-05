from inspect import isclass
from typing import Any, MutableMapping

import pygame

from .schedule import schedule_instance_method_interval


class AnimationImage:
    def __init__(self):
        self._anim_frames: list[pygame.surface.Surface] = [
            pygame.surface.Surface((0, 0)), ]
        self.anim_frame_id = 0
        self.anim_interval = 1
        self.loop_count = -1  # -1 means unset loop count
        self.is_playing = False
        self.is_loop = True
        self.image = self.anim_frames[self.anim_frame_id]
        self.was_played_once = False  # to notify for garbage collection
        self.is_finished = False
        self._frame_num = len(self.anim_frames)
        self._do_reset_anim_interval_counter = False
        self._loop_counter = 0

    @property
    def anim_frames(self):
        return self._anim_frames

    @anim_frames.setter
    def anim_frames(self, value):
        self._anim_frames = value
        self.image = self.anim_frames[self.anim_frame_id]

    @property
    def frame_num(self):
        return len(self.anim_frames)

    def draw_while_playing(self, screen: pygame.surface.Surface):
        if self.is_playing:
            screen.blit(self.image, self.rect)

    @schedule_instance_method_interval(
        "anim_interval",
    )
    def update_frame_at_interval(self):
        self.update_frame()

    def update_frame(self):
        if self.loop_count > 0:
            if self._loop_counter > self.loop_count and self.was_played_once:
                return
        if self.is_playing:
            if self.anim_frame_id < len(self.anim_frames):
                self.image = self.anim_frames[self.anim_frame_id]
                self.anim_frame_id += 1
            if self.anim_frame_id == len(self.anim_frames):
                if self.is_loop:
                    self.reset_animation()
                    self._loop_counter += 1
                    self.is_finished = True
                self.was_played_once = True

    def set_current_frame_to_image(self):
        self.image = self.anim_frames[self.anim_frame_id]

    def set_current_frame_id(self, id: int):
        self.anim_frame_id = id

    def let_play_animation(self):
        """Active update and draw function"""
        self.is_playing = True
        self.is_finished = False
        self.reset_animation()

    def let_continue_animation(self):
        """Active update and draw function without reset animation"""
        self.is_playing = True

    def let_stop_animation(self):
        self.is_playing = False

    def reset_animation(self):
        self.anim_frame_id = 0
        self._anim_frame_progress = 0
        self._loop_counter = 0
        self._do_reset_anim_interval_counter = True

    def draw(self, screen):
        self.draw_while_playing(screen)

    def update(self, dt):
        self.update_frame_at_interval()


class AnimationFactory(MutableMapping):
    """
    Examples:
        class ExampleAnimation(AnimationImage):
            pass
        a = AnimationFactory()
        a["animation_a"] = ExampleAnimation
        animation = a["jump_animation"]
        animation.let_play_animation()
    """

    def __init__(self, *args, **kwargs):
        self.__dict__: dict[Any, AnimationImage]
        self.__dict__.update(*args, **kwargs)
        # self.anim_action_id = 0

    # def register(self, animation: AnimationImage):
        # self.__setitem__()

    def __getitem__(self, key) -> AnimationImage:
        return self.__dict__[key]()

    def __setitem__(self, key, value: AnimationImage):
        if isclass(value):
            self.__dict__[key] = value
        else:
            raise ValueError("The value must not be instance.")

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


class AnimationDict(MutableMapping):
    """
    Examples:
        class ExampleAnimation(AnimationImage):
            pass
        a = AnimationFactory()
        a["animation_a"] = ExampleAnimation()
        animation = a["jump_animation"]
        animation.let_play_animation()
    """

    def __init__(self, *args, **kwargs):
        self.__dict__: dict[Any, AnimationImage]
        self.__dict__.update(*args, **kwargs)

    def __getitem__(self, key) -> AnimationImage:
        return self.__dict__[key]

    def __setitem__(self, key, value: AnimationImage):
        if not isclass(value):
            self.__dict__[key] = value
        else:
            raise ValueError("The value must be instance.")

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


class SpriteSheet:
    def __init__(self, filename):
        self.image = pygame.image.load(filename)

    def image_by_area(self, x, y, width, height) -> pygame.surface.Surface:
        """"""
        image = pygame.Surface((width, height))
        image.blit(self.image, (0, 0), (x, y, width, height))
        image.set_colorkey((0, 0, 0))
        # image = pg.transform.scale(image, (width // 2, height // 2))
        return image
