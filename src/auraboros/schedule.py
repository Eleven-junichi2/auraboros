from collections import OrderedDict
from typing import Union

import pygame


class Stopwatch:
    _stopwatch_started: bool = False
    _stopwatch_starttime: int = 0
    _stopwatch_lasttime: int = 0
    _stopwatch_pausetime: int = 0
    _is_stopwatch_running: bool = False

    @classmethod
    def start(cls):
        if cls._stopwatch_starttime == 0:
            cls._stopwatch_starttime = pygame.time.get_ticks()
            cls._stopwatch_started = True
        else:
            cls._stopwatch_starttime += cls.read_pausing()
        cls._is_stopwatch_running = True

    @classmethod
    def update(cls):
        if cls._is_stopwatch_running:
            cls._stopwatch_lasttime = pygame.time.get_ticks()
        elif cls._stopwatch_started:
            cls._stopwatch_pausetime = pygame.time.get_ticks()

    @classmethod
    def stop(cls):
        cls._is_stopwatch_running = False

    @classmethod
    def read(cls):
        return cls._stopwatch_lasttime - cls._stopwatch_starttime

    @classmethod
    def read_pausing(cls):
        if cls._is_stopwatch_running:
            time = 0
        else:
            time = cls._stopwatch_pausetime - cls._stopwatch_lasttime
        return time


class Schedule:
    """指定した時間間隔で関数を実行するためのスケジュール機能を提供するクラス
    _schedule_list = [func, interval, last_time, added_time, is_active]
    """

    _schedule_list: list[dict] = []

    @classmethod
    def add(cls, func, interval):
        """関数をスケジュールに追加する。
        Args:
            func (function): 定期的に呼び出す関数
            interval (int): 関数を呼び出す間隔(milliseconds)
        """
        schedule = OrderedDict()
        schedule["func"] = func
        schedule["interval"] = interval
        schedule["last_time"] = None
        schedule["added_time"] = pygame.time.get_ticks()
        schedule["is_active"] = False
        schedule["deactivated_time"] = None
        schedule["pausing_time"] = None
        cls._schedule_list.append(schedule)

    @classmethod
    def execute(cls):
        """スケジュールに登録された関数を実行する"""
        current_time = pygame.time.get_ticks()

        for schedule in cls._schedule_list:
            if not schedule["is_active"]:
                if schedule["deactivated_time"]:
                    schedule["pausing_time"] = pygame.time.get_ticks() -\
                        schedule["deactivated_time"]
                continue
            if current_time - schedule["last_time"] >= schedule["interval"]:
                schedule["func"]()
                schedule["last_time"] = current_time

    @classmethod
    def remove(cls, func):
        """スケジュールから関数を削除する"""
        cls._schedule_list = [
            schedule for schedule in cls._schedule_list
            if schedule["func"] != func]

    @classmethod
    def is_func_scheduled(cls, func) -> bool:
        """スケジュールに指定した関数が登録されているかどうかを判定する"""
        return any([func == scheduled_func
                   for scheduled_func, _, _, _, _ in cls._schedule_list])

    @classmethod
    def get_mutable_schedule(cls, func) -> Union[dict, None]:
        """指定した関数オブジェクトが登録されているスケジュールを取得する"""
        for schedule in cls._schedule_list:
            if schedule["func"] == func:
                return schedule
        return None

    @classmethod
    def activate_schedule(cls, func):
        """スケジュールに登録した関数のインターバル実行を開始するフラグを立てる。"""
        schedule = cls.get_mutable_schedule(func)
        schedule["is_active"] = True
        schedule["last_time"] = pygame.time.get_ticks()

    @classmethod
    def deactivate_schedule(cls, func):
        """スケジュールに登録した関数のインターバル実行を停止するフラグを立てる。"""
        schedule = cls.get_mutable_schedule(func)
        schedule["is_active"] = False
        schedule["deactivated_time"] = pygame.time.get_ticks()

    @classmethod
    def _debug(cls):
        for schedule in cls._schedule_list:
            schedule = list(schedule.values())
            print("func", id(schedule[0]),
                  "interval", schedule[1],
                  "elapsed", schedule[2],
                  "added", schedule[3],
                  "is active?", schedule[4],
                  "deactivated", schedule[5],
                  "pausing time", schedule[6])
