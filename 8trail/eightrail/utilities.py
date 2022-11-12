from dataclasses import dataclass
from pathlib import Path
import sys

import pygame


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
    is_up: bool = False
    is_down: bool = False
    is_right: bool = False
    is_left: bool = False

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

    def switch(self, direction: Arrow):
        if direction is Arrow.up:
            self.is_up = not self.is_up
        elif direction is Arrow.down:
            self.is_down = not self.is_down
        elif direction is Arrow.right:
            self.is_right = self.is_right
        elif direction is Arrow.left:
            self.is_left = self.is_left


class AssetFilePath:
    root = Path(sys.argv[0]).parent / "assets"
    img_dirname = "imgs"
    font_dirname = "fonts"
    sound_dirname = "sounds"

    @ classmethod
    def img(cls, filename):
        return cls.root / cls.img_dirname / filename

    @ classmethod
    def font(cls, filename):
        return cls.root / cls.font_dirname / filename

    @ classmethod
    def sound(cls, filename):
        return cls.root / cls.sound_dirname / filename


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
