"""
This module implements classes for event handlers for mouse, keyboard, joystick
and other input events.
"""

from collections import UserDict
from dataclasses import dataclass
from typing import Callable, Union

import pygame

from .schedule import Stopwatch
from .gametext import split_multiline_text, len_str_contain_fullwidth_char
from .utilities import is_char_fullwidth


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
        self,
        pygame_key_const: int,
        delay: int,
        interval: int,
        first_interval: int,
        keydown: Callable = lambda: None,
        keyup: Callable = lambda: None,
    ):
        """first_interval = interval if first_interval is None"""
        if first_interval is None:
            first_interval = interval
        self.keyactions[pygame_key_const] = KeyAction(
            delay=delay,
            interval=interval,
            first_interval=first_interval,
            keydown=keydown,
            keyup=keyup,
        )

    def is_keyaction_regitered(self, pygame_key_const: int) -> bool:
        return True if self.keyactions.get(pygame_key_const) else False

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.is_keyaction_regitered(event.key):
                self.keyactions[event.key]._is_pressed = True
        if event.type == pygame.KEYUP:
            if self.is_keyaction_regitered(event.key):
                self.keyactions[event.key]._is_pressed = False

    def do_action_on_keyinput(self, pygame_key_const, ignore_unregistered=True):
        if not self.is_keyaction_regitered(pygame_key_const) and ignore_unregistered:
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
                    if self.keyactions[KEY]._input_timer.read() >= INTERVAL:
                        do_keydown = True
                        self.keyactions[KEY]._input_timer.reset()
                else:
                    if self.keyactions[KEY]._input_timer.read() >= FIRST_INTERVAL:
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
        self._current_setup: Keyboard = None
        self._current_setup_key = None

    @property
    def current_setup(self):
        return self._current_setup

    @property
    def current_setup_key(self):
        return self._current_setup_key

    def set_current_setup(self, key):
        if self._current_setup_key == key:
            return
        if self._current_setup is not None:
            self._current_setup.release_all_of_keys()
        self._current_setup = self.data[key]
        self._current_setup_key = key


FuncsOnMouseEvent = dict[str : dict[str, Callable]]


class Mouse:
    def __init__(self):
        self.is_dragging = False
        self.pos_drag_start = None
        self._funcs_on_event: FuncsOnMouseEvent = {
            "up": {
                "left": lambda: None,
                "middle": lambda: None,
                "right": lambda: None,
                "wheel_up": lambda: None,
                "wheel_down": lambda: None,
            },
            "down": {
                "left": lambda: None,
                "middle": lambda: None,
                "right": lambda: None,
                "wheel_up": lambda: None,
                "wheel_down": lambda: None,
            },
            "motion": {
                "left": lambda: None,
                "middle": lambda: None,
                "right": lambda: None,
            },
            "drag": {
                "left": lambda drag_pos: None,
                "middle": lambda drag_pos: None,
                "right": lambda drag_pos: None,
            },
        }
        self.is_dragging = {"left": False, "middle": False, "right": False}
        self.pos_prev_drag = {"left": None, "middle": None, "right": None}

    @staticmethod
    def _translate_int_pygame_mouse_event_to_str(int_pygame_mouse_event_type):
        return {
            pygame.MOUSEBUTTONDOWN: "down",
            pygame.MOUSEBUTTONUP: "up",
            pygame.MOUSEMOTION: "motion",
        }[int_pygame_mouse_event_type]

    def register_mouseaction(
        self,
        keyname_or_int_pygame_mouse_event_type: Union[str, int],
        on_left: Union[Callable, None] = None,
        on_middle: Union[Callable, None] = None,
        on_right: Union[Callable, None] = None,
        on_wheel_up: Union[Callable, None] = None,
        on_wheel_down: Union[Callable, None] = None,
    ):
        """
        Args:
            keyname_or_int_pygame_mouse_event_type (Union[str, int]):
                The keyname or the int value of the mouse event.

                "up" or "down" or "motion", "drag".

                You can also use the int value of the pygame mouse event.

                MOUSEBUTTONDOWN or MOUSEBUTTONUP, MOUSEMOTION.
        """
        if isinstance(keyname_or_int_pygame_mouse_event_type, int):
            key = self._translate_int_pygame_mouse_event_to_str(
                keyname_or_int_pygame_mouse_event_type
            )
        else:
            key = keyname_or_int_pygame_mouse_event_type
        if on_left:
            self._funcs_on_event[key]["left"] = on_left
        if on_middle:
            self._funcs_on_event[key]["middle"] = on_middle
        if on_right:
            self._funcs_on_event[key]["right"] = on_right
        if key != "motion" and "drag":
            if on_wheel_up:
                self._funcs_on_event[key]["wheel_up"] = on_wheel_up
            if on_wheel_down:
                self._funcs_on_event[key]["wheel_down"] = on_wheel_down

    def event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            KEY = "down"
            if event.button == 1:
                self._funcs_on_event[KEY]["left"]()
                self.is_dragging["left"] = True
                self.pos_prev_drag["left"] = pygame.mouse.get_pos()
            elif event.button == 2:
                self._funcs_on_event[KEY]["middle"]()
                self.is_dragging["middle"] = True
                self.pos_prev_drag["middle"] = pygame.mouse.get_pos()
            elif event.button == 3:
                self._funcs_on_event[KEY]["right"]()
                self.is_dragging["right"] = True
                self.pos_prev_drag["right"] = pygame.mouse.get_pos()
            elif event.button == 4:
                self._funcs_on_event[KEY]["wheel_up"]()
            elif event.button == 5:
                self._funcs_on_event[KEY]["wheel_down"]()
        if event.type == pygame.MOUSEBUTTONUP:
            KEY = "up"
            if event.button == 1:
                self._funcs_on_event[KEY]["left"]()
                self.is_dragging["left"] = False
            elif event.button == 2:
                self._funcs_on_event[KEY]["middle"]()
                self.is_dragging["middle"] = False
            elif event.button == 3:
                self._funcs_on_event[KEY]["right"]()
                self.is_dragging["right"] = False
            elif event.button == 4:
                self._funcs_on_event[KEY]["wheel_up"]()
            elif event.button == 5:
                self._funcs_on_event[KEY]["wheel_down"]()
        elif event.type == pygame.MOUSEMOTION:
            KEY = "motion"
            if pygame.mouse.get_pressed()[0]:
                self._funcs_on_event[KEY]["left"]()
            else:
                pass
            if pygame.mouse.get_pressed()[1]:
                self._funcs_on_event[KEY]["middle"]()
            else:
                pass
            if pygame.mouse.get_pressed()[2]:
                self._funcs_on_event[KEY]["right"]()
            else:
                pass
            KEY = "drag"
            if self.is_dragging["left"]:
                self._funcs_on_event[KEY]["left"](event.pos)
                self.pos_prev_drag["left"] = event.pos
            if self.is_dragging["middle"]:
                self._funcs_on_event[KEY]["middle"](event.pos)
                self.pos_prev_drag["middle"] = event.pos
            if self.is_dragging["right"]:
                self._funcs_on_event[KEY]["right"](event.pos)
                self.pos_prev_drag["right"] = event.pos


