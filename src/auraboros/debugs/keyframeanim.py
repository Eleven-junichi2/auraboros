
# from collections import deque
from pathlib import Path
import sys
# from string import ascii_lowercase

import pygame

import init_for_dev  # noqa
from auraboros import engine, global_
from auraboros.animation import KeyframeAnimation, Keyframe
from auraboros.gametext import GameText, Font2
from auraboros.gamescene import Scene, SceneManager
from auraboros.gameinput import Keyboard
from auraboros.ui import GameMenuSystem, GameMenuUI, MsgWindow
from auraboros.utilities import AssetFilePath, draw_grid, pos_on_pixel_scale
from auraboros.schedule import Stopwatch
# from auraboros import global_

engine.init(caption="Test Animation System")

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(
    Font2(AssetFilePath.font("misaki_gothic.ttf"), 16), "misakigothic")


class DebugScene(Scene):
    def setup(self):
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
            "play", self.play_animation, text="Play")
        self.menusystem.add_menu_item(
            "stop", self.stop_animation, text="STOP")
        self.menusystem.add_menu_item(
            "reset", self.reset_animation, text="RESET")
        self.menuui = GameMenuUI(self.menusystem, GameText.font, "filled_box")
        self.menuui.padding = 4
        self.msgbox = MsgWindow(GameText.font, "Press 'Z'")
        self.msgbox.padding = 4
        self.msgbox2 = MsgWindow(GameText.font)
        self.msgbox2.padding = 4
        self.msgbox3 = MsgWindow(GameText.font)
        self.msgbox3.padding = 4
        self.msgbox4 = MsgWindow(GameText.font)
        self.msgbox4.padding = 4
        self.msgbox5 = MsgWindow(GameText.font)
        self.msgbox5.padding = 4
        self.msgbox6 = MsgWindow(GameText.font)
        self.msgbox6.padding = 4
        self.msgbox7 = MsgWindow(GameText.font)
        self.msgbox7.padding = 4
        self.msgbox8 = MsgWindow(GameText.font)
        self.msgbox8.padding = 4
        self.msgbox9 = MsgWindow(GameText.font)
        self.msgbox9.padding = 4
        self.stopwatch = Stopwatch()
        self.mouse.register_mouseaction(
            "down",
            on_left=lambda: self.menuui.do_option_if_givenpos_on_ui(
                pos_on_pixel_scale(pygame.mouse.get_pos())))
        self.args_of_script_on_everyframe = None
        self.animation = KeyframeAnimation(
            self.script_on_everyframe,
            [Keyframe(0, [0, 0]),
             Keyframe(1000, [100, 25]),
                Keyframe(2000, [200, 200])])

    def script_on_everyframe(self, *args):
        self.args_of_script_on_everyframe = tuple(map(int, args))
        # if args[0] == 0.:
        #     print(self.stopwatch.read())

    def play_animation(self):
        # if not self.anim_textshowing.is_playing:
        # self.anim_textshowing.let_play()
        if not self.animation.is_playing:
            if self.animation.is_finished():
                self.stopwatch.reset()
            self.animation.let_play()
            self.stopwatch.start()

    def stop_animation(self):
        self.stopwatch.stop()
        self.animation.let_stop()

    def reset_animation(self):
        self.stopwatch.reset()
        self.animation.reset_animation()
        # self.anim_textshowing.reset_animation()

    def update(self, dt):
        self.animation.update(dt)
        # self.anim_textshowing.update(dt)
        if not self.animation.is_playing:
            if self.animation.is_finished():
                self.stopwatch.stop()
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_UP)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_DOWN)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_z)
        self.menuui.set_pos_to_center()
        self.menusystem.update()
        self.menuui.highlight_option_on_givenpos(
            pos_on_pixel_scale(pygame.mouse.get_pos()))
        self.msgbox2.text = \
            f"id of current frame:{self.animation.id_current_frame}"
        self.msgbox3.text = \
            f"id of next frame:{self.animation.id_current_frame+1}"
        self.msgbox4.rewrite_text(
            f"{self.args_of_script_on_everyframe}")
        self.msgbox5.rewrite_text(
            f"time:{self.animation.read_current_frame_progress()}")
        self.msgbox6.text = \
            f"elapsed time:{self.stopwatch.read()/1000}"
        self.msgbox7.rewrite_text(
            f"loop:{self.animation.finished_loop_counter}/" +
            f"{self.animation.loop_count}")
        self.msgbox8.rewrite_text(
            f"script_args:{[frame[1] for frame in self.animation.frames]}")
        self.msgbox9.rewrite_text(
            f"keytimes:{[frame[0] for frame in self.animation.frames]}")
        self.msgbox2.pos[1] = \
            self.msgbox.real_size[1]
        self.msgbox3.pos[1] = \
            self.msgbox.real_size[1] +\
            self.msgbox2.real_size[1]
        self.msgbox4.pos[1] = \
            self.msgbox.real_size[1] +\
            self.msgbox2.real_size[1] +\
            self.msgbox3.real_size[1]
        self.msgbox5.pos[1] = \
            self.msgbox.real_size[1] +\
            self.msgbox2.real_size[1] +\
            self.msgbox3.real_size[1] +\
            self.msgbox4.real_size[1]
        self.msgbox6.pos[1] = \
            self.msgbox.real_size[1] +\
            self.msgbox2.real_size[1] +\
            self.msgbox3.real_size[1] +\
            self.msgbox4.real_size[1] +\
            self.msgbox5.real_size[1]
        self.msgbox7.pos[1] = \
            self.msgbox.real_size[1] +\
            self.msgbox2.real_size[1] +\
            self.msgbox3.real_size[1] +\
            self.msgbox4.real_size[1] +\
            self.msgbox5.real_size[1] +\
            self.msgbox6.real_size[1]
        self.msgbox8.pos[1] = \
            global_.w_size[1] -\
            self.msgbox8.real_size[1] -\
            self.msgbox9.real_size[1]
        self.msgbox9.pos[1] = \
            global_.w_size[1] -\
            self.msgbox8.real_size[1]

    def draw(self, screen):
        draw_grid(screen, 16, (78, 78, 78))
        self.menuui.draw(screen)
        self.msgbox.draw(screen)
        self.msgbox2.draw(screen)
        self.msgbox3.draw(screen)
        self.msgbox4.draw(screen)
        self.msgbox5.draw(screen)
        self.msgbox6.draw(screen)
        self.msgbox7.draw(screen)
        self.msgbox8.draw(screen)
        self.msgbox9.draw(screen)


scene_manager = SceneManager()
scene_manager.push(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager, fps=60)
