
# from collections import deque
from pathlib import Path
import sys
# from string import ascii_lowercase

import pygame

import init_for_dev  # noqa
from auraboros import engine, global_
from auraboros.gametext import TextSurfaceFactory, Font2
from auraboros.gamescene import Scene, SceneManager
from auraboros.ui import MsgWindow
from auraboros.utilities import AssetFilePath, draw_grid, pos_on_pixel_scale

engine.init(caption="Test Font2.renderln", pixel_scale=2)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

textfactory = TextSurfaceFactory()
textfactory.register_font(
    "misaki_gothic",
    pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16))


class DebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textfactory.set_current_font("misaki_gothic")
        self.msgbox = MsgWindow(
            textfactory.font(), "frame_width=4", "fixed", frame_width=4)
        self.msgbox.padding = 4
        self.msgbox.size[0] = global_.w_size[0]*0.95
        self.msgbox.size[1] = global_.w_size[1]*0.22
        self.msgbox.pos[1] = global_.w_size[1]*0.975 - self.msgbox.real_size[1]
        self.msgbox.set_x_to_center()

        self.msgbox2 = MsgWindow(
            textfactory.font(),
            ["click or down up to next | (text 1)",
             "(text 2)",
             "wheel up to back | (text 3)"], "fixed")
        self.msgbox2.padding = 4
        self.msgbox2.size[0] = global_.w_size[0]*0.95
        self.msgbox2.size[1] = global_.w_size[1]*0.22
        self.msgbox2.pos[1] = self.msgbox.pos[1] * \
            0.95 - self.msgbox2.real_size[1]
        self.msgbox2.set_x_to_center()

        self.mouse.register_mouseaction(
            "down",
            on_left=lambda: self.msgbox2.do_func_if_pos_is_on_ui(
                pos_on_pixel_scale(pygame.mouse.get_pos()),
                lambda: self.msgbox2.change_text_to_next()))

        self.mouse.register_mouseaction(
            "down",
            on_wheel_down=lambda: self.msgbox2.do_func_if_pos_is_on_ui(
                pos_on_pixel_scale(pygame.mouse.get_pos()),
                lambda: self.msgbox2.change_text_to_next()),
            on_wheel_up=lambda: self.msgbox2.do_func_if_pos_is_on_ui(
                pos_on_pixel_scale(pygame.mouse.get_pos()),
                lambda: self.msgbox2.rewind_text()))
        self.font2 = Font2(AssetFilePath.font("misaki_gothic.ttf"), 16)
        self.font2_renderlned = self.font2.renderln(
            "This is multiline text!", True, (255, 255, 255),
            line_width_by_char_count=12)

    def draw(self, screen):
        draw_grid(screen, 16, (78, 78, 78))
        screen.blit(self.font2_renderlned, (0, 0))
        self.msgbox2.draw(screen)
        self.msgbox.draw(screen)


scene_manager = SceneManager()
scene_manager.push(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager, fps=60)
