# from collections import deque
from pathlib import Path
import sys

# from string import ascii_lowercase

import pygame

import setup_syspath  # noqa
from auraboros import engine
from auraboros.gametext import GameText, Font2
from auraboros.gamescene import Scene, SceneManager
from auraboros.ui import MenuUI
from auraboros.utilities import AssetFilePath, draw_grid
from auraboros.gameinput import Keyboard

engine.init(caption="Test MsgBox", pixel_scale=2)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(
    Font2(AssetFilePath.font("misaki_gothic.ttf"), 24),
    "misakigothic",
)
GameText.setup_font(
    Font2(AssetFilePath.font("PixelMPlus/PixelMplus12-Regular.ttf"), 24),
    "PixelMplus12Regular",
)


class DebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        GameText.use_font("PixelMplus12Regular")
        # GameText.use_font("misakigothic")
        self.menu1 = MenuUI(GameText.font)
        self.menu1.interface.add_menuitem("option1")
        self.menu1.interface.add_menuitem("option2")
        self.menu1.interface.add_menuitem("option3")
        self.keyboard["menu"] = Keyboard()
        self.keyboard["menu"].register_keyaction(
            pygame.K_UP, 0, 122, 122, self.menu1.interface.cursor_up
        )
        self.keyboard["menu"].register_keyaction(
            pygame.K_DOWN, 0, 122, 122, self.menu1.interface.cursor_down
        )
        self.keyboard["menu"].register_keyaction(
            pygame.K_z, 0, 122, 122, self.menu1.interface.do_selected_action
        )
        self.keyboard.set_current_setup("menu")

    def update(self, dt):
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_UP)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_DOWN)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_z)

    def draw(self, screen: pygame.Surface):
        draw_grid(screen, 16, (78, 78, 78))
        self.menu1.draw(screen)


scene_manager = SceneManager()
scene_manager.push(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager, fps=60)
