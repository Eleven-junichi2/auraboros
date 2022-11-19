from typing import Callable


class KeyBoard:
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

    def isKeyPressed(self):
        pass
