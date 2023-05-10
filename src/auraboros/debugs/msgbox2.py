# from collections import deque
from pathlib import Path
import sys

# from string import ascii_lowercase

import pygame

import setup_syspath  # noqa
from auraboros import engine
from auraboros.gametext import GameText, Font2
from auraboros.gamescene import Scene, SceneManager
from auraboros.ui import MsgBoxUI
from auraboros.utilities import AssetFilePath, draw_grid

engine.init(caption="Test MsgBox", pixel_scale=2)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(
    Font2(AssetFilePath.font("PixelMPlus/PixelMplus12-Regular.ttf"), 24),
    "PixelMplus12Regular",
)


class DebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        GameText.use_font("PixelMplus12Regular")
        self.msgbox1 = MsgBoxUI(
            GameText.font,
            "first line text\nsecond line text",
        )
        self.msgbox1.property.linelength_in_px = 200
        self.msgbox2 = MsgBoxUI(GameText.font)
        self.msgbox1.property.padding = 10
        self.msgbox2.property.pos[1] = self.msgbox1.property.real_size[1]
        self.msgbox3 = MsgBoxUI(GameText.font)
        self.msgbox3.property.pos[1] = (
            self.msgbox2.property.pos[1] + self.msgbox2.property.real_size[1]
        )

    def update(self, dt):
        self.msgbox2.property.rewrite_text(
            "↑size_of_multiline_text()={}".format(
                self.msgbox1.property.font.size_of_multiline_text(
                    self.msgbox1.property.current_page_text,
                    self.msgbox1.property.linelength_in_px,
                )
            )
        )
        self.msgbox3.property.rewrite_text(
            "↑〃(in_charcount=True)={}".format(
                self.msgbox1.property.font.size_of_multiline_text(
                    self.msgbox1.property.current_page_text,
                    self.msgbox1.property.linelength_in_px,
                    getsize_in_charcount=True,
                )
            )
        )

    def draw(self, screen: pygame.Surface):
        draw_grid(screen, 10, (78, 78, 78))
        self.msgbox1.draw(screen)
        self.msgbox2.draw(screen)
        self.msgbox3.draw(screen)


scene_manager = SceneManager()
scene_manager.push(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager, fps=60)
