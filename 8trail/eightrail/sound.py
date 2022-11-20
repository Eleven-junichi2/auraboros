# from dataclasses import dataclass
from collections import UserDict
from inspect import isclass
# from typing import Any

import pygame


# @dataclass
# class SoundManager:
#     sound_dict = dict[Any, pygame.mixer.Sound] = {}


class SoundDict(UserDict):

    def __init__(self, channel: pygame.mixer.Channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel = channel
        self.sound = None

    def __getitem__(self, key) -> pygame.mixer.Sound:
        return self.__dict__[key]

    def __setitem__(self, key, value: pygame.mixer.Sound):
        if not isclass(value):
            self.__dict__[key] = value
        else:
            raise ValueError("The value must be instance.")

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)
