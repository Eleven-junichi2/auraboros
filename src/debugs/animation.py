
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
from auraboros.animation2 import AnimationImage, SpriteSheet
from auraboros import global_

engine.init(caption="Test Animation System")

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

textfactory = TextSurfaceFactory()
textfactory.register_font(
    "misaki_gothic",
    pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16))


class TestAnimImg(AnimationImage):
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
        self.anim_interval = 500


class GameMenuDebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textfactory.set_current_font("misaki_gothic")
        self.test_anim_img = TestAnimImg()
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
            "stop", self.stop_animation,
            lambda: self.msgwindow.rewrite_text("|>"),
            text="STOP")
        self.menusystem.add_menu_item(
            "reset", self.reset_animation,
            text="RESET")
        self.menuui = GameMenuUI(self.menusystem, textfactory, "filled_box")
        self.menuui.padding = 4
        self.msgwindow = MsgWindow(textfactory.font())
        self.msgwindow.padding = 4
        self.msgwindow2 = MsgWindow(textfactory.font())
        self.msgwindow2.padding = 10
        self.msgwindow2.text = "Press 'Z'"
        self.anim_frame_id_msgbox = MsgWindow(textfactory.font())
        self.anim_frame_id_msgbox.padding = 10
        self.anim_frame_id_msgbox.pos[1] =\
            self.anim_frame_id_msgbox.calculate_ultimate_size()[1]
        self.is_playing_msgbox = MsgWindow(textfactory.font())
        self.is_playing_msgbox.padding = 10
        self.is_playing_msgbox.pos[1] =\
            self.is_playing_msgbox.calculate_ultimate_size()[1] * 2

    def play_animation(self):
        self.test_anim_img.let_play()

    def stop_animation(self):
        self.test_anim_img.let_stop()

    def reset_animation(self):
        self.test_anim_img.reset_animation()
        pass

    def update(self, ):
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_UP)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_DOWN)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_z)
        self.menuui.set_pos_to_center()
        self.msgwindow.set_x_to_center()
        self.msgwindow.pos[1] = global_.w_size[1]//3*2
        self.menusystem.update()
        # self.test_anim_img
        self.anim_frame_id_msgbox.text = \
            f"anim_frame_id:{self.test_anim_img.anim_frame_id}"
        # self.is_playing_msgbox.text = \
        #     f"is_playing:{self.test_anim_img.is_playing}"

    def draw(self, screen):
        draw_grid_background(screen, 16, (78, 78, 78))
        # self.test_anim_img.draw(screen)
        screen.blit(
            self.test_anim_img.image,
            (global_.w_size[0]//2-self.test_anim_img.image.get_width()//2,
             self.menuui.pos[1]-self.test_anim_img.image.get_height()))
        self.menuui.draw(screen)
        self.msgwindow.draw(screen)
        self.msgwindow2.draw(screen)
        self.anim_frame_id_msgbox.draw(screen)
        self.is_playing_msgbox.draw(screen)


scene_manager = SceneManager()
scene_manager.push(GameMenuDebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager, fps_num=60)