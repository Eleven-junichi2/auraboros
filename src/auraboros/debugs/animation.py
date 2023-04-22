
# from collections import deque
from pathlib import Path
from random import randint
import sys
# from string import ascii_lowercase

import pygame

import init_for_dev  # noqa
from auraboros import engine, global_
from auraboros.animation import Animation, AnimFrameProgram, AnimFrame
from auraboros.gametext import TextSurfaceFactory
from auraboros.gamescene import Scene, SceneManager
from auraboros.gameinput import Keyboard
from auraboros.ui import GameMenuSystem, GameMenuUI, MsgWindow
from auraboros.utilities import AssetFilePath, draw_grid, pos_on_pixel_scale
from auraboros.schedule import Stopwatch
# from auraboros import global_

engine.init(caption="Test AnimationImage System")

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

textfactory = TextSurfaceFactory()
textfactory.register_font(
    "misaki_gothic",
    pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16))


class DebugScene(Scene):
    def setup(self):
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
            "play", self.play_animation, text="Play")
        self.menusystem.add_menu_item(
            "stop", self.stop_animation, text="STOP")
        self.menusystem.add_menu_item(
            "reset", self.reset_animation, text="RESET")
        self.menuui = GameMenuUI(self.menusystem, textfactory, "filled_box")
        self.menuui.padding = 4
        self.msgbox = MsgWindow(textfactory.font())
        self.msgbox.padding = 4
        self.msgbox.text = "Press 'Z'"
        self.msgbox2 = MsgWindow(textfactory.font())
        self.msgbox2.padding = 4
        self.msgbox3 = MsgWindow(textfactory.font())
        self.msgbox3.padding = 4
        self.msgbox4 = MsgWindow(textfactory.font())
        self.msgbox4.padding = 4
        self.msgbox5 = MsgWindow(textfactory.font())
        self.msgbox5.padding = 4
        self.msgbox6 = MsgWindow(textfactory.font())
        self.msgbox6.padding = 4
        self.msgbox7 = MsgWindow(textfactory.font())
        self.msgbox7.padding = 4
        self.msgbox8 = MsgWindow(textfactory.font())
        self.msgbox8.padding = 4
        self.msgbox9 = MsgWindow(textfactory.font())
        self.msgbox9.padding = 4
        self.stopwatch = Stopwatch()
        self.mouse.register_mouseaction(
            "down",
            on_left=lambda: self.menuui.do_option_if_givenpos_on_ui(
                pos_on_pixel_scale(pygame.mouse.get_pos())))

        class TextAddRandIntProgram(AnimFrameProgram):
            @staticmethod
            def script():
                self.msgbox2.text += str(randint(0, 9))

            @staticmethod
            def reset():
                self.msgbox2.text = ""

        self.anim_textshowing = Animation(
            [AnimFrame(TextAddRandIntProgram, 1000, 1000) for _ in range(3)]
        )

    def play_animation(self):
        if not self.anim_textshowing.is_playing:
            self.anim_textshowing.let_play()
            self.stopwatch.start()
        if self.anim_textshowing.is_all_loop_finished():
            self.stopwatch.reset()

    def stop_animation(self):
        self.stopwatch.stop()
        self.anim_textshowing.let_stop()

    def reset_animation(self):
        self.stopwatch.reset()
        self.anim_textshowing.reset_animation()

    def update(self, dt):
        self.anim_textshowing.update(dt)
        if not self.anim_textshowing.is_playing:
            if self.anim_textshowing.is_all_loop_finished():
                self.stopwatch.stop()
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_UP)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_DOWN)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_z)
        self.menuui.set_pos_to_center()
        self.menusystem.update()
        self.menuui.highlight_option_on_givenpos(
            pos_on_pixel_scale(pygame.mouse.get_pos()))
        self.msgbox3.text = \
            f"id of current frame:{self.anim_textshowing.id_current_frame}"
        self.msgbox4.text = \
            f"frame count:{self.anim_textshowing.frame_count}"
        self.msgbox5.text = \
            f"elapsed time:{self.stopwatch.read()/1000}"
        self.msgbox6.text = \
            f"pausing time:{self.stopwatch.read_pausing()/1000}"
        self.msgbox7.text = \
            "delay + interval:" + str(
                list(map(sum, zip(
                    [frame.delay for frame in self.anim_textshowing.frames],
                    [frame.interval for frame in self.anim_textshowing.frames]
                ))))
        self.msgbox8.text = \
            "delay:" + str(
                [frame.delay for frame in self.anim_textshowing.frames])
        self.msgbox9.text = \
            "interval:" + str(
                [frame.interval for frame in self.anim_textshowing.frames])
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
            global_.w_size[1] -\
            self.msgbox7.real_size[1] -\
            self.msgbox8.real_size[1] -\
            self.msgbox9.real_size[1]
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
