from pathlib import Path
import sys

import pygame

import setup_syspath  # noqa
from auraboros import engine
from auraboros.gametext import GameText, Font2
from auraboros.ui import LabelUI
from auraboros.gamescene import Scene, SceneManager
from auraboros.utils.path import AssetFilePath
from auraboros.utils.surface import draw_grid

engine.init(caption="Test Label", base_pixel_scale=2)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(
    Font2(AssetFilePath.font("PixelMPlus/PixelMplus10-Regular.ttf"), 20),
    "PixelMplus10Regular",
)

EXAMPLE_TEXT = "メロスは激怒した。"


class ExampleScene(Scene):
    def setup(self):
        GameText.use_font("PixelMplus10Regular")
        self.example_text = GameText(
            text=EXAMPLE_TEXT,
            color_foreground=pygame.Color("#6495ed"),
            color_background=pygame.Color("#ba3162"),
        )
        self.example_msgbox = LabelUI(self.example_text)

    def update(self, dt):
        pass

    def draw(self, screen: pygame.surface.Surface):
        draw_grid(screen, 8, (78, 78, 78))
        self.example_msgbox.draw(screen)


scene_manager = SceneManager()
scene_manager.add(ExampleScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
