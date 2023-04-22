import abc
from dataclasses import dataclass
from inspect import isclass
from typing import Any, Callable, MutableMapping, Union

import pygame

from .schedule import Schedule, Stopwatch


class AnimationImage:
    """アニメーションのある画像を設定・描写するためのクラス

        How does it differ from Animation class?

        This class is specified to implement animation of Images,
        such as Sprite.
        Animation class can implement it as this class but require
        executing its update() method after the let_play() method
        to play.
        In this class, the update method of the frame is
        auto-registered to the Schedule class and executed.


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


class AnimFrameProgram(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def script(self):
        raise NotImplementedError

    def reset(self):
        pass


@dataclass
class AnimFrame(metaclass=abc.ABCMeta):
    """
    Attributes:
        interval (int):
            milliseconds to freeze this frame
        duration (int):
            milliseconds for the duration of the program's script execution.
    """
    program: Union[AnimFrameProgram, Callable, None] = None
    interval: int = 0
    duration: int = 0
    is_frame_finished = False

    def __post_init__(self):
        if callable(self.program):
            if self.program.reset is None:
                self.program.reset = lambda: None

    def period(self) -> int:
        """return duration + interval"""
        return self.duration + self.interval

    def do_program(self):
        """
        This is called from Animation object every milliseconds
        for the set duration.
        """
        return_value = None
        if not self.is_frame_finished:
            # print("do program")
            if isinstance(self.program, AnimFrameProgram) or \
                    issubclass(self.program, AnimFrameProgram):
                # print("animframe prg")
                return_value = self.program.script()
            elif callable(self.program):
                # print("callable prg")
                return_value = self.program()
        return return_value

    def reset(self):
        self.program.reset()
        self.is_frame_finished = False


class Animation:
    """
    Examples:
        class TextAddRandIntProgram(AnimFrameProgram):
            @staticmethod
            def script():
                self.msgbox2.text += str(randint(0, 9))

            @staticmethod
            def reset():
                self.msgbox2.text = ""

        self.anim_textshowing = Animation(
            [AnimFrame(TextAddRandIntProgram, 0, 1), ]
        )

    """
    def __init__(self, frames: list[AnimFrame] = [], delay_1st_frame=0):
        self.delay_1st_frame = delay_1st_frame
        self.is_delay_1st_frame_finished = False
        self._frames: list[AnimFrame] = frames
        self.id_current_frame: int = 0
        self.is_playing = False
        self.__timer = Stopwatch()
        self._return_of_script = None

    @property
    def return_of_script(self):
        """return value returned from the program of the current frame."""
        return self._return_of_script

    @property
    def frames(self):
        return self._frames

    @frames.setter
    def frames(self, value):
        self._frames = value

    def let_play(self):
        self.is_playing = True
        if not self.__timer.is_playing:
            self.__timer.start()

    def let_stop(self):
        self.is_playing = False
        if self.__timer.is_playing:
            self.__timer.stop()

    def reset_animation(self, reset_all_programs_of_frames=True):
        self.id_current_frame = 0
        self.__timer.reset()
        if reset_all_programs_of_frames:
            [frame.reset() for frame in self.frames]

    @property
    def current_frame(self) -> AnimFrame:
        return self.frames[self.id_current_frame]

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    def seek(self, frame_id: int):
        self.id_current_frame = frame_id

    def __notify_current_frame_that_the_frame_finished(self):
        self.current_frame.is_frame_finished = True

    def update(self, dt):
        if self.is_playing:
            if self.is_delay_1st_frame_finished:
                if self.__timer.is_playing():
                    pass
                else:
                    self.__timer.start()
                if not self.current_frame.is_frame_finished:
                    if self.__timer.read() <= self.current_frame.duration:
                        print("dura!!!")
                        self._return_of_script = self.current_frame.do_program()
                    if self.__timer.read() >= self.current_frame.period():
                        print("one frame finished")
                        self.id_current_frame = (
                            self.id_current_frame + 1) % self.frame_count
                        self.__timer.stop()
                        self.__notify_current_frame_that_the_frame_finished()
                        if self.id_current_frame == 0:
                            self.is_playing = False
                return self.return_of_script
            else:
                # print("delay phase")
                if self.__timer.is_playing():
                    pass
                else:
                    self.__timer.start()
                if self.__timer.read() >= self.delay_1st_frame:
                    self.is_delay_1st_frame_finished = True
                    self.__timer.reset()
                    self.__timer.stop()

            # self.current_frame.do_program()
            # self.id_current_frame = (
            #     self.id_current_frame + 1) % self.frame_count
            # if self.id_current_frame == self.frame_count:
            #     self.let_stop()
            #     self.id_current_frame = 0


class AnimationFactory(MutableMapping):
    """For AnimationImage

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
    """For AnimationImage

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
