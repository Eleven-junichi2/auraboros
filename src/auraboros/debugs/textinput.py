from pathlib import Path
import sys

import pygame

import setup_syspath  # noqa
from auraboros import engine
from auraboros.utils import AssetFilePath
from auraboros.gametext import GameText, Font2
from auraboros.gamescene import Scene, SceneManager

from auraboros.ui import MsgBoxUI, TextInputUI
from auraboros import global_

engine.init()

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")


GameText.setup_font(Font2(AssetFilePath.font("misaki_gothic.ttf"), 16), "misakigothic")
GameText.setup_font(
    Font2(AssetFilePath.font("PixelMPlus/PixelMplus12-Regular.ttf"), 24),
    "PixelMplus12Regular",
)


class RawImplementedTextInputScene(Scene):
    def setup(self):
        GameText.use_font("PixelMplus12Regular")
        self.IMEtextinput = ""
        self.textinput = ""
        self.debug_msgbox1 = MsgBoxUI(GameText.font)
        self.debug_msgbox2 = MsgBoxUI(GameText.font)
        self.debug_msgbox1.property.pos[1] = (
            global_.w_size[1] - self.debug_msgbox1.property.real_size[1]
        )
        self.debug_msgbox2.property.pos[1] = (
            global_.w_size[1]
            - self.debug_msgbox1.property.real_size[1]
            - self.debug_msgbox2.property.real_size[1]
        )
        # you can set pos of displaying candidates of IME
        # by Rect[1], Rect[3]
        # self.IME_candidate_rect = pygame.rect.Rect(0, 10, 0, 30)
        # pygame.key.set_text_input_rect(self.IME_candidate_rect)

    def event(self, event: pygame.event.Event):
        if event.type == pygame.TEXTEDITING:
            # textinput in full-width characters
            self.IMEtextinput = event.text
            if pygame.key.get_pressed()[pygame.K_RETURN]:
                self.textinput += self.IMEtextinput
        elif event.type == pygame.TEXTINPUT:
            # textinput in half-width characters
            self.debug_msgbox1.property.rewrite_text(f"event.text: {event.text}")
            self.textinput += event.text
        elif event.type == pygame.KEYDOWN:
            self.debug_msgbox2.property.rewrite_text(f"event.unicode: {event.unicode}")
            if event.key == pygame.K_RETURN:
                self.textinput += "\n"
            if event.key == pygame.K_BACKSPACE:
                self.textinput = self.textinput[:-1]

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.blit(
            GameText.font.renderln(
                self.textinput,
                True,
                (255, 255, 255),
                line_width_by_px=global_.w_size[0],
            ),
            (0, 0),
        )
        self.debug_msgbox1.draw(screen)
        self.debug_msgbox2.draw(screen)


class DebugScene(Scene):
    def setup(self):
        GameText.use_font("PixelMplus12Regular")
        self.textinputbox1 = TextInputUI(GameText.font)
        self.msgbox1 = MsgBoxUI(GameText.font)
        self.msgbox2 = MsgBoxUI(GameText.font)
        self.msgbox1.property.pos[1] = (
            global_.w_size[1] - self.msgbox1.property.real_size[1]
        )
        self.msgbox2.property.pos[1] = (
            self.msgbox1.property.pos[1] - self.msgbox2.property.real_size[1]
        )
        self.keyboard["textinputbox1"] = self.textinputbox1.interface.keyboard
        # set pos display of candidates of IME
        # by Rect[1], Rect[3]
        self.keyboard.set_current_setup("textinputbox1")
        self.textinputbox1.interface.activate()
        self.textinputbox1.property.fixed_size = [200, 200]

    def event(self, event: pygame.event.Event):
        self.textinputbox1.interface.event(event)
        # self.
        pass

    def update(self, dt):
        self.msgbox1.property.rewrite_text(
            f"real_size of textinput UI: {self.textinputbox1.property.real_size}"
        )
        self.textinputbox1.interface.let_keyboard_input()

    def draw(self, screen):
        self.textinputbox1.draw(screen)
        self.msgbox1.draw(screen)
        self.msgbox2.draw(screen)


scene_manager = SceneManager()
# scene_manager.push(RawImplementedTextInputScene(scene_manager))
scene_manager.push(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
