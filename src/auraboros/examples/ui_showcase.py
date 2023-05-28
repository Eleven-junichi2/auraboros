import setup_syspath  # noqa

from pathlib import Path
import sys

import pygame

from auraboros import engine
from auraboros.gamescene import SceneManager, Scene
from auraboros.ui import TextUI
from auraboros.gametext import Font2, GameText
from auraboros.utils.path import AssetFilePath

engine.init(caption="Hello, World!")

AssetFilePath.set_root_dir(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(
    Font2(AssetFilePath.get_asset("fonts/PixelMPlus/PixelMplus12-Regular.ttf"), 24),
    "PixelMPlus12-Regular"
)


class TextUIScene(Scene):
    def setup(self):
        self.textui_example = TextUI([0, 0], GameText("Example of TextUI"))

    def draw(self, screen: pygame.surface.Surface):
        self.textui_example.draw(screen)


scenemanager = SceneManager()
scenemanager.add(TextUIScene(scenemanager))

if __name__ == "__main__":
    engine.run(scenemanager)
