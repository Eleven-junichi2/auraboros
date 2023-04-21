

# from collections import deque
from pathlib import Path
import sys
# from string import ascii_lowercase

import pygame

import init_for_dev  # noqa
from auraboros import engine
from auraboros.gametext import TextSurfaceFactory
from auraboros.gamescene import Scene, SceneManager
from auraboros.utilities import AssetFilePath, draw_grid
from auraboros.gameinput import Mouse
from auraboros import global_
# from auraboros.global_ import _fix_dislodge_between_givenpos_and_drawpos

engine.init(caption="Test Mouse System", pixel_scale=2)
# issue: dislodge coordinate to paint if pixel_scale=2

# pygame.mouse.get_pos = _fix_dislodge_between_givenpos_and_drawpos(
#             pygame.mouse.get_pos, pixel_scale=2)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

textfactory = TextSurfaceFactory()
textfactory.register_font(
    "misaki_gothic",
    pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16))


class DebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textfactory.set_current_font("misaki_gothic")
        textfactory.register_text("mouse_pos", pos=(0, 0))
        self.mouse = Mouse()
        self.mouse.register_mouseaction("down", on_left=self.paint)
        self.canvas_surf = pygame.surface.Surface(global_.w_size)
        draw_grid(self.canvas_surf, 16, (78, 78, 78))

    def paint(self):
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.rect(
            self.canvas_surf, (255, 255, 255), (*mouse_pos, 4, 4), 1)

    def event(self, event):
        self.mouse.event(event)

    def update(self, dt):
        textfactory.rewrite_text("mouse_pos", text=f"{pygame.mouse.get_pos()}")

    def draw(self, screen):
        screen.blit(self.canvas_surf, (0, 0))
        textfactory.render("mouse_pos", screen)


scene_manager = SceneManager()
scene_manager.push(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager, fps=60)
