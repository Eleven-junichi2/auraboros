
from pathlib import Path
import sys

import pygame

import init_for_dev  # noqa
from auraboros import engine
from auraboros.utilities import AssetFilePath
from auraboros.gametext import TextSurfaceFactory
from auraboros.gamescene import Scene, SceneManager
from auraboros.gameinput import Keyboard

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

textfactory = TextSurfaceFactory()
textfactory.register_font(
    "misaki_gothic",
    pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16))


class TitleMenuScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textfactory.set_current_font("misaki_gothic")
        self.keyboard["qwerty"] = Keyboard()
        for key_name in "qwertyuiopasdfghjklzxcvbnm":
            self.keyboard["qwerty"].register_keyaction(
                pygame.key.key_code(key_name), 0, 0,
                lambda kn=key_name: self.press_key(kn),
                lambda kn=key_name: self.release_key(kn))
        self.key_i_o_map: dict[str: bool] = dict.fromkeys(
            "qwertyuiopasdfghjklzxcvbnm", False)
        self.keyboard.set_current_setup("qwerty")

    def press_key(self, key):
        self.key_i_o_map[key] = True
        print(key)
        textfactory.register_text("recent_pressed", f"{key}")

    def release_key(self, key):
        self.key_i_o_map[key] = False
        print(key)
        textfactory.register_text("recent_pressed", f"{key}")

    def update(self, dt):
        for key_name in "qwertyuiopasdfghjklzxcvbnm":
            self.keyboard["qwerty"].do_action_by_keyinput(
                pygame.key.key_code(key_name))

    def draw(self, screen):
        for i, key_name in enumerate("qwertyuiopasdfghjklzxcvbnm"):
            char_size = textfactory.font().size("a")
            if i < 10:  # key_name <= "p"
                surface_pos = (i*char_size[0], 0)
            elif 10 <= i < 19:  # key_name <= "l"
                surface_pos = (char_size[0]//3+(i-10)
                               * char_size[0], char_size[1])
            elif 19 <= i:  # key_name <= "m"
                surface_pos = (char_size[0]//2+(i-19)
                               * char_size[0], char_size[1]*2)
            if self.key_i_o_map[key_name]:
                text_surface = textfactory.font().render(
                    key_name, True, (89, 255, 89))
                screen.blit(text_surface, surface_pos)
            else:
                text_surface = textfactory.font().render(
                    key_name, True, (255, 255, 255))
                screen.blit(text_surface, surface_pos)

        # textfactory.render("recent_pressed", screen, (32, 16))


scene_manager = SceneManager()
scene_manager.push(TitleMenuScene(scene_manager))

if __name__ == "__main__":
    engine.init()
    engine.run(scene_manager=scene_manager)
