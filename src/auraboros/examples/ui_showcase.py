import setup_syspath  # noqa

from pathlib import Path
import sys

import pygame

from auraboros import engine
from auraboros.gamescene import SceneManager, Scene
from auraboros.gametext import Font2, GameText
from auraboros.ui import MenuUI, Option, TextUI, ButtonUI
from auraboros.utils.path import AssetFilePath
from auraboros.utils.coordinate import calc_pos_to_center

engine.init(caption="Hello, World!")

AssetFilePath.set_root_dir(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(
    Font2(AssetFilePath.get_asset("fonts/PixelMPlus/PixelMplus12-Regular.ttf"), 24),
    "PixelMPlus12-Regular",
)


class TextUIScene(Scene):
    def setup(self):
        self.textui_example = TextUI(GameText("Example of TextUI"))

    def draw(self, screen: pygame.surface.Surface):
        self.textui_example.draw(screen)


class ButtonUIScene(Scene):
    def setup(self):
        def show_pressed(ui: ButtonUI):
            ui.parts.gametext.rewrite("Pressed!")

        self.btnui_example = ButtonUI(
            GameText("Example of Button UI"),
            on_press=lambda: show_pressed(self.btnui_example),
        )
        self.btnui_example.parts.pos = calc_pos_to_center(
            self.btnui_example.parts.real_size
        )

    def event(self, event: pygame.event.Event):
        self.btnui_example.event(event)

    def draw(self, screen: pygame.surface.Surface):
        self.btnui_example.draw(screen)


class MenuUIScene(Scene):
    def setup(self):
        # TODO: make button event on mouse cursor
        self.menuui = MenuUI(padding=10, spacing=10)
        btn1 = ButtonUI(GameText("Option1"))
        self.menuui.interface.add_option(
            Option(
                btn1,
                "option1",
                on_select=lambda: btn1.parts.gametext.rewrite("Option1 was selected")
            )
        )
        btn2 = ButtonUI(GameText("Option2"))
        self.menuui.interface.add_option(
            Option(
                btn2,
                "option2",
                on_select=lambda: btn2.parts.gametext.rewrite("Option2 was selected")
            ),
        )
        self.menuui.update_children_on_menu()
        self.menuui.reposition_children()
        self.menuui.keyboard.register_keyaction(
            pygame.K_UP, 0, 78, 122, keydown=self.menuui.interface.up_cursor
        )
        self.menuui.keyboard.register_keyaction(
            pygame.K_DOWN, 0, 78, 122, keydown=self.menuui.interface.down_cursor
        )

    def event(self, event: pygame.event.Event):
        self.menuui.event(event)

    def update(self, dt):
        self.menuui.keyboard.do_action_on_keyinput(pygame.K_UP)
        self.menuui.keyboard.do_action_on_keyinput(pygame.K_DOWN)

    def draw(self, screen: pygame.surface.Surface):
        self.menuui.draw(screen)


scenemanager = SceneManager()
scenemanager.add(MenuUIScene(scenemanager))

if __name__ == "__main__":
    engine.run(scenemanager)
