from collections import UserDict
from dataclasses import dataclass
from typing import Callable, TypedDict, Union

import pygame

from .schedule import Stopwatch


@dataclass
class KeyAction:
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
        self.keyactions: dict[int, KeyAction] = {}

    def __getitem__(self, key) -> KeyAction:
        return self.keyactions[key]

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
        self.keyactions[pygame_key_const] = KeyAction(
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
            return self.keyactions[KEY].keydown()
        if do_keyup:
            return self.keyactions[KEY].keyup()

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
        if self.current_setup_key == key:
            return
        if self.current_setup is not None:
            self.current_setup.release_all_of_keys()
        self.current_setup = self.data[key]
        self.current_setup_key = key


class Mouse:
    def __init__(self):
        self.is_dragging = False
        self.pos_drag_start = None

    # def new_pos_by_dragging(self, pos_to_drag):
    #     new_pos = pos_to_drag -= event.pos[0] - \
    #         self.pos_start_drag[0]
    #     self.camera.offset_y -= event.pos[1] - \
    #         self.pos_start_drag[1]
    #     self.pos_start_drag = event.pos[]

    def event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pass
            elif event.button == 2:
                pass
            elif event.button == 3:
                pass
            elif event.button == 4:
                pass
            elif event.button == 5:
                pass
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                pass
            elif event.button == 2:
                pass
            elif event.button == 3:
                pass
            elif event.button == 4:
                pass
            elif event.button == 5:
                pass
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:
                pass
            else:
                pass
            if pygame.mouse.get_pressed()[1]:
                pass
            else:
                pass
            if pygame.mouse.get_pressed()[2]:
                pass
            else:
                pass
            if pygame.mouse.get_pressed()[3]:
                pass
            else:
                pass
            if pygame.mouse.get_pressed()[4]:
                pass
            else:
                pass
            if self.is_mouse_dragging:
                self.camera.offset_x -= event.pos[0] - \
                    self.pos_start_drag[0]
                self.camera.offset_y -= event.pos[1] - \
                    self.pos_start_drag[1]
                self.pos_start_drag = event.pos
