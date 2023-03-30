from collections import UserDict
from typing import Callable, TypedDict

import pygame

# TODO: mouse input


class Keyboard:
    # TODO: inplement non repeat input
    def __init__(self):
        self.keyaction_dict: dict[int, KeyActionItem] = {}

    def __getitem__(self, key):
        return self.keyaction_dict[key]

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.keyaction_dict.get(event.key):
                # print("DOWN", event.key)
                self.keyaction_dict[event.key]["is_pressed"] = True
        if event.type == pygame.KEYUP:
            if self.keyaction_dict.get(event.key):
                # print("UP", event.key)
                self.keyaction_dict[event.key]["is_pressed"] = False

    def release_all_of_keys(self):
        for key in self.keyaction_dict.keys():
            self.keyaction_dict[key]["is_pressed"] = False

    def do_action_by_keyinput(self, key_const, ignore_inregistered_key=False):
        # TODO: refactor this
        if self.keyaction_dict.get(key_const) is None\
                and ignore_inregistered_key:
            return
        IS_PRESSED = self.keyaction_dict[key_const]["is_pressed"]
        DELAY = self.keyaction_dict[key_const]["delay"]
        INTERVAL = self.keyaction_dict[key_const]["interval"]
        do_keydown = False
        do_keyup = False
        if IS_PRESSED:
            # print("do_action", key_const)
            if not self.keyaction_dict[key_const]["_first_input_finished"]:
                # first input
                if self.keyaction_dict[key_const][
                        "_delay_counter"] < DELAY:
                    self.keyaction_dict[key_const]["_delay_counter"] += 1
                else:
                    self.keyaction_dict[key_const]["_delay_counter"] = 0
                    do_keydown = True
                    self.keyaction_dict[key_const][
                        "_first_input_finished"] = True
            else:
                # repeating input
                if self.keyaction_dict[key_const][
                        "_interval_counter"] < INTERVAL:
                    self.keyaction_dict[key_const]["_interval_counter"] += 1
                else:
                    self.keyaction_dict[key_const]["_interval_counter"] = 0
                    do_keydown = True
        else:
            self.keyaction_dict[key_const]["_delay_counter"] = 0
            self.keyaction_dict[key_const]["_interval_counter"] = 0
            self.keyaction_dict[key_const]["_first_input_finished"] = False
            do_keyup = True
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

        self.keyaction_dict[key_const] = KeyActionItem({
            "keydown": keydown, "keyup": keyup,
            "delay": delay, "interval": interval,
            "is_pressed": False,
            "_delay_counter": 0, "_interval_counter": 0,
            "_first_input_finished": False,
            "keydown_deactivated": False,
            "keyup_deactivated": False})

    def deactivate_keyup(self, key_const):
        self.keyaction_dict[key_const]["keyup_deactivated"] = True

    def activate_keyup(self, key_const):
        self.keyaction_dict[key_const]["keyup_deactivated"] = False

    def deactivate_keydown(self, key_const):
        self.keyaction_dict[key_const]["keydown_deactivated"] = True

    def activate_keydown(self, key_const):
        self.keyaction_dict[key_const]["keydown_deactivated"] = False


class KeyActionItem(TypedDict):
    keydown: Callable
    keyup: Callable
    delay: int
    interval: int
    is_pressed: bool
    _delay_counter: int
    _interval_counter: int
    _first_input_finished: bool
    keydown_deactivated: bool
    keyup_deactivated: bool


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


class Joystick2:
    def __init__(self, joystick: pygame.joystick.Joystick):
        self.joystick = joystick

    def event(self, event):
        if event.type == pygame.JOYAXISMOTION:
            stick0 = self.joystick.get_axis(0)
            stick1 = self.joystick.get_axis(1)
            print(stick0, stick1)
        elif event.type == pygame.JOYBUTTONDOWN:
            print(event.button)
        elif event.type == pygame.JOYBUTTONUP:
            print(event.button)
        elif event.type == pygame.JOYHATMOTION:
            hat_pos = self.joystick.get_hat(0)
            print(hat_pos)
