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
from auraboros import global_

os.environ["SDL_IME_SHOW_UI"] = "1"

engine.init()

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")


GameText.setup_font(
    Font2(AssetFilePath.font("misaki_gothic.ttf"), 16), "misakigothic"
)


class DebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.IMEtextinput = ""
        self.textinput = ""
        # set pos display of candidates of google japanese IME
        # by Rect[1], Rect[3]
        self.IME_candidate_rect = pygame.rect.Rect(0, 10, 0, 30)
        pygame.key.set_text_input_rect(self.IME_candidate_rect)

    def event(self, event: pygame.event.Event):
        if event.type == pygame.TEXTEDITING:
            # textinput in full-width characters
            self.IMEtextinput = event.text
            if pygame.key.get_pressed()[pygame.K_RETURN]:
                self.textinput += self.IMEtextinput
        elif event.type == pygame.TEXTINPUT:
            # textinput in half-width characters
            self.textinput += event.text

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


scene_manager = SceneManager()
scene_manager.push(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
