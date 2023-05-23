from pathlib import Path
import sys

import pygame

import setup_syspath  # noqa
from auraboros import engine
from auraboros.gametext import GameText, Font2

# from auraboros.old_ui import LabelUI
from auraboros.ui import GameTextUI, MsgboxUI, OptionsUI
from auraboros.gamescene import Scene, SceneManager
from auraboros.utils.path import AssetFilePath
from auraboros.utils.surface import draw_grid

engine.init(caption="Test Label", base_pixel_scale=2)

AssetFilePath.set_root_dir(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(
    Font2(AssetFilePath.get_asset("fonts/PixelMPlus/PixelMplus10-Regular.ttf"), 20),
    "PixelMplus10Regular",
)

EXAMPLE_TEXT = "メロスは激怒した。"


class ExampleScene(Scene):
    def setup(self):
        GameText.use_font("PixelMplus10Regular")
        self.gametext1 = GameText(
            text=EXAMPLE_TEXT,
            color_foreground=pygame.Color("#6495ed"),
            color_background=pygame.Color("#ba3162"),
        )
        self.gametext2 = GameText(
            text=EXAMPLE_TEXT,
            color_foreground=pygame.Color("#64ed95"),
            color_background=pygame.Color("#31ba62"),
        )
        self.gametext3 = GameText(
            text=EXAMPLE_TEXT,
            color_foreground=pygame.Color("#6495ed"),
            color_background=pygame.Color("#3162ba"),
        )
        self.gametextui1 = GameTextUI(self.gametext1)
        self.gametextui2 = MsgboxUI(self.gametext2, padding=10)
        self.gametextui2.pos[1] = (
            self.gametextui1.pos[1] + self.gametextui1.real_size[1]
        )
        self.gametextui3 = GameTextUI(self.gametext3)
        self.uilayout1 = OptionsUI(spacing=10)
        self.uilayout1.add_child(self.gametextui1)
        self.uilayout1.add_child(self.gametextui2)
        self.uilayout1.add_child(self.gametextui3)

    def update(self, dt):
        pass

    def draw(self, screen: pygame.surface.Surface):
        draw_grid(screen, 8, (78, 78, 78))
        # self.gametextui1.draw(surface_to_blit=screen)
        # self.gametextui2.draw(surface_to_blit=screen)
        self.uilayout1.draw(screen)


scene_manager = SceneManager()
scene_manager.add(ExampleScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
