from collections import UserDict
from dataclasses import dataclass
from typing import Callable, TypedDict, Union

import pygame

from .schedule import Stopwatch


@dataclass
class _KeyAction:
    delay: int
    first_interval: int
    interval: int
    keydown: Callable
    keyup: Callable
    is_keydown_enabled: bool = True
    is_keyup_enabled: bool = True
    _is_pressed: bool = False
    _input_timer: Stopwatch = None
    _is_delayinput_finished: bool = False
    _is_firstinterval_finished: bool = False

    def __post_init__(self):
        self._input_timer = Stopwatch()


class Keyboard:
    def __init__(self):
        self.keyactions: dict[int, _KeyAction] = {}

    def register_keyaction(
            self, pygame_key_const: int,
            delay: int,
            interval: int,
            first_interval: Union[int, None] = None,
            keydown: Callable = lambda: None,
            keyup: Callable = lambda: None):
        """first_interval = interval if first_interval is None"""
        if first_interval is None:
            first_interval = interval
        self.keyactions[pygame_key_const] = _KeyAction(
            delay=delay, interval=interval, first_interval=first_interval,
            keydown=keydown, keyup=keyup)

    def is_keyaction_regitered(self, pygame_key_const: int) -> bool:
        return True if self.keyactions.get(pygame_key_const) else False

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.is_keyaction_regitered(event.key):
                self.keyactions[event.key]._is_pressed = True
        if event.type == pygame.KEYUP:
            if self.is_keyaction_regitered(event.key):
                self.keyactions[event.key]._is_pressed = False

    def do_action_on_keyinput(
            self, pygame_key_const, ignore_unregistered=True):
        if not self.is_keyaction_regitered(pygame_key_const)\
                and ignore_unregistered:
            return
        KEY = pygame_key_const
        DELAY = self.keyactions[KEY].delay
        FIRST_INTERVAL = self.keyactions[KEY].first_interval
        INTERVAL = self.keyactions[KEY].interval
        IS_KEYDOWN_ACTION_ENABLED = self.keyactions[KEY].is_keydown_enabled
        IS_KEYUP_ACTION_ENABLED = self.keyactions[KEY].is_keyup_enabled
        IS_KEY_PRESSED = self.keyactions[KEY]._is_pressed
        do_keydown = False
        do_keyup = False
        if IS_KEYDOWN_ACTION_ENABLED and IS_KEY_PRESSED:
            self.keyactions[KEY]._input_timer.start()
            if self.keyactions[KEY]._is_delayinput_finished:
                if self.keyactions[KEY]._is_firstinterval_finished:
                    if self.keyactions[KEY]._input_timer.read()\
                            >= INTERVAL:
                        do_keydown = True
                        self.keyactions[KEY]._input_timer.reset()
                else:
                    if self.keyactions[KEY]._input_timer.read()\
                            >= FIRST_INTERVAL:
                        do_keydown = True
                        self.keyactions[KEY]._is_firstinterval_finished = True
                        self.keyactions[KEY]._input_timer.reset()
            else:
                if self.keyactions[KEY]._input_timer.read() >= DELAY:
                    do_keydown = True
                    self.keyactions[KEY]._is_delayinput_finished = True
                    self.keyactions[KEY]._input_timer.reset()
        elif IS_KEYUP_ACTION_ENABLED:
            self.keyactions[KEY]._input_timer.reset()
            self.keyactions[KEY]._input_timer.stop()
            self.keyactions[KEY]._is_delayinput_finished = False
            self.keyactions[KEY]._is_firstinterval_finished = False
            do_keyup = True
        if do_keydown:
            self.keyactions[KEY].keydown()
        if do_keyup:
            self.keyactions[KEY].keyup()

    def release_all_of_keys(self):
        for key in self.keyactions.keys():
            self.keyactions[key]._is_pressed = False

    def enable_action_on_keyup(self, pygame_key_const):
        self.keyactions[pygame_key_const].is_keyup_enabled = True

    def enable_action_on_keydown(self, pygame_key_const):
        self.keyactions[pygame_key_const].is_keydown_enabled = True

    def disable_action_on_keyup(self, pygame_key_const):
        self.keyactions[pygame_key_const].is_keyup_enabled = False

    def disable_action_on_keydown(self, pygame_key_const):
        self.keyactions[pygame_key_const].is_keydown_enabled = False


