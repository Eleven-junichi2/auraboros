
# from collections import deque
from pathlib import Path
import sys
# from string import ascii_lowercase

import setup_syspath  # noqa
from auraboros import engine
from auraboros.gametext import GameText, Font2
from auraboros.gamescene import Scene, SceneManager
from auraboros.utils.path import AssetFilePath
from auraboros.utils.surface import draw_grid

engine.init(caption="Test GameText system", base_pixel_scale=2)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(
    Font2(AssetFilePath.font("misaki_gothic.ttf"), 16), "misakigothic")
GameText.setup_font(
    Font2(AssetFilePath.font("ayu18gothic/9x18gm.bdf"), 16), "ayu18gothic")


class DebugScene(Scene):
    def setup(self):
        GameText.use_font("misakigothic")
        self.gametext_sample = GameText(
            "this is a sample of\nmultiline text using GameText object.",
            (0, 0))

    def draw(self, screen):
        draw_grid(screen, 16, (78, 78, 78))
        self.gametext_sample.renderln(20, surface_to_blit=screen)


scene_manager = SceneManager()
scene_manager.add(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager, fps=60)