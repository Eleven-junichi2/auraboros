from collections import deque
from pathlib import Path
import sys
from string import ascii_lowercase

import pygame

import init_for_dev  # noqa
from auraboros import engine
from auraboros.utilities import AssetFilePath
from auraboros.gametext import GameText, Font2
from auraboros.gamescene import Scene, SceneManager
from auraboros.gameinput import Keyboard
from auraboros.ui import MsgWindow
from auraboros import global_

engine.init(pixel_scale=2)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")


GameText.setup_font(
    Font2(AssetFilePath.font("misaki_gothic.ttf"), 16), "misakigothic")


QWERTY_STR = "qwertyuiopasdfghjklzxcvbnm"
AZERTY_STR = "azertyuiopqsdfghjklmwxcvbn"


class KeyboardDebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textinput = ""
        self.keyboard["qwerty"] = Keyboard()
        self.keyboard["azerty"] = Keyboard()
        for key_name in QWERTY_STR:
            self.keyboard["qwerty"].register_keyaction(
                pygame.key.key_code(key_name), 0, 22, 89,
                lambda kn=key_name: self.press_key(kn),
                lambda kn=key_name: self.release_key(kn))
        self.keyboard["qwerty"].register_keyaction(
            pygame.K_1, 0, 0, 0,
            lambda: self.switch_keyboard_layout("azerty", "1"))
        for key_name in AZERTY_STR:
            self.keyboard["azerty"].register_keyaction(
                pygame.key.key_code(key_name), 44, 22, 44,
                lambda kn=key_name: self.press_key(kn),
                lambda kn=key_name: self.release_key(kn))
        self.keyboard["azerty"].register_keyaction(
            pygame.K_2, 0, 0, 0,
            lambda: self.switch_keyboard_layout("qwerty", "2"))
        self.key_i_o_map: dict[str: bool] = dict.fromkeys(
            ascii_lowercase, False)
        self.keyboard.set_current_setup("qwerty")
        self.msgbox1 = MsgWindow(GameText.font)
        self.msgbox2 = MsgWindow(GameText.font)
        self.msgbox3 = MsgWindow(GameText.font)
        self.msgbox4 = MsgWindow(GameText.font)
        self.msgbox5 = MsgWindow(GameText.font)

    def press_key(self, key):
        self.textinput += key
        self.key_i_o_map[key] = True

    def release_key(self, key):
        self.key_i_o_map[key] = False

    def switch_keyboard_layout(self, layout_name, key):
        print(key)
        self.keyboard.set_current_setup(layout_name)

    def update(self, dt):
        for key_name in ascii_lowercase:
            self.keyboard.current_setup.do_action_on_keyinput(
                pygame.key.key_code(key_name))
        self.keyboard.current_setup.do_action_on_keyinput(
            pygame.K_1, True)
        self.keyboard.current_setup.do_action_on_keyinput(
            pygame.K_2, True)
        self.msgbox1.pos[1] = global_.w_size[1] - \
            self.msgbox1.real_size[1]
        self.msgbox2.pos[1] = self.msgbox1.pos[1] - \
            self.msgbox2.real_size[1]
        self.msgbox3.pos[1] = self.msgbox2.pos[1] - \
            self.msgbox3.real_size[1]
        self.msgbox4.pos[1] = self.msgbox3.pos[1] - \
            self.msgbox4.real_size[1]
        self.msgbox5.pos[1] = self.msgbox4.pos[1] - \
            self.msgbox5.real_size[1]
        self.msgbox1.text = "q _input_timer: " +\
            str(self.keyboard.current_setup.keyactions[
                pygame.K_q]._input_timer.read())
        self.msgbox2.text = "q _input_timer pause: " +\
            str(self.keyboard.current_setup.keyactions[
                pygame.K_q]._input_timer.read_pausing())
        self.msgbox3.text = "q is_pressed: " +\
            str(self.keyboard.current_setup.keyactions[
                pygame.K_q]._is_pressed)
        self.msgbox4.text = "q is_delayinput_finished: " +\
            str(self.keyboard.current_setup.keyactions[
                pygame.K_q]._is_delayinput_finished)
        self.msgbox5.text = "q is_firstinterval_finished: " +\
            str(self.keyboard.current_setup.keyactions[
                pygame.K_q]._is_firstinterval_finished)

    def draw(self, screen):
        if self.keyboard.current_setup_key == "qwerty":
            keyboard_layout = QWERTY_STR
        elif self.keyboard.current_setup_key == "azerty":
            keyboard_layout = AZERTY_STR
        char_size = GameText.font.size("a")
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
                text_surface = GameText.font.render(
                    key_name, True, (89, 255, 89))
                screen.blit(text_surface, surface_pos)
            else:
                text_surface = GameText.font.render(
                    key_name, True, (255, 255, 255))
                screen.blit(text_surface, surface_pos)
        textinput_size = GameText.font.size(self.textinput)
        textinput_homepos = (0, char_size[1]*6)
        if textinput_size[0] > global_.w_size[0]:
            num_of_chars = global_.w_size[0] // char_size[0]
            textinput_lines = [
                self.textinput[i:i+num_of_chars]
                for i in range(0, len(self.textinput), num_of_chars)]
            if (textinput_size[1]*len(textinput_lines) >
                    global_.w_size[1]-textinput_homepos[1]):
                textinput_deque = deque(self.textinput)
                self.textinput = textinput_deque.pop()
        else:
            textinput_lines = [self.textinput]
        for line_num, line in enumerate(textinput_lines):
            textinput_to_show = line
            textinput_surface = GameText.font.render(
                textinput_to_show, True, (255, 255, 255))
            screen.blit(
                textinput_surface,
                (textinput_homepos[0],
                 textinput_homepos[1]+char_size[1]*line_num))
        self.msgbox1.draw(screen)
        self.msgbox2.draw(screen)
        self.msgbox3.draw(screen)
        self.msgbox4.draw(screen)
        self.msgbox5.draw(screen)


scene_manager = SceneManager()
scene_manager.push(KeyboardDebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
