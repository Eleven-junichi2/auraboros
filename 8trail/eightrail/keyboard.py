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
                self.keyaction_dict[event.key]["is_pressed"] = True
        if event.type == pygame.KEYUP:
            if self.keyaction_dict.get(event.key):
                self.keyaction_dict[event.key]["is_pressed"] = False

    def action_by_keyinput(self, pygame_key_const):
        # run keyaction whether the key is pressed
        if self.keyaction_dict[pygame_key_const]['is_pressed']:
            if self.keyaction_dict[pygame_key_const]['_interval_counter'] == 0:
                self.keyaction_dict[pygame_key_const]['_interval_counter'] += 1
                return self.keyaction_dict[pygame_key_const]["keydown"]()
            elif self.keyaction_dict[
                    pygame_key_const][
                        '_interval_counter'] == self.keyaction_dict[
                        pygame_key_const]['interval']:
                self.keyaction_dict[pygame_key_const]['_interval_counter'] = 0
                return self.keyaction_dict[pygame_key_const]["keydown"]()
            else:
                self.keyaction_dict[pygame_key_const]['_interval_counter'] += 1
        else:
            self.keyaction_dict[pygame_key_const]['_interval_counter'] = 0
            return self.keyaction_dict[pygame_key_const]["keyup"]()

    def register_keyaction(
            self,
            pygame_key_const,
            delay, interval,
            keydown: Callable = lambda: None, keyup: Callable = lambda: None):

        self.keyaction_dict[pygame_key_const] = KeyActionItem({
            "keydown": keydown, "keyup": keyup,
            "delay": delay, "interval": interval,
            "is_pressed": False,
            "_delay_counter": 0, "_interval_counter": 0})


class KeyActionItem(TypedDict):
    keydown: Callable
    keyup: Callable
    delay: int
    interval: int
    is_pressed: bool
