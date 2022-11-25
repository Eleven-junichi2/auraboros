import functools
from typing import Callable


from . import global_

# TODO: make clock count reset feature


class IntervalCounter:
    """This is used to implement intervals for scheduling functions."""
    counters = []

    def __init__(self):
        self.counters.append(self)
        self.count = 0

    def increment_count(self, dt):
        self.count += round(1 * dt * global_.TARGET_FPS, 3)
        # self.count += 1 * dt * global_.TARGET_FPS

    @classmethod
    def tick(cls, dt):
        [counter.increment_count(dt) for counter in cls.counters]


class _ScheduleManager:
    funcs: dict[Callable, IntervalCounter] = {}

    def __init__(self):
        pass

    def register(self, func_name: str, clock: IntervalCounter):
        self.funcs[func_name] = clock


def schedule_instance_method_interval(
        variable_as_interval: str, interval_ignorerer=None):
    """This decorator is for method of object.
    Args:
        variable_as_interval:
            The name of the variable as interval.
        times:
            Indicates how many times the decorated function is executed.
        interval_ignorerer:
            The name of the bool variable that is the condition for ignoring
            interval.
            If interval_ignorer is True, the decorated function is executed
            regardless of the interval.

    Examples:
        class ClassA:
            def __init__(self):
                self.interval_a = 3

            @schedule_instance_method_interval("interval_a")
            def func_a(self):
                pass

        while True:
            instance_a = ClassA()
            instance_a.func_a()
            if clock_counter < 60:
                clock_counter += 1
            else:
                clock_counter = 0
    """
    def _decorator(func):
        _decorator.schedule_manager = _ScheduleManager()

        @functools.wraps(func)
        def _wrapper(self, *args, **kwargs):
            execute_func = False
            method_id = str(id(self)) + str(func.__name__)
            if not (method_id in _decorator.schedule_manager.funcs):
                _decorator.schedule_manager.funcs[
                    method_id] = IntervalCounter()
                _decorator.schedule_manager.funcs[
                    method_id].count = getattr(self, variable_as_interval)
            if interval_ignorerer:
                bool_from_interval_ignorerer = getattr(
                    self, interval_ignorerer)
            else:
                bool_from_interval_ignorerer = False
            count = _decorator.schedule_manager.funcs[method_id].count
            interval = float(getattr(self, variable_as_interval))
            if ((count >= interval)
                    or bool_from_interval_ignorerer):
                execute_func = True
            if (count > interval):
                _decorator.schedule_manager.funcs[method_id].count = 0
            if execute_func:
                return func(self, *args, **kwargs)
        return _wrapper

    return _decorator
