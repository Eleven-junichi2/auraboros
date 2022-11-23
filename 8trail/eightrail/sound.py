# from dataclasses import dataclass
from collections import UserDict
from inspect import isclass
from typing import Any, TypedDict, Union

import pygame


# @dataclass
# class SoundManager:
#     sound_dict = dict[Any, pygame.mixer.Sound] = {}


class SoundDict(UserDict):

    def __init__(self, channel: pygame.mixer.Channel = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel = channel
        self.sound = None

    def __setitem__(self, key, value: pygame.mixer.Sound):
        if not isclass(value):
            self.data[key] = value
        else:
            raise ValueError("The value must be instance.")


class ChannelManager(UserDict):
    def register(
            self, key: Any, channel: pygame.mixer.Channel,
            volume: Union[float, tuple[float, float]]):
        channel.set_volume(volume)
        self.data[key]: ChannelDict = ChannelDict(
            channel=channel, volume=volume)


class _ChannelDictData(TypedDict):
    channel: pygame.mixer.Channel
    volume: Union[float, tuple[float, float]]


class ChannelDict(UserDict):
    def __init__(self, dict=None, /, **kwargs):
        self.data: _ChannelDictData = _ChannelDictData()
        if dict is not None:
            self.update(dict)
        if kwargs:
            self.update(kwargs)

    def __setitem__(self, key, value):
        if key == "volume":
            if not (value < 0 or 1.0 < value):
                self.data["channel"].set_volume(value)
            else:
                return
        super().__setitem__(key, value)
