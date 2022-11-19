from collections import UserDict
from typing import Callable

# import pygame


class Keyboard:
    def __init__(self):
        self.keyaction_dict = {}

    def register_keyaction(
            self,
            pygame_key_const, keydown: Callable, keyup: Callable,
            delay, interval):
        keyaction_item = {
            "keydown": keydown, "keyup": keyup,
            "delay": 0, "interval": 0,
            "is_key_pressed": False}
        self.keyaction_dict[pygame_key_const] = keyaction_item

    def on_press(self, pygame_event_key, *args, **kwargs):
        key_action = self.keyaction_dict.get(pygame_event_key)
        if key_action is not None:
            return self.keyaction_dict[
                pygame_event_key]["keydown"](*args, **kwargs)

    def on_release(self, pygame_event_key, *args, **kwargs) -> Callable:
        return self.keyaction_dict[
            pygame_event_key]["keyup"]


class KeyActionDict(UserDict):
    pass