class KeyboardSetupDict(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, item: Keyboard):
        if isinstance(item, Keyboard):
            self.data[key] = item
        else:
            raise TypeError("The value must be Keyboard object.")

    def __getitem__(self, key) -> Keyboard:
        return self.data[key]


class KeyboardManager(KeyboardSetupDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_setup: Keyboard = None
        self.current_setup_key = None

    def set_current_setup(self, key):
        if self.current_setup is not None:
            self.current_setup.release_all_of_keys()
        self.current_setup = self.data[key]
        self.current_setup_key = key


class OldKeyboard:
    """DEPRECATED"""

    def __init__(self):
        self.keyaction_dict: dict[int, OldKeyActionItem] = {}

    def __getitem__(self, key):
        return self.keyaction_dict[key]

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.keyaction_dict.get(event.key):
                self.keyaction_dict[event.key][
                    "is_pressed"] = True
                self.keyaction_dict[event.key][
                    "last_time"] = pygame.time.get_ticks()
        if event.type == pygame.KEYUP:
            if self.keyaction_dict.get(event.key):
                self.keyaction_dict[event.key]["is_pressed"] = False

    def release_all_of_keys(self):
        for key in self.keyaction_dict.keys():
            self.keyaction_dict[key]["is_pressed"] = False

    def do_action_by_keyinput(self, key_const, ignore_inregistered_key=False):
        if self.keyaction_dict.get(key_const) is None\
                and ignore_inregistered_key:
            return
        IS_PRESSED = self.keyaction_dict[key_const]["is_pressed"]
        DELAY = self.keyaction_dict[key_const]["delay"]
        INTERVAL = self.keyaction_dict[key_const]["interval"]
        last_time = self.keyaction_dict[key_const]["last_time"]
        current_time = pygame.time.get_ticks()
        do_keydown = False
        do_keyup = False
        if IS_PRESSED:
            if current_time - last_time >= DELAY:
                if not self.keyaction_dict[key_const]["_first_input_finished"]:
                    self.keyaction_dict[key_const][
                        "_first_input_finished"] = True
                    do_keydown = True
                elif current_time - last_time >= INTERVAL:
                    do_keydown = True
                    self.keyaction_dict[key_const]["last_time"] = current_time
        else:
            if self.keyaction_dict[key_const]["_first_input_finished"]:
                do_keyup = True
                self.keyaction_dict[key_const]["_first_input_finished"] = False
        if self.keyaction_dict[key_const]["keydown_deactivated"]:
            do_keydown = False
        if self.keyaction_dict[key_const]["keyup_deactivated"]:
            do_keyup = False
        if do_keydown:
            return self.keyaction_dict[key_const]["keydown"]()
        elif do_keyup:
            return self.keyaction_dict[key_const]["keyup"]()

    def register_keyaction(
            self,
            key_const,
            delay, interval,
            keydown: Callable = lambda: None, keyup: Callable = lambda: None):

        self.keyaction_dict[key_const] = OldKeyActionItem({
            "keydown": keydown, "keyup": keyup,
            "delay": delay,
            "interval": interval,
            "is_pressed": False,
            "last_time": 0,
            "_first_input_finished": False,
            "keydown_deactivated": False,
            "keyup_deactivated": False,
            "inputtimer": Stopwatch()})

    def deactivate_keyup(self, key_const):
        self.keyaction_dict[key_const]["keyup_deactivated"] = True

    def activate_keyup(self, key_const):
        self.keyaction_dict[key_const]["keyup_deactivated"] = False

    def deactivate_keydown(self, key_const):
        self.keyaction_dict[key_const]["keydown_deactivated"] = True

    def activate_keydown(self, key_const):
        self.keyaction_dict[key_const]["keydown_deactivated"] = False


class OldKeyActionItem(TypedDict):
    """DEPRECATED"""
    keydown: Callable
    keyup: Callable
    delay: int
    interval: int
    is_pressed: bool
    last_time: int
    _first_input_finished: bool
    keydown_deactivated: bool
    keyup_deactivated: bool
    inputtimer: Stopwatch
