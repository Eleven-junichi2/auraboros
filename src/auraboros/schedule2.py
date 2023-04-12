import pygame


# class Clock:
#     """時間の経過を管理するためのクロック機能を提供するクラス"""

#     def __init__(self, clock: pygame.time.Clock):
#         self.clock = clock
#         self._start_time = pygame.time.get_ticks()
#         self._last_tick_time = self._start_time

#     def tick(self):
#         """前回のtickからの経過時間を返す"""
#         elapsed_time = pygame.time.get_ticks() - self._last_tick_time
#         self._last_tick_time = pygame.time.get_ticks()
#         return elapsed_time

#     def get_time(self):
#         """開始からの経過時間を返す"""
#         return pygame.time.get_ticks() - self._start_time


class Schedule:
    """指定した時間間隔で関数を実行するためのスケジュール機能を提供するクラス"""

    _schedule_list = []

    @classmethod
    def add(cls, func, interval):
        """関数をスケジュールに追加する"""
        cls._schedule_list.append((func, interval, pygame.time.get_ticks()))

    @classmethod
    def execute(cls):
        """スケジュールに登録された関数を実行する"""
        current_time = pygame.time.get_ticks()
        for i, (func, interval, last_time) in enumerate(cls._schedule_list):
            if current_time - last_time >= interval:
                func()
                cls._schedule_list[i] = (func, interval, current_time)

    @classmethod
    def remove(cls, func):
        """スケジュールから関数を削除する"""
        cls._schedule_list = [(f, i, t)
                              for f, i, t in cls._schedule_list if f != func]

    @classmethod
    def schedule(cls, interval):
        """スケジュールを登録するデコレータ"""
        def decorator(func):
            cls.add(func, interval)
            return func
        return decorator


def seconds_to_milliseconds(seconds):
    """秒をミリ秒に変換する"""
    return seconds * 1000


def milliseconds_to_seconds(milliseconds):
    """ミリ秒を秒に変換する"""
    return milliseconds / 1000
