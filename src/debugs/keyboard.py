
from pathlib import Path
import sys
from string import ascii_lowercase

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

QWERTY_STR = "qwertyuiopasdfghjklzxcvbnm"
AZERTY_STR = "azertyuiopqsdfghjklmwxcvbn"


class KeyboardDebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textfactory.set_current_font("misaki_gothic")
        self.keyboard["qwerty"] = Keyboard()
        self.keyboard["azerty"] = Keyboard()
        for key_name in QWERTY_STR:
            self.keyboard["qwerty"].register_keyaction(
                pygame.key.key_code(key_name), 0, 0,
                lambda kn=key_name: self.press_key(kn),
                lambda kn=key_name: self.release_key(kn))
        self.keyboard["qwerty"].register_keyaction(
            pygame.K_1, 0, 0,
            lambda: self.switch_keyboard_layout("qwerty"))
        for key_name in AZERTY_STR:
            self.keyboard["azerty"].register_keyaction(
                pygame.key.key_code(key_name), 0, 0,
                lambda kn=key_name: self.press_key(kn),
                lambda kn=key_name: self.release_key(kn))
        self.keyboard["azerty"].register_keyaction(
            pygame.K_2, 0, 0,
            lambda: self.switch_keyboard_layout("azerty"))
        self.key_i_o_map: dict[str: bool] = dict.fromkeys(
            ascii_lowercase, False)
        self.keyboard.set_current_setup("qwerty")

    def press_key(self, key):
        self.key_i_o_map[key] = True
        # print(key)
        textfactory.register_text("recent_pressed", f"{key}")

    def release_key(self, key):
        self.key_i_o_map[key] = False
        # print(key)
        textfactory.register_text("recent_pressed", f"{key}")

    def switch_keyboard_layout(self, layout_name):
        self.keyboard.set_current_setup(layout_name)

    def update(self, dt):
        for key_name in ascii_lowercase:
            self.keyboard.current_setup.do_action_by_keyinput(
                pygame.key.key_code(key_name))
        self.keyboard.current_setup.do_action_by_keyinput(
            pygame.K_1, True)
        self.keyboard.current_setup.do_action_by_keyinput(
            pygame.K_2, True)

        textfactory.register_text(
            "current_layout",
            f"layout:{self.keyboard.current_setup_key}",
            color_rgb=(178, 150, 250))

    def draw(self, screen):
        if self.keyboard.current_setup_key == "qwerty":
            keyboard_layout = QWERTY_STR
        elif self.keyboard.current_setup_key == "azerty":
            keyboard_layout = AZERTY_STR
        char_size = textfactory.font().size("a")
        for i, key_name in enumerate(keyboard_layout):
            if i < 10:  # key_name <= "p"(qwerty)
                surface_pos = (i*char_size[0], 0)
            elif 10 <= i < 19:  # key_name <= "l"(qwerty)
                surface_pos = (char_size[0]//3+(i-10)
                               * char_size[0], char_size[1])
            elif 19 <= i:  # key_name <= "m"(qwerty)
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
        textfactory.render("current_layout", screen, (0, char_size[1]*4))


scene_manager = SceneManager()
scene_manager.push(KeyboardDebugScene(scene_manager))

if __name__ == "__main__":
    engine.init()
    engine.run(scene_manager=scene_manager)
