import setup_syspath  # noqa

from pathlib import Path
import sys

import pygame

from auraboros import engine
from auraboros.gamescene import SceneManager, Scene
from auraboros.gametext import Font2, GameText
from auraboros.ui import (
    MenuUI,
    Option,
    Orientation,
    TextUI,
    ButtonUI,
    FrameStyle,
    UIFlowLayout,
    HighlightStyle,
)
from auraboros.utils.path import AssetFilePath
from auraboros.utils.coordinate import calc_pos_to_center

engine.init(caption="Hello, World!")

AssetFilePath.set_root_dir(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(
    Font2(AssetFilePath.get_asset("fonts/PixelMPlus/PixelMplus12-Regular.ttf"), 24),
    "PixelMPlus12-Regular",
)

scenemanager = SceneManager()


def build_navbar_ui() -> MenuUI:
    menu = MenuUI(
        orientation=Orientation.HORIZONTAL,
        padding=4,
        spacing=2,
        frame_style=FrameStyle.BORDER,
    )
    menu.interface.add_option(
        Option(
            ButtonUI(gametext=GameText("TextUI")),
            "TextUI",
            on_select=lambda: scenemanager.transition_to(0),
        )
    )
    menu.interface.add_option(
        Option(
            ButtonUI(gametext=GameText("ButtonUI")),
            "ButtonUI",
            on_select=lambda: scenemanager.transition_to(1),
        )
    )
    menu.interface.add_option(
        Option(
            ButtonUI(gametext=GameText("MenuUI")),
            "MenuUI",
            on_select=lambda: scenemanager.transition_to(2),
        )
    )
    menu.update_children_on_menu()
    menu.reposition_children()
    return menu


navbar_ui = build_navbar_ui()


class TextUIScene(Scene):
    def setup(self):
        self.uilayout = UIFlowLayout()
        self.uilayout.add_child(navbar_ui)

        self.textui_example = TextUI(GameText("Example of TextUI"))
        self.uilayout.add_child(self.textui_example)

        self.uilayout.reposition_children()

    def event(self, event: pygame.event.Event):
        self.uilayout.event(event)

    def draw(self, screen: pygame.surface.Surface):
        self.uilayout.draw(screen)


class ButtonUIScene(Scene):
    def setup(self):
        self.uilayout = UIFlowLayout()
        self.uilayout.add_child(navbar_ui)

        def show_pressed(ui: ButtonUI):
            ui.parts.gametext.rewrite("Pressed!")

        self.btnui_example = ButtonUI(
            GameText("Example of Button UI"),
            on_press=lambda: show_pressed(self.btnui_example),
        )
        self.btnui_example.parts.pos = calc_pos_to_center(
            self.btnui_example.parts.real_size
        )
        self.uilayout.add_child(self.btnui_example)

        self.uilayout.reposition_children()

    def event(self, event: pygame.event.Event):
        self.uilayout.event(event)

    def draw(self, screen: pygame.surface.Surface):
        self.uilayout.draw(screen)


class MenuUIScene(Scene):
    def setup(self):
        self.uilayout = UIFlowLayout()
        self.uilayout.add_child(navbar_ui)
        self.menuui = MenuUI(
            padding=10,
            spacing=10,
            frame_style=FrameStyle.BORDER,
            highlight_style=HighlightStyle.FILL_BG,
            highlight_bg_color=pygame.Color("#1086b8"),
        )
        self.uilayout.add_child(self.menuui)
        self.uilayout.reposition_children()
        self.menuui.interface.add_option(
            Option(
                ButtonUI(
                    GameText("HighlightStyle.CURSOR", color_foreground=(89, 89, 89))
                ),
                "option1",
                on_select=lambda: setattr(
                    self.menuui.parts, "highlight_style", HighlightStyle.CURSOR
                ),
            )
        )
        self.menuui.interface.add_option(
            Option(
                ButtonUI(
                    GameText("HighlightStyle.FRAME_BG", color_foreground=(89, 89, 89))
                ),
                "option2",
                on_select=lambda: setattr(
                    self.menuui.parts, "highlight_style", HighlightStyle.FRAME_BG
                ),
            ),
        )
        self.menuui.interface.add_option(
            Option(
                ButtonUI(
                    GameText("HighlightStyle.FILL_BG", color_foreground=(89, 89, 89))
                ),
                "option3",
                on_select=lambda: setattr(
                    self.menuui.parts, "highlight_style", HighlightStyle.FILL_BG
                ),
            ),
        )
        self.menuui.interface.add_option(
            Option(
                ButtonUI(
                    GameText(
                        "HighlightStyle.RECOLOR_GAMETEXT_FG",
                        color_foreground=(89, 89, 89),
                    )
                ),
                "option4",
                on_select=lambda: setattr(
                    self.menuui.parts,
                    "highlight_style",
                    HighlightStyle.RECOLOR_GAMETEXT_FG,
                ),
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
        self.menuui.keyboard.register_keyaction(
            pygame.K_z, 0, 78, 122, keydown=self.menuui.interface.do_func_on_select
        )
        self.current_highlight_style_display_ui = TextUI(GameText(""))
        self.uilayout.add_child(self.current_highlight_style_display_ui)
        self.uilayout.reposition_children()

    def event(self, event: pygame.event.Event):
        self.uilayout.event(event)

    def update(self, dt):
        self.current_highlight_style_display_ui.parts.gametext.rewrite(
            f"Current Highlight Style: {self.menuui.parts.highlight_style}"
        )
        self.menuui.keyboard.do_action_on_keyinput(pygame.K_UP)
        self.menuui.keyboard.do_action_on_keyinput(pygame.K_DOWN)
        self.menuui.keyboard.do_action_on_keyinput(pygame.K_z)

    def draw(self, screen: pygame.surface.Surface):
        self.uilayout.draw(screen)


scenemanager.add(TextUIScene(scenemanager))
scenemanager.add(ButtonUIScene(scenemanager))
scenemanager.add(MenuUIScene(scenemanager))

if __name__ == "__main__":
    engine.run(scenemanager)
