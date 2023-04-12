from inspect import isclass
from typing import Any, MutableMapping

import pygame

from .schedule2 import Schedule


class AnimationImage:
    """アニメーションのある画像を設定・描写するためのクラス

    Attributes:
        anim_frame_id (int): 現在のフレームを示すインデックス
        anim_interval (int): アニメーションの更新間隔（ミリ秒）
        image (pygame.surface.Surface): 現在のフレームの画像
        is_playing (bool): アニメーションが再生中かどうかを示すフラグ
    """

    def __init__(self):
        self._anim_frames: list[pygame.surface.Surface] = [
            pygame.surface.Surface((0, 0)), ]
        self.anim_frame_id = 0
        self._anim_interval = 1
        self.image = self.anim_frames[self.anim_frame_id]
        self.is_playing = False

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

    @property
    def anim_interval(self):
        return self._anim_interval

    @anim_interval.setter
    def anim_interval(self, value):
        # Schedule.remove(self.anim_interval)
        print("aaa")
        self._anim_interval = value
        Schedule.add(self.update_animation, self.anim_interval)

    def let_play(self):
        self.is_playing = True

    def let_stop(self):
        self.is_playing = False

    def seek(self, frame_id: int):
        self.anim_frame_id = frame_id
        self.image = self.anim_frames[self.anim_frame_id]

    def reset_animation(self):
        self.anim_frame_id = 0
        self.image = self._anim_frames[self.anim_frame_id]

    def update_animation(self):
        if self.is_playing:
            self.anim_frame_id = (self.anim_frame_id + 1) % len(
                self._anim_frames)
            self.image = self._anim_frames[self.anim_frame_id]


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
