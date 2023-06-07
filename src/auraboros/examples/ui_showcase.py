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
    Frame,
    Orientation,
    Padding,
    TextUI,
    TextButtonUI,
    FrameStyle,
    UIFlowLayout,
    # HighlightStyle,
)
from auraboros.utils.path import AssetFilePath

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
        padding=Padding(4),
        spacing=2,
        frame=Frame(FrameStyle.BORDER, 1),
    )
    menu.interface.add_option(
        Option(
            TextButtonUI(gametext=GameText("TextUI")),
            "TextUI",
            on_select=lambda: scenemanager.transition_to(0),
        )
    )
    menu.interface.add_option(
        Option(
            TextButtonUI(gametext=GameText("ButtonUI")),
            "ButtonUI",
            on_select=lambda: scenemanager.transition_to(1),
        )
    )
    menu.interface.add_option(
        Option(
            TextButtonUI(gametext=GameText("UIFlowLayout")),
            "UIFlowLayout",
            on_select=lambda: scenemanager.transition_to(2),
        )
    )
    menu.interface.add_option(
        Option(
            TextButtonUI(gametext=GameText("MenuUI")),
            "MenuUI",
            on_select=lambda: scenemanager.transition_to(3),
        )
    )
    menu.update_children_on_menu()
    menu.relocate_children()
    return menu


navbar_ui = build_navbar_ui()


class TextUIScene(Scene):
    def setup(self):
        self.uilayout = UIFlowLayout()
        self.uilayout.add_child(navbar_ui)

        self.textui1 = TextUI(
            GameText("TextUI Example", fg_color=pygame.Color(0, 255, 255))
        )
        self.uilayout.add_child(self.textui1)

        self.uilayout.relocate_children()

    def event(self, event: pygame.event.Event):
        self.uilayout.event(event)

    def draw(self, screen: pygame.surface.Surface):
        self.uilayout.draw(screen)


class TextButtonUIScene(Scene):
    def setup(self):
        self.uilayout = UIFlowLayout()
        self.uilayout.add_child(navbar_ui)

        btntext = "TextButtonUI Example"
        self.btnui1 = TextButtonUI(
            GameText(btntext),
            pos=[20, 20],
            padding=Padding(10),
            frame=Frame(FrameStyle.BORDER, width=1, radius=3),
            bg_color=pygame.Color(122, 122, 122),
        )

        def btnui1_on_press():
            self.btnui1.bg_color.update(78, 78, 78)
            self.btnui1.gametext.rewrite("Pressed!")

        def btnui1_on_release():
            self.btnui1.bg_color.update(122, 122, 122)
            self.btnui1.gametext.rewrite(btntext)

        self.btnui1.on_press = btnui1_on_press
        self.btnui1.on_release = btnui1_on_release

        self.uilayout.add_child(self.btnui1)
        self.uilayout.relocate_children()

    def event(self, event: pygame.event.Event):
        self.uilayout.event(event)

    def draw(self, screen: pygame.surface.Surface):
        self.uilayout.draw(screen)


class UIFlowLayoutScene(Scene):
    def setup(self):
        self.uilayout = UIFlowLayout()
        self.uilayout.add_child(navbar_ui)

        self.uiflowlayout1 = UIFlowLayout(
            spacing=10, padding=Padding(10), frame=Frame(FrameStyle.BORDER, 1)
        )
        self.uiflowlayout1.add_child(TextUI(GameText("child ui 1")))
        self.uiflowlayout1.add_child(TextUI(GameText("child ui 2")))
        self.uiflowlayout1.add_child(TextUI(GameText("child ui 3")))
        # self.uiflowlayout1.relocate_children()

        self.uilayout.add_child(self.uiflowlayout1)
        self.uilayout.relocate_children()

    def event(self, event: pygame.event.Event):
        self.uilayout.event(event)

    def draw(self, screen: pygame.surface.Surface):
        self.uilayout.draw(screen)


class MenuUIScene(Scene):
    def setup(self):
        self.uilayout = UIFlowLayout()
        self.uilayout.add_child(navbar_ui)

        self.menuui1 = MenuUI()
        self.menuui1.interface.add_option(
            Option(
                TextUI(GameText("child ui 1", fg_color=pygame.Color(144, 144, 144))),
                "child1",
            )
        )
        self.menuui1.interface.add_option(
            Option(
                TextUI(GameText("child ui 2", fg_color=pygame.Color(144, 144, 144))),
                "child2",
            )
        )
        self.menuui1.interface.add_option(
            Option(
                TextUI(GameText("child ui 3", fg_color=pygame.Color(144, 144, 144))),
                "child3",
            )
        )
        self.menuui1.update_children_on_menu()
        # self.menuui1.relocate_children()

        self.uilayout.add_child(self.menuui1)
        self.uilayout.relocate_children()

    def event(self, event: pygame.event.Event):
        self.uilayout.event(event)

    def draw(self, screen: pygame.surface.Surface):
        self.uilayout.draw(screen)


scenemanager.add(TextUIScene(scenemanager))
scenemanager.add(TextButtonUIScene(scenemanager))
scenemanager.add(UIFlowLayoutScene(scenemanager))
scenemanager.add(MenuUIScene(scenemanager))

if __name__ == "__main__":
    engine.run(scenemanager)
