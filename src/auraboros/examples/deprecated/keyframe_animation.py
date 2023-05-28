from pathlib import Path
import sys

import pygame

import setup_syspath  # noqa
from auraboros import engine
from auraboros.animation import KeyframeAnimation, Keyframe
from auraboros.gametext import GameText, Font2
from auraboros.gamescene import Scene, SceneManager
from auraboros.gameinput import Keyboard
from auraboros.oldold_ui import MenuUI, MsgBoxUI
from auraboros.utils.path import AssetFilePath
from auraboros.utils.surface import draw_grid
from auraboros.utils.coordinate import in_scaled_px, window_size
from auraboros.schedule import Stopwatch

engine.init(caption="Test Animation System")

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(Font2(AssetFilePath.font("misaki_gothic.ttf"), 16), "misakigothic")


class DebugScene(Scene):
    def setup(self):
        self.keyboard["menu"] = Keyboard()
        self.keyboard.set_current_setup("menu")
        self.menuui = MenuUI(GameText.font)
        self.menuui.interface.add_menuitem("play", self.play_animation, text="PLAY")
        self.menuui.interface.add_menuitem("stop", self.stop_animation, text="STOP")
        self.menuui.interface.add_menuitem("reset", self.reset_animation, text="RESET")
        self.keyboard["menu"].register_keyaction(
            pygame.K_UP, 0, 122, 122, self.menuui.interface.cursor_up
        )
        self.keyboard["menu"].register_keyaction(
            pygame.K_DOWN, 0, 122, 122, self.menuui.interface.cursor_down
        )
        self.keyboard["menu"].register_keyaction(
            pygame.K_z, 0, 122, 122, self.menuui.interface.do_selected_action
        )
        self.menuui.property.padding = 4
        self.menuui.property.set_pos_to_center()
        self.msgbox = MsgBoxUI(GameText.font, "Press 'Z'")
        self.msgbox.property.padding = 4
        self.msgbox2 = MsgBoxUI(GameText.font)
        self.msgbox2.property.padding = 4
        self.msgbox3 = MsgBoxUI(GameText.font)
        self.msgbox3.property.padding = 4
        self.msgbox4 = MsgBoxUI(GameText.font)
        self.msgbox4.property.padding = 4
        self.msgbox5 = MsgBoxUI(GameText.font)
        self.msgbox5.property.padding = 4
        self.msgbox6 = MsgBoxUI(GameText.font)
        self.msgbox6.property.padding = 4
        self.msgbox7 = MsgBoxUI(GameText.font)
        self.msgbox7.property.padding = 4
        self.msgbox8 = MsgBoxUI(GameText.font)
        self.msgbox8.property.padding = 4
        self.msgbox9 = MsgBoxUI(GameText.font)
        self.msgbox9.property.padding = 4
        self.stopwatch = Stopwatch()
        self.mouse.register_mouseaction(
            "down",
            on_left=lambda: self.menuui.interface.do_selected_action()
            if self.menuui.property.is_givenpos_on_ui(
                in_scaled_px(pygame.mouse.get_pos())
            )
            else None,
        )
        self.args_of_script_on_everyframe = None
        self.animation = KeyframeAnimation(
            self.script_on_everyframe,
            [
                Keyframe(0, [0, 0]),
                Keyframe(1000, [100, 25]),
                Keyframe(2000, [200, 200]),
            ],
        )

    def script_on_everyframe(self, *args):
        self.args_of_script_on_everyframe = tuple(map(int, args))

    def play_animation(self):
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

    def update(self, dt):
        self.animation.update(dt)
        if not self.animation.is_playing:
            if self.animation.is_finished():
                self.stopwatch.stop()
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_UP)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_DOWN)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_z)
        self.menuui.highlight_option_on_givenpos(
            in_scaled_px(pygame.mouse.get_pos())
        )
        self.msgbox2.property.rewrite_text(
            f"id of current frame:{self.animation.id_current_frame}"
        )
        self.msgbox3.property.rewrite_text(
            f"id of next frame:{self.animation.id_current_frame+1}"
        )
        self.msgbox4.property.rewrite_text(f"{self.args_of_script_on_everyframe}")
        self.msgbox5.property.rewrite_text(
            f"time:{self.animation.read_current_frame_progress()}"
        )
        self.msgbox6.property.rewrite_text(f"elapsed time:{self.stopwatch.read()/1000}")
        self.msgbox7.property.rewrite_text(
            f"loop:{self.animation.finished_loop_counter}/"
            + f"{self.animation.loop_count}"
        )
        self.msgbox8.property.rewrite_text(
            f"script_args:{[frame[1] for frame in self.animation.frames]}"
        )
        self.msgbox9.property.rewrite_text(
            f"keytimes:{[frame[0] for frame in self.animation.frames]}"
        )
        self.msgbox2.property.pos[1] = self.msgbox.property.real_size[1]
        self.msgbox3.property.pos[1] = (
            self.msgbox.property.real_size[1] + self.msgbox2.property.real_size[1]
        )
        self.msgbox4.property.pos[1] = (
            self.msgbox.property.real_size[1]
            + self.msgbox2.property.real_size[1]
            + self.msgbox3.property.real_size[1]
        )
        self.msgbox5.property.pos[1] = (
            self.msgbox.property.real_size[1]
            + self.msgbox2.property.real_size[1]
            + self.msgbox3.property.real_size[1]
            + self.msgbox4.property.real_size[1]
        )
        self.msgbox6.property.pos[1] = (
            self.msgbox.property.real_size[1]
            + self.msgbox2.property.real_size[1]
            + self.msgbox3.property.real_size[1]
            + self.msgbox4.property.real_size[1]
            + self.msgbox5.property.real_size[1]
        )
        self.msgbox7.property.pos[1] = (
            self.msgbox.property.real_size[1]
            + self.msgbox2.property.real_size[1]
            + self.msgbox3.property.real_size[1]
            + self.msgbox4.property.real_size[1]
            + self.msgbox5.property.real_size[1]
            + self.msgbox6.property.real_size[1]
        )
        self.msgbox8.property.pos[1] = (
            window_size()[1]
            - self.msgbox8.property.real_size[1]
            - self.msgbox9.property.real_size[1]
        )
        self.msgbox9.property.pos[1] = (
            window_size()[1] - self.msgbox8.property.real_size[1]
        )

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
scene_manager.add(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager, fps=60)
