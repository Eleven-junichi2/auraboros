from pathlib import Path
import sys

import pygame

import setup_syspath  # noqa
from auraboros import engine
from auraboros.gametext import GameText, Font2
from auraboros.gamescene import Scene, SceneManager
from auraboros.oldold_ui import MsgBoxUI, TextInputUI
from auraboros.utils.path import AssetFilePath
from auraboros.utils.coordinate import window_size_in_scaled_px

engine.init()

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")


GameText.setup_font(Font2(AssetFilePath.font("misaki_gothic.ttf"), 16), "misakigothic")
GameText.setup_font(
    Font2(AssetFilePath.font("PixelMPlus/PixelMplus12-Regular.ttf"), 24),
    "PixelMplus12Regular",
)


class DebugScene(Scene):
    def setup(self):
        GameText.use_font("PixelMplus12Regular")
        self.textinputbox1 = TextInputUI(GameText.font)
        self.msgbox1 = MsgBoxUI(GameText.font)
        self.msgbox2 = MsgBoxUI(GameText.font)
        self.msgbox1.property.pos[1] = (
            window_size_in_scaled_px()[1] - self.msgbox1.property.real_size[1]
        )
        self.msgbox2.property.pos[1] = (
            self.msgbox1.property.pos[1] - self.msgbox2.property.real_size[1]
        )
        self.keyboard["textinputbox1"] = self.textinputbox1.interface.keyboard
        self.keyboard.set_current_setup("textinputbox1")
        self.textinputbox1.interface.activate()
        self.textinputbox1.property.fixed_size = [200, 200]

    def event(self, event: pygame.event.Event):
        self.textinputbox1.interface.event(event)

    def update(self, dt):
        self.msgbox1.property.rewrite_text(
            f"real_size of textinput UI: {self.textinputbox1.property.real_size}"
        )
        self.textinputbox1.interface.do_keyinput()

    def draw(self, screen):
        self.textinputbox1.draw(screen)
        self.msgbox1.draw(screen)
        self.msgbox2.draw(screen)


scene_manager = SceneManager()
scene_manager.add(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
