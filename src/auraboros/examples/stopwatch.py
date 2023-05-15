# from collections import deque
from pathlib import Path
import sys

# from string import ascii_lowercase

import pygame

import setup_syspath  # noqa
from auraboros import engine
from auraboros.animation import AnimationImage, SpriteSheet
from auraboros.gametext import GameText, Font2
from auraboros.gamescene import Scene, SceneManager
from auraboros.gameinput import Keyboard
from auraboros.schedule import Stopwatch
from auraboros.utils.surface import draw_grid
from auraboros.utils.path import AssetFilePath
from auraboros.ui import MsgBoxUI, MenuUI

engine.init(caption="Test Stopwatch System", base_pixel_scale=3)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(Font2(AssetFilePath.font("misaki_gothic.ttf"), 16), "misakigothic")


class TestAnimImg(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("testsprite.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 0, 32, 32),
            self.sprite_sheet.image_by_area(0, 32, 32, 32),
            self.sprite_sheet.image_by_area(0, 32 * 2, 32, 32),
            self.sprite_sheet.image_by_area(0, 32 * 3, 32, 32),
            self.sprite_sheet.image_by_area(0, 32 * 4, 32, 32),
            self.sprite_sheet.image_by_area(0, 32 * 3, 32, 32),
            self.sprite_sheet.image_by_area(0, 32 * 2, 32, 32),
            self.sprite_sheet.image_by_area(0, 32, 32, 32),
        ]
        self.anim_interval = 1000
        self.loop_count = 1


class DebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stopwatch = Stopwatch()
        self.stopwatch.enable_pausing_time_count()
        self.menuui = MenuUI(GameText.font, option_highlight_style="filled-box")
        self.menuui.interface.add_menuitem("play", self.start_stopwatch, text="Play")
        self.menuui.interface.add_menuitem("stop", self.stop_stopwatch, text="STOP")
        self.menuui.interface.add_menuitem("reset", self.reset_stopwatch, text="RESET")
        self.menuui.property.padding = 4
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
        self.keyboard["menu"] = Keyboard()
        self.keyboard.set_current_setup("menu")
        self.keyboard["menu"].register_keyaction(
            pygame.K_UP, 0, 122, 122, self.menuui.interface.cursor_up
        )
        self.keyboard["menu"].register_keyaction(
            pygame.K_DOWN, 0, 122, 122, self.menuui.interface.cursor_down
        )
        self.keyboard["menu"].register_keyaction(
            pygame.K_z, 0, 0, 0, self.menuui.interface.do_selected_action
        )

    def start_stopwatch(self):
        self.stopwatch.start()

    def stop_stopwatch(self):
        self.stopwatch.stop()

    def reset_stopwatch(self):
        self.stopwatch.reset()

    def update(self, dt):
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_UP)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_DOWN)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_z)
        self.menuui.property.set_pos_to_center()
        self.msgbox2.property.rewrite_text(
            f"1 elapsed time:{self.stopwatch.read()/1000}"
        )
        self.msgbox3.property.rewrite_text(
            f"1 pausing time:{self.stopwatch.read_pausing()/1000}"
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
            self.msgbox.property.real_size[1]
            + self.msgbox2.property.real_size[1]
            + self.msgbox3.property.real_size[1]
            + self.msgbox4.property.real_size[1]
            + self.msgbox5.property.real_size[1]
            + self.msgbox6.property.real_size[1]
            + self.msgbox7.property.real_size[1]
        )

    def draw(self, screen):
        draw_grid(screen, 16, (78, 78, 78))
        self.menuui.draw(screen)
        self.msgbox.draw(screen)
        self.msgbox2.draw(screen)
        self.msgbox3.draw(screen)


scene_manager = SceneManager()
scene_manager.add(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager, fps=60)
