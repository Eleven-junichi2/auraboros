from collections import OrderedDict
from typing import Union

import pygame


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
        cls._schedule_list.append(schedule)
        # cls._schedule_list.append(
        #     [func, interval, pygame.time.get_ticks(),
        #      pygame.time.get_ticks(), False])

    @classmethod
    def execute(cls):
        """スケジュールに登録された関数を実行する"""
        current_time = pygame.time.get_ticks()

        # for i, (func, interval, last_time, added_time, is_active)
        # in enumerate(
        #         cls._schedule_list):
        #     if current_time - last_time >= interval:
        #         func()
        #         cls._schedule_list[i][2] = current_time

        for schedule in cls._schedule_list:
            if not schedule["is_active"]:
                continue
            if current_time - schedule["last_time"] >= schedule["interval"]:
                schedule["func"]()
                # cls._schedule_list[i] = [
                #     func, interval, current_time, added_time, True]
                schedule["last_time"] = current_time
                # cls._schedule_list[i][2] = current_time

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
    def get_schedule(cls, func) -> Union[dict, None]:
        """指定した関数オブジェクトが登録されているスケジュールを取得する"""
        for schedule in cls._schedule_list:
            if schedule["func"] == func:
                return schedule
        return None

    @classmethod
    def activate_schedule(cls, func):
        """スケジュールに登録した関数のインターバル実行を開始する。"""
        schedule = cls.get_schedule(func)
        schedule["is_active"] = True
        schedule["last_time"] = pygame.time.get_ticks()

    @classmethod
    def _debug(cls):
        for schedule in cls._schedule_list:
            schedule = list(schedule.values())
            print("func", id(schedule[0]),
                  "interval", schedule[1],
                  "elapsed", schedule[2],
                  "added", schedule[3],
                  "is active?", schedule[4])
