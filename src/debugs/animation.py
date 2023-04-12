
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
from auraboros.ui import GameMenuSystem, GameMenuUI, MsgWindow
from auraboros.animation import AnimationImage, SpriteSheet
from auraboros import global_

engine.init()

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

textfactory = TextSurfaceFactory()
textfactory.register_font(
    "misaki_gothic",
    pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16))


class TestSpriteIdle(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("testsprite.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 0, 32, 32),
            self.sprite_sheet.image_by_area(0, 32, 32, 32),
            self.sprite_sheet.image_by_area(0, 32*2, 32, 32),
            self.sprite_sheet.image_by_area(0, 32*3, 32, 32),
            self.sprite_sheet.image_by_area(0, 32*4, 32, 32),
            self.sprite_sheet.image_by_area(0, 32*3, 32, 32),
            self.sprite_sheet.image_by_area(0, 32*2, 32, 32),
            self.sprite_sheet.image_by_area(0, 32, 32, 32)]


class GameMenuDebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textfactory.set_current_font("misaki_gothic")
        self.testsprite_animimg = TestSpriteIdle()
        self.keyboard["menu"] = Keyboard()
        self.keyboard.set_current_setup("menu")
        self.menusystem = GameMenuSystem()
        self.keyboard["menu"].register_keyaction(
            pygame.K_UP, 0, 8, self.menusystem.menu_cursor_up)
        self.keyboard["menu"].register_keyaction(
            pygame.K_DOWN, 0, 8, self.menusystem.menu_cursor_down)
        self.keyboard["menu"].register_keyaction(
            pygame.K_z, 0, 0, self.menusystem.do_selected_action)
        self.menusystem.add_menu_item(
            "play", self.play_animation,
            lambda: self.msgwindow.rewrite_text("[]"),
            text="Play")
        self.menusystem.add_menu_item(
            "green", self.stop_animation,
            lambda: self.msgwindow.rewrite_text("|>"),
            text="STOP")
        self.menuui = GameMenuUI(self.menusystem, textfactory, "filled_box")
        self.menuui.padding = 4
        self.msgwindow = MsgWindow(textfactory.font())
        self.msgwindow.padding = 4
        self.msgwindow2 = MsgWindow(textfactory.font())
        self.msgwindow2.padding = 10
        self.msgwindow2.text = "Press 'Z' to Play/Stop"
        self.box_size = (24, 24)

    def play_animation(self):
        self.testsprite_animimg.let_play_animation()

    def stop_animation(self):
        self.testsprite_animimg.let_stop_animation()

    def turn_blue(self):
        self.box_color = (0, 0, 255)
        self.msgwindow.text = "Blue"

    def update(self, dt):
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_UP)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_DOWN)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_z)
        self.menuui.set_pos_to_center()
        self.msgwindow.set_x_to_center()
        self.msgwindow.pos[1] = global_.w_size[1]//3*2
        self.menusystem.update()
        self.testsprite_animimg.update(dt)

    def draw(self, screen):
        draw_grid_background(screen, 16, (78, 78, 78))
        # self.testsprite_animimg.draw(screen)
        screen.blit(self.testsprite_animimg.image, (100, 100))
        self.menuui.draw(screen)
        self.msgwindow.draw(screen)
        self.msgwindow2.draw(screen)


scene_manager = SceneManager()
scene_manager.push(GameMenuDebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
