# from collections import UserDict
from typing import Callable, TypedDict

import pygame


class Keyboard:
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

    def do_action_by_keyinput(self, key_const):
        # TODO: refactor this
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
            "_first_input_finished": False})


class KeyActionItem(TypedDict):
    keydown: Callable
    keyup: Callable
    delay: int
    interval: int
    is_pressed: bool
    _delay_counter: int
    _interval_counter: int
    _first_input_finished: bool
