from pathlib import Path
from random import randint
import sys

import pygame

import setup_syspath  # noqa
from auraboros import engine
from auraboros.gametext import GameText, Font2
from auraboros.gamescene import Scene, SceneManager
from auraboros.gamecamera import TopDownCamera
from auraboros.gameinput import Keyboard
from auraboros.ui import MsgBoxUI
from auraboros.utils.path import AssetFilePath
from auraboros.utils.surface import draw_grid
from auraboros.utils.coordinate import in_scaled_px, window_size

engine.init(caption="Test Mouse System", base_pixel_scale=2)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

GameText.setup_font(Font2(AssetFilePath.font("misaki_gothic.ttf"), 16), "misakigothic")


class DebugScene(Scene):
    def setup(self):
        self.canvas_surf = pygame.surface.Surface(window_size())
        draw_grid(self.canvas_surf, 16, (78, 78, 78))
        self.canvas_surf.set_colorkey((0, 0, 0))
        self.camera = TopDownCamera()
        self.keyboard["camera"] = Keyboard()
        self.keyboard["camera"].register_keyaction(
            pygame.K_LEFT, 0, 0, 0, self.camera.go_left_camera
        )
        self.keyboard["camera"].register_keyaction(
            pygame.K_UP, 0, 0, 0, self.camera.go_up_camera
        )
        self.keyboard["camera"].register_keyaction(
            pygame.K_RIGHT, 0, 0, 0, self.camera.go_right_camera
        )
        self.keyboard["camera"].register_keyaction(
            pygame.K_DOWN, 0, 0, 0, self.camera.go_down_camera
        )
        self.keyboard.set_current_setup("camera")
        self.mouse.register_mouseaction("down", on_left=self.paint_canvas)
        self.mouse.register_mouseaction("motion", on_left=self.paint_canvas)
        self.mouse.register_mouseaction("down", on_right=self.erase_canvas)
        self.mouse.register_mouseaction("motion", on_right=self.erase_canvas)
        self.mouse.register_mouseaction("drag", on_middle=self.drag_canvas)
        self.msgbox = MsgBoxUI(GameText.font)
        self.msgbox.property.padding = 2
        self.msgbox.property.rewrite_text(
            "Click to paint | Click wheel and drag to move canvas"
        )
        self.text_to_show_param1 = GameText("", (0, self.msgbox.property.real_size[1]))
        self.text_to_show_param2 = GameText(
            "", (0, self.msgbox.property.real_size[1] + GameText.font.get_height())
        )

    def paint_canvas(self):
        camera_offset = self.camera.offset
        mouse_pos = in_scaled_px(pygame.mouse.get_pos())
        pos = map(sum, zip(mouse_pos, camera_offset))
        pygame.draw.rect(
            self.canvas_surf,
            (randint(0, 255), randint(0, 255), randint(0, 255)),
            (*pos, 2, 2),
            2,
        )

    def drag_canvas(self, drag_pos):
        self.camera.offset_x -= drag_pos[0] - self.mouse.pos_prev_drag["middle"][0]
        self.camera.offset_y -= drag_pos[1] - self.mouse.pos_prev_drag["middle"][1]

    def erase_canvas(self):
        camera_offset = self.camera.offset
        mouse_pos = in_scaled_px(pygame.mouse.get_pos())
        pos = map(sum, zip(mouse_pos, camera_offset))
        pygame.draw.rect(self.canvas_surf, (0, 0, 0), (*pos, 2, 2), 2)

    def update(self, dt):
        self.text_to_show_param1.rewrite(f"mouse_pos:{pygame.mouse.get_pos()}")
        self.text_to_show_param2.rewrite(f"mouse_pressed:{pygame.mouse.get_pressed()}")
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_LEFT)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_UP)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_RIGHT)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_DOWN)

    def draw(self, screen):
        # screen.blit(self.canvas_surf, (0, 0))
        self.camera.projection_on_screen(screen, self.canvas_surf, window_size())
        self.msgbox.draw(screen)
        self.text_to_show_param1.render(screen)
        self.text_to_show_param2.render(screen)


scene_manager = SceneManager()
scene_manager.add(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager, fps=60)
