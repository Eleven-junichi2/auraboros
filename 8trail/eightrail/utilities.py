from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
import sys


import pygame


def open_json_file(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


@dataclass
class Arrow:
    """Arrow symbol"""
    up = 0
    down = 1
    right = 2
    left = 3


@dataclass
class ArrowToTurnToward:
    """Use to set direction"""
    is_up: bool = field(default=False)
    is_down: bool = field(default=False)
    is_right: bool = field(default=False)
    is_left: bool = field(default=False)

    def set(self, direction: Arrow):
        if direction is Arrow.up:
            self.is_up = True
        elif direction is Arrow.down:
            self.is_down = True
        elif direction is Arrow.right:
            self.is_right = True
        elif direction is Arrow.left:
            self.is_left = True

    def unset(self, direction: Arrow):
        if direction is Arrow.up:
            self.is_up = False
        elif direction is Arrow.down:
            self.is_down = False
        elif direction is Arrow.right:
            self.is_right = False
        elif direction is Arrow.left:
            self.is_left = False

    # def switch(self, direction: Arrow):
    #     if direction is Arrow.up:
    #         self.is_down = False
    #     elif direction is Arrow.down:
    #         self.is_down = not self.is_down
    #     elif direction is Arrow.right:
    #         self.is_right = self.is_right
    #     elif direction is Arrow.left:
    #         self.is_left = self.is_left

    def is_set_any(self):
        return True in set(asdict(self).values())


class AssetFilePath:
    root_dirname = "assets"
    root = Path(sys.argv[0]).parent / root_dirname
    img_dirname = "imgs"
    font_dirname = "fonts"
    sound_dirname = "sounds"
    level_dirname = "level_data"

    @ classmethod
    def _pyinstaller_path(cls, filepath):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            path = Path(sys._MEIPASS) / cls.root_dirname / filepath
            # path will be such as: "sys._MEIPASS/assets/imgs/example.png"
        except AttributeError:
            path = cls.root / filepath
        return path

    @ classmethod
    def img(cls, filename):
        return cls._pyinstaller_path(Path(cls.img_dirname) / filename)

    @ classmethod
    def font(cls, filename):
        return cls._pyinstaller_path(Path(cls.font_dirname) / filename)

    @ classmethod
    def sound(cls, filename):
        return cls._pyinstaller_path(Path(cls.sound_dirname) / filename)

    @ classmethod
    def level(cls, filename):
        return cls._pyinstaller_path(Path(cls.level_dirname) / filename)


class TextToDebug:
    @ staticmethod
    def arrow_keys(key):
        key_text = f"↑{key[pygame.K_UP]}"
        key_text += f"↓{key[pygame.K_DOWN]}"
        key_text += f"←{key[pygame.K_LEFT]}"
        key_text += f"→{key[pygame.K_RIGHT]}"
        return key_text

    @ staticmethod
    def arrow_keys_from_event(event_key):
        key_text = f"↑{event_key == pygame.K_UP}"
        key_text += f"↓{event_key == pygame.K_DOWN}"
        key_text += f"←{event_key == pygame.K_LEFT}"
        key_text += f"→{event_key == pygame.K_RIGHT}"
        return key_text

    @ staticmethod
    def movement_speed(movement_speed):
        return f"speed:{movement_speed}"

    @ staticmethod
    def fps(clock: pygame.time.Clock):
        return f"FPS:{clock.get_fps()}"
