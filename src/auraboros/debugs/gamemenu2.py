# from collections import deque
from pathlib import Path
import sys

# from string import ascii_lowercase

import pygame

import setup_syspath  # noqa
from auraboros import engine, global_
from auraboros.gametext import GameText, Font2
from auraboros.gamescene import Scene, SceneManager
from auraboros.ui import MenuUI, MsgBoxUI
from auraboros.utilities import AssetFilePath, draw_grid, pos_on_px_scale
from auraboros.gameinput import Keyboard

engine.init(caption="Test MsgBox", pixel_scale=2)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(
    Font2(AssetFilePath.font("misaki_gothic.ttf"), 24),
    "misakigothic",
)
GameText.setup_font(
    Font2(AssetFilePath.font("PixelMPlus/PixelMplus12-Regular.ttf"), 24),
    "PixelMplus12Regular",
)


class DebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        GameText.use_font("PixelMplus12Regular")
        # GameText.use_font("misakigothic")
        self.msgbox1 = MsgBoxUI(
            GameText.font,
            ["option1 was selected", "option2 was selected", "option3 was selected"],
        )
        self.msgbox2 = MsgBoxUI(
            GameText.font,
            [
                "option1 is highlighted",
                "option2 is highlighted",
                "option3 is highlighted",
            ],
        )
        self.tutorial_msgbox = MsgBoxUI(
            GameText.font,
            "(Press 'Z' to select)",
        )
        self.menu1 = MenuUI(GameText.font, option_highlight_style="cursor")
        self.menu1.interface.add_menuitem(
            "option1",
            action_on_select=lambda: self.msgbox1.property.go_to_page(0),
            action_on_highlight=lambda: self.msgbox2.property.go_to_page(0),
        )
        self.menu1.interface.add_menuitem(
            "option2",
            action_on_select=lambda: self.msgbox1.property.go_to_page(1),
            action_on_highlight=lambda: self.msgbox2.property.go_to_page(1),
        )
        self.menu1.interface.add_menuitem(
            "option3",
            action_on_select=lambda: self.msgbox1.property.go_to_page(2),
            action_on_highlight=lambda: self.msgbox2.property.go_to_page(2),
        )
        self.keyboard["menu"] = Keyboard()
        self.keyboard["menu"].register_keyaction(
            pygame.K_UP, 0, 122, 122, self.menu1.interface.cursor_up
        )
        self.keyboard["menu"].register_keyaction(
            pygame.K_DOWN, 0, 122, 122, self.menu1.interface.cursor_down
        )
        self.keyboard["menu"].register_keyaction(
            pygame.K_z, 0, 122, 122, self.menu1.interface.do_selected_action
        )
        self.keyboard.set_current_setup("menu")
        self.mouse.register_mouseaction(
            "down",
            on_left=lambda: self.menu1.interface.do_selected_action()
            if self.menu1.property.is_givenpos_on_ui(
                pos_on_px_scale(pygame.mouse.get_pos())
            )
            else None,
        )
        self.msgbox2.property.pos[1] = self.msgbox1.property.real_size[1]
        self.menu1.property.pos[1] = (
            self.msgbox2.property.pos[1] + self.msgbox2.property.real_size[1]
        )
        self.tutorial_msgbox.property.pos[1] = (
            global_.w_size[1] - self.tutorial_msgbox.property.real_size[1]
        )

    def update(self, dt):
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_UP)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_DOWN)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_z)
        self.menu1.highlight_option_on_givenpos(pos_on_px_scale(pygame.mouse.get_pos()))
        self.menu1.interface.do_action_on_highlight()

    def draw(self, screen: pygame.Surface):
        draw_grid(screen, 16, (78, 78, 78))
        self.msgbox2.draw(screen)
        self.msgbox1.draw(screen)
        self.menu1.draw(screen)
        self.tutorial_msgbox.draw(screen)


scene_manager = SceneManager()
scene_manager.push(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager, fps=60)
