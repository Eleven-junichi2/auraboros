
# from collections import deque
from pathlib import Path
import sys
# from string import ascii_lowercase

import pygame

import init_for_dev  # noqa
from auraboros import engine
from auraboros.utilities import AssetFilePath, draw_grid, pos_on_pixel_scale
from auraboros.gametext import TextSurfaceFactory
from auraboros.gamescene import Scene, SceneManager
from auraboros.gameinput import Keyboard
from auraboros.ui import GameMenuSystem, GameMenuUI, MsgWindow
from auraboros import global_

engine.init(pixel_scale=2)

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
        self.menusystem = GameMenuSystem()
        self.keyboard["menu"].register_keyaction(
            pygame.K_UP, 0, 122, 122, self.menusystem.menu_cursor_up)
        self.keyboard["menu"].register_keyaction(
            pygame.K_DOWN, 0, 122, 122, self.menusystem.menu_cursor_down)
        self.keyboard["menu"].register_keyaction(
            pygame.K_z, 0, 122, 122, self.menusystem.do_selected_action)
        self.menusystem.add_menu_item(
            "red", self.turn_red,
            lambda: self.msgwindow.rewrite_text("Red"),
            text="RED")
        self.menusystem.add_menu_item(
            "green", self.turn_green,
            lambda: self.msgwindow.rewrite_text("Green"),
            text="GREEN")
        self.menusystem.add_menu_item(
            "blue", self.turn_blue,
            lambda: self.msgwindow.rewrite_text("Blue"),
            text="BLUE")
        self.menuui = GameMenuUI(self.menusystem, textfactory, "filled_box")
        self.menuui.padding = 4
        self.msgwindow = MsgWindow(textfactory.font())
        self.msgwindow.padding = 4
        self.msgwindow2 = MsgWindow(textfactory.font())
        self.msgwindow2.padding = 10
        self.msgwindow2.text = "Press 'Z' to turn color of the box."
        self.turn_red()
        self.box_size = (24, 24)
        self.mouse.register_mouseaction(
            "down",
            on_left=lambda: self.menuui.do_option_if_givenpos_on_ui(
                pos_on_pixel_scale(pygame.mouse.get_pos())))

    def turn_red(self):
        self.box_color = (255, 0, 0)
        self.msgwindow.text = "Red"

    def turn_green(self):
        self.box_color = (0, 255, 0)
        self.msgwindow.text = "Green"

    def turn_blue(self):
        self.box_color = (0, 0, 255)
        self.msgwindow.text = "Blue"

    def update(self, dt):
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_UP)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_DOWN)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_z)
        self.menuui.set_pos_to_center()
        self.msgwindow.set_x_to_center()
        self.msgwindow.pos[1] = global_.w_size[1]//3*2
        self.menusystem.update()
        self.menuui.highlight_option_on_givenpos(
            pos_on_pixel_scale(pygame.mouse.get_pos()))

    def draw(self, screen):
        draw_grid(screen, 16, (78, 78, 78))
        pygame.draw.rect(
            screen, self.box_color,
            tuple(map(sum, zip(self.menuui.pos, self.menuui.real_size))) +
            self.box_size)
        self.menuui.draw(screen)
        self.msgwindow.draw(screen)
        self.msgwindow2.draw(screen)


scene_manager = SceneManager()
scene_manager.push(GameMenuDebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
