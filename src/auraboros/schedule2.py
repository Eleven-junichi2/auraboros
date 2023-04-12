import pygame


class Schedule:
    """指定した時間間隔で関数を実行するためのスケジュール機能を提供するクラス"""

    _schedule_list = []

    @classmethod
    def add(cls, func, interval):
        """関数をスケジュールに追加する。
        Args:
            func (function): 定期的に呼び出す関数
            interval (int): 関数を呼び出す間隔(milliseconds)
        """
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
