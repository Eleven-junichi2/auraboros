# from collections import deque
from pathlib import Path
import sys

# from string import ascii_lowercase

import pygame

import setup_syspath  # noqa
from auraboros import engine
from auraboros.gametext import GameText, Font2
from auraboros.gamescene import Scene, SceneManager
from auraboros.old_ui import MsgBoxUI
from auraboros.utils.path import AssetFilePath
from auraboros.utils.surface import draw_grid
from auraboros.utils.coordinate import window_size_in_scaled_px
from auraboros.animation import KeyframeAnimation, Keyframe

engine.init(caption="Test MsgBox", base_pixel_scale=2)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(
    Font2(AssetFilePath.font("PixelMPlus/PixelMplus12-Regular.ttf"), 24),
    "PixelMplus12Regular",
)


class DebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        GameText.use_font("PixelMplus12Regular")
        self.msgbox1 = MsgBoxUI(
            GameText.font,
            "abcdefg",
        )

        self.msgbox_anim_info = MsgBoxUI(GameText.font, "")

        def animate_msgbox1_text(x, y):
            self.msgbox_anim_info.property.rewrite_text(
                f"anim script args:{x, y}",
            )
            self.msgbox1.property.pos[0] = x
            self.msgbox1.property.pos[1] = y

        self.msgbox1_anim = KeyframeAnimation(
            animate_msgbox1_text,
            [
                Keyframe(0, [0, 0]),
                Keyframe(
                    10000,
                    [
                        window_size_in_scaled_px()[0]
                        - self.msgbox1.property.real_size[0],
                        window_size_in_scaled_px()[1]
                        - self.msgbox1.property.real_size[1],
                    ],
                ),
            ],
        )

        self.msgbox1_anim.let_play()

    def update(self, dt):
        self.msgbox1_anim.update(dt)

    def draw(self, screen: pygame.Surface):
        draw_grid(screen, 16, (78, 78, 78))
        self.msgbox1.draw(screen)
        self.msgbox_anim_info.draw(screen)


scene_manager = SceneManager()
scene_manager.add(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager, fps=60)