class TextInput:
    def __init__(self):
        self._IMEinput = ""
        self.text = ""
        self.keyboard = Keyboard()
        self.keyboard.register_keyaction(
            pygame.K_RETURN, 0, 44, 88, keydown=self.start_newline
        )
        self.keyboard.register_keyaction(
            pygame.K_BACKSPACE, 0, 44, 88, keydown=self.backspace
        )
        self.is_active = False
        self.is_inputing_with_IME = False
        self.caret_column_num: int = 0
        self.caret_line_num: int = 0
        self.column_num_at_line_wrap: int = None

    @property
    def text_lines(self):
        return split_multiline_text(self.text)

    def activate(self):
        self.is_active = True
        pygame.key.start_text_input()

    def deactivate(self):
        self.is_active = False
        pygame.key.stop_text_input()

    def let_keyboard_input(self):
        if self.is_active:
            self.keyboard.do_action_on_keyinput(pygame.K_RETURN)
            self.keyboard.do_action_on_keyinput(pygame.K_BACKSPACE)

    def event(self, event: pygame.event.Event):
        if self.is_active:
            if event.type == pygame.TEXTEDITING:
                # textinput in full-width characters
                self._IMEtextinput = event.text
                if self._IMEtextinput != "":
                    self.is_inputing_with_IME = True
                else:
                    self.is_inputing_with_IME = False
                # print(
                #     f"event.length: {event.length}"
                #     + " | "
                #     + f"event.start {event.start}"
                #     + " | "
                #     + f"event.text {event.text}"
                #     + " | "
                #     + f"self.is_inputing_with_IME {self.is_inputing_with_IME}"
                #     + " | "
                #     + f"self.caret_column_num {self.caret_column_num}"
                #     + " | "
                #     + f"self.caret_line_num {self.caret_line_num}"
                # )
                if pygame.key.get_pressed()[pygame.K_RETURN]:
                    self.text += self._IMEtextinput
                    self.caret_column_num += len_str_contain_fullwidth_char(
                        self._IMEtextinput
                    )
                if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
                    self.back_caret_pos()
            elif event.type == pygame.TEXTINPUT:
                # textinput in half-width characters
                self.text += event.text
                self.caret_column_num += len_str_contain_fullwidth_char(event.text)
                print(
                    f"self.is_inputing_with_IME {self.is_inputing_with_IME}"
                    + " | "
                    + f"self.caret_column_num {self.caret_column_num}"
                    + " | "
                    + f"self.caret_line_num {self.caret_line_num}"
                )

    def start_newline(self):
        self.start_newline_caret()
        self.text += "\n"

    def backspace(self):
        self.back_caret_pos()
        self.text = self.text[:-1]
        print(
            f"self.caret_column_num {self.caret_column_num}"
            + " | "
            + f"self.caret_line_num {self.caret_line_num}"
        )

    def start_newline_caret(self):
        self.caret_column_num = 0
        self.caret_line_num += 1

    def back_caret_pos(self):
        print("---back caret---")
        if self.caret_column_num > 0:
            print("through self.caret_column_num > 0")
            if is_char_fullwidth(self.text[-1]) and not self.caret_column_num < 2:
                back_length = 2
            else:
                back_length = 1
            print("back_length: ", back_length)
            self.caret_column_num -= back_length
            print("self.caret_column_num: ", self.caret_column_num)
        else:
            if self.caret_line_num > 0:
                print("back line")
                self.caret_line_num -= 1
                self.caret_column_num = len(self.text_lines[self.caret_line_num])
