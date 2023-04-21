
# from collections import deque
from pathlib import Path
import sys
# from string import ascii_lowercase

import pygame

import init_for_dev  # noqa
from auraboros import engine, global_
from auraboros.gametext import TextSurfaceFactory
from auraboros.gamescene import Scene, SceneManager
from auraboros.ui import MsgWindow
from auraboros.utilities import AssetFilePath, draw_grid

engine.init(caption="Test MsgWindow System", pixel_scale=2)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

textfactory = TextSurfaceFactory()
textfactory.register_font(
    "misaki_gothic",
    pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16))


class DebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textfactory.set_current_font("misaki_gothic")
        self.msgbox = MsgWindow(textfactory.font(), "fixed")
        self.msgbox.padding = 4
        self.msgbox.text = "This is a test message."
        self.msgbox.size[0] = global_.w_size[0]*0.95
        self.msgbox.size[1] = global_.w_size[1]*0.22
        self.msgbox.pos[1] = global_.w_size[1]*0.975 - self.msgbox.real_size[1]
        self.msgbox.set_x_to_center()

    def draw(self, screen):
        draw_grid(screen, 16, (78, 78, 78))
        self.msgbox.draw(screen)


scene_manager = SceneManager()
scene_manager.push(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager, fps=60)
