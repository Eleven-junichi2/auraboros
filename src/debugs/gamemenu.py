
# from collections import deque
from pathlib import Path
import sys
# from string import ascii_lowercase

import pygame

import init_for_dev  # noqa
from auraboros import engine
from auraboros.utilities import AssetFilePath, draw_grid_background
from auraboros.gametext import TextSurfaceFactory
from auraboros.gamescene import Scene, SceneManager
from auraboros.gameinput import Keyboard
from auraboros.ui import GameMenuSystem
from auraboros import global_

engine.init()

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

textfactory = TextSurfaceFactory()
textfactory.register_font(
    "misaki_gothic",
    pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16))

QWERTY_STR = "qwertyuiopasdfghjklzxcvbnm"
AZERTY_STR = "azertyuiopqsdfghjklmwxcvbn"


class GameMenuDebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textfactory.set_current_font("misaki_gothic")
        self.keyboard["menu"] = Keyboard()
        self.keyboard.set_current_setup("menu")
        self.gamemenu = GameMenuSystem()
        self.keyboard["menu"].register_keyaction(
            pygame.K_UP, 0, 10, self.gamemenu.menu_cursor_up)
        self.keyboard["menu"].register_keyaction(
            pygame.K_DOWN, 0, 10, self.gamemenu.menu_cursor_down)
        self.keyboard["menu"].register_keyaction(
            pygame.K_z, 0, 0, self.gamemenu.do_selected_action)
        self.gamemenu.add_menu_item("red", self.turn_red, "RED")
        self.gamemenu.add_menu_item("green", self.turn_green, "GREEN")
        self.gamemenu.add_menu_item("blue", self.turn_blue, "BLUE")
        self.menu_size = [
            self.gamemenu.max_option_text_length()*textfactory.char_size()[0],
            self.gamemenu.count_menu_items()*textfactory.char_size()[1]]
        self.menu_pos = [
            global_.w_size[0]//2-self.menu_size[0]//2,
            global_.w_size[1]//2-self.menu_size[1]//2]
        self.menu_frame_color = (200, 200, 200)
        for i, (key, text) in enumerate(
            zip(self.gamemenu.menu_option_keys,
                self.gamemenu.menu_option_texts)):
            # print(i, key, text)
            textfactory.register_text(
                key, text,
                (self.menu_pos[0],
                 self.menu_pos[1]+textfactory.char_size()[1]*i))
        self.turn_red()
        self.box_size = (24, 24)
        self.menu_cursor_size = textfactory.char_size()
        self.menu_cursor_pos = [
            self.menu_pos[0]-self.menu_cursor_size[0],
            self.menu_pos[1]]

    def turn_red(self):
        self.box_color = (255, 0, 0)

    def turn_green(self):
        self.box_color = (0, 255, 0)

    def turn_blue(self):
        self.box_color = (0, 0, 255)

    def update(self, dt):
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_UP)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_DOWN)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_z)

    def draw(self, screen):
        print(self.gamemenu.menu_selected_index)
        draw_grid_background(screen, 16, (78, 78, 78))
        pygame.draw.rect(
            screen, self.menu_frame_color,
            self.menu_pos + self.menu_size, 1)
        pygame.draw.rect(
            screen, self.box_color,
            tuple(map(sum, zip(self.menu_pos, self.menu_size))) +
            self.box_size)
        for key in self.gamemenu.menu_option_keys:
            textfactory.render(key, screen)
        pygame.draw.polygon(
            screen, self.menu_frame_color,
            ((self.menu_cursor_pos[0],
              self.menu_cursor_pos[1]+self.menu_cursor_size[1]
              * self.gamemenu.menu_selected_index),
             (self.menu_cursor_pos[0]+self.menu_cursor_size[0],
              (self.menu_cursor_pos[1]+self.menu_cursor_size[1]//2)
              + self.menu_cursor_size[1]*self.gamemenu.menu_selected_index),
             (self.menu_cursor_pos[0],
              (self.menu_cursor_pos[1]+self.menu_cursor_size[1])
              + self.menu_cursor_size[1]*self.gamemenu.menu_selected_index)))


scene_manager = SceneManager()
scene_manager.push(GameMenuDebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
