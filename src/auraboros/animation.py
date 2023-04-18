from inspect import isclass
from typing import Any, MutableMapping

import pygame

from .schedule import Schedule


class AnimationImage:
    """アニメーションのある画像を設定・描写するためのクラス

    Attributes:
        anim_frame_id (int): 現在のフレームを示すインデックス
        anim_interval (int): アニメーションの更新間隔（ミリ秒）
        image (pygame.surface.Surface): 現在のフレームの画像
        is_playing (bool): アニメーションが再生中かどうかを示すフラグ
        loop_count (int): アニメーションのループ回数。-1で無限ループ指定
        loop_counter (int): 現在のループ回数
    """

    def __init__(self):
        self._anim_frames: list[pygame.surface.Surface] = [
            pygame.surface.Surface((0, 0)), ]
        self.anim_frame_id = 0
        self.anim_interval = 1
        self.image = self.anim_frames[self.anim_frame_id]
        self.is_playing = False
        self.loop_count = -1
        self.loop_counter = 0

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
        self._anim_interval = value
        if Schedule.is_func_scheduled(self.update_animation):
            Schedule.change_interval(self.update_animation, self.anim_interval)
        else:
            Schedule.add(self.update_animation, self.anim_interval)

    def is_all_loop_finished(self):
        return self.loop_count > 0 and self.loop_counter >= self.loop_count

    def let_play(self):
        if not self.is_playing:
            Schedule.activate_schedule(self.update_animation)
        self.is_playing = True
        if self.is_all_loop_finished():
            self.loop_counter = 0

    def let_stop(self):
        if self.is_playing:
            Schedule.deactivate_schedule(self.update_animation)
        self.is_playing = False

    def seek(self, frame_id: int):
        self.anim_frame_id = frame_id
        self.image = self.anim_frames[self.anim_frame_id]

    def reset_current_loop(self):
        self.anim_frame_id = 0
        self.image = self._anim_frames[self.anim_frame_id]

    def reset_animation(self):
        self.anim_frame_id = 0
        self.image = self._anim_frames[self.anim_frame_id]
        self.loop_counter = 0
        Schedule.reset_interval_clock(self.update_animation)

    def update_animation(self):
        if self.is_playing and (self.loop_counter < self.loop_count or
                                self.loop_count < 0):
            self.anim_frame_id = (self.anim_frame_id + 1) % len(
                self._anim_frames)
            self.image = self._anim_frames[self.anim_frame_id]
            if self.anim_frame_id == 0:
                self.loop_counter += 1
                if self.is_all_loop_finished():
                    self.is_playing = False
                    Schedule.deactivate_schedule(self.update_animation)


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
