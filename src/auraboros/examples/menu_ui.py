from pathlib import Path
import sys

import pygame

import setup_syspath  # noqa
from auraboros import engine
from auraboros.gametext import GameText, Font2

from auraboros.ui import OptionsUI
from auraboros.gamescene import Scene, SceneManager
from auraboros.utils.path import AssetFilePath
from auraboros.utils.surface import draw_grid

engine.init(caption="Test Label", base_pixel_scale=2)

AssetFilePath.set_root_dir(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(
    Font2(AssetFilePath.get_asset("fonts/PixelMPlus/PixelMplus10-Regular.ttf"), 20),
    "PixelMplus10Regular",
)


class ExampleScene(Scene):
    def setup(self):
        GameText.use_font("PixelMplus10Regular")
        self.menuui = OptionsUI(spacing=10, padding=10)
        self.menuui.interface.add_option("test1", "TEST I")
        self.menuui.interface.add_option("test2", "TEST II")
        self.menuui.interface.add_option("test3", "TEST III")
        self.menuui.interface.add_option("test4", "TEST IV")

    def update(self, dt):
        self.menuui.update(dt)

    def draw(self, screen: pygame.surface.Surface):
        draw_grid(screen, 16, (78, 78, 78))
        self.menuui.draw(screen)


scene_manager = SceneManager()
scene_manager.add(ExampleScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
