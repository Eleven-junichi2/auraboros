
from pathlib import Path
import sys

import pygame

import init  # noqa
from auraboros.utilities import AssetFilePath
from auraboros.gametext import TextSurfaceFactory
from auraboros import engine
from auraboros.gamescene import Scene, SceneManager

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

textfactory = TextSurfaceFactory()
textfactory.register_font(
    "misaki_gothic",
    pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16))


class TitleMenuScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textfactory.set_current_font("misaki_gothic")
        textfactory.register_text("hello_world", "Hello, World!")

    def update(self, dt):
        pass

    def draw(self, screen):
        textfactory.render("hello_world", screen, (16, 0))


scene_manager = SceneManager()
scene_manager.push(TitleMenuScene(scene_manager))

if __name__ == "__main__":
    engine.init()
    engine.run(scene_manager=scene_manager)
