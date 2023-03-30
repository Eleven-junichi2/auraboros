
# from collections import deque
from pathlib import Path
import sys
# from string import ascii_lowercase

import pygame

import init_for_dev  # noqa
from auraboros import engine
from auraboros.utilities import AssetFilePath
from auraboros.gametext import TextSurfaceFactory
from auraboros.gamescene import Scene, SceneManager
from auraboros.gameinput import Keyboard
from auraboros.ui import GameMenuSystem
# from auraboros import global_

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

textfactory = TextSurfaceFactory()
textfactory.register_font(
    "misaki_gothic",
    pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16))

QWERTY_STR = "qwertyuiopasdfghjklzxcvbnm"
AZERTY_STR = "azertyuiopqsdfghjklmwxcvbn"


class GameMenuDebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textfactory.set_current_font("misaki_gothic")
        self.keyboard["menu"] = Keyboard()
        self.keyboard.set_current_setup("menu")
        self.gamemenu = GameMenuSystem()
        self.keyboard["menu"].register_keyaction(
            pygame.K_UP, 0, 0, self.gamemenu.menu_cursor_up)
        self.keyboard["menu"].register_keyaction(
            pygame.K_DOWN, 0, 0, self.gamemenu.menu_cursor_down)
        self.keyboard["menu"].register_keyaction(
            pygame.K_z, 0, 0, self.gamemenu.do_selected_action)
        self.gamemenu.do_selected_action()

    def update(self, dt):
        pass

    def draw(self, screen):
        pass


scene_manager = SceneManager()
scene_manager.push(GameMenuDebugScene(scene_manager))

if __name__ == "__main__":
    engine.init()
    engine.run(scene_manager=scene_manager)
