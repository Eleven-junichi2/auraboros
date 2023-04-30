from pathlib import Path
import sys
import os

import pygame

import init_for_dev  # noqa
from auraboros import engine
from auraboros.utilities import AssetFilePath
from auraboros.gametext import GameText, Font2
from auraboros.gamescene import Scene, SceneManager
# from auraboros.gameinput import Keyboard
from auraboros.ui import MsgWindow
# from auraboros import global_

os.environ["SDL_IME_SHOW_UI"] = "1"

engine.init()

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")


GameText.setup_font(
    Font2(AssetFilePath.font("misaki_gothic.ttf"), 16), "misakigothic")


class DebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msgbox1 = MsgWindow(GameText.font)
        self.textinput = ""
        self.msgbox1_rect = pygame.rect.Rect(
            *(self.msgbox1.pos + self.msgbox1.real_size))
        pygame.key.set_text_input_rect(self.msgbox1_rect)

    def event(self, event: pygame.event.Event):
        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_RETURN:
        #         self.textinput = ''
        #     elif event.key == pygame.K_BACKSPACE:
        #         self.textinput = self.textinput[:-1]
        #     else:
        #         self.textinput += event.unicode
        if event.type == pygame.TEXTEDITING:
            self.textinput = event.text
            # print("textediting", event.text)
        elif event.type == pygame.TEXTINPUT:
            self.textinput += event.text
        elif event.type == pygame.KEYDOWN:
            print(event.key)
            if event.key == pygame.K_BACKSPACE:
                self.textinput = self.textinput[:-1]

    def update(self, dt):
        self.msgbox1.rewrite_text(self.textinput)

    def draw(self, screen):
        self.msgbox1.draw(screen)


scene_manager = SceneManager()
scene_manager.push(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
