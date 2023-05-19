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
from auraboros.utils.path import AssetFilePath
from auraboros.utils.surface import draw_grid

engine.init(caption="Test MsgBox", base_pixel_scale=2)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(
    Font2(AssetFilePath.font("PixelMPlus/PixelMplus12-Regular.ttf"), 24),
    "PixelMplus12Regular",
)

EXAMPLE_TEXT_FOR_MSGBOX = (
    "メロスは激怒した。必ず、かの邪智暴虐の王を除かなければならぬと決意した。",
    "メロスには政治がわからぬ。メロスは、村の牧人である。",
    "笛を吹き、羊と遊んで暮して来た。けれども邪悪に対しては、人一倍に敏感であった。",
    "きょう未明メロスは村を出発し、野を越え山越え、十里はなれた此のシラクスの市にやって来た。",
    "メロスには父も、母も無い。女房も無い。十六の、内気な妹と二人暮しだ。",
)
EXAMPLE_TEXT_FOR_MSGBOX = "\n".join(EXAMPLE_TEXT_FOR_MSGBOX)


class DebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        GameText.use_font("PixelMplus12Regular")
        self.msgbox1 = MsgBoxUI(
            GameText.font,
            EXAMPLE_TEXT_FOR_MSGBOX,
        )

    def update(self, dt):
        pass

    def draw(self, screen: pygame.Surface):
        draw_grid(screen, 8, (78, 78, 78))
        self.msgbox1.draw(screen)


scene_manager = SceneManager()
scene_manager.add(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
