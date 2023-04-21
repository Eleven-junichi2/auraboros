from pathlib import Path
from random import randint
import sys

import pygame

import init_for_dev  # noqa
from auraboros import engine
from auraboros.gametext import TextSurfaceFactory
from auraboros.gamescene import Scene, SceneManager
from auraboros.utilities import AssetFilePath, draw_grid, pos_on_pixel_scale
from auraboros.gamecamera import TopDownCamera
from auraboros.gameinput import Keyboard
from auraboros.ui import MsgWindow
from auraboros import global_

engine.init(caption="Test Mouse System", pixel_scale=2)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

textfactory = TextSurfaceFactory()
textfactory.register_font(
    "misaki_gothic",
    pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16))


class DebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas_surf = pygame.surface.Surface(global_.w_size)
        draw_grid(self.canvas_surf, 16, (78, 78, 78))
        self.canvas_surf.set_colorkey((0, 0, 0))
        textfactory.set_current_font("misaki_gothic")
        self.camera = TopDownCamera()
        self.keyboard["camera"] = Keyboard()
        self.keyboard["camera"].register_keyaction(
            pygame.K_LEFT, 0, 0, 0, self.camera.go_left_camera)
        self.keyboard["camera"].register_keyaction(
            pygame.K_UP, 0, 0, 0, self.camera.go_up_camera)
        self.keyboard["camera"].register_keyaction(
            pygame.K_RIGHT, 0, 0, 0, self.camera.go_right_camera)
        self.keyboard["camera"].register_keyaction(
            pygame.K_DOWN, 0, 0, 0, self.camera.go_down_camera)
        self.keyboard.set_current_setup("camera")
        self.mouse.register_mouseaction("down", on_left=self.paint_canvas)
        self.mouse.register_mouseaction("motion", on_left=self.paint_canvas)
        self.mouse.register_mouseaction("down", on_right=self.erase_canvas)
        self.mouse.register_mouseaction("motion", on_right=self.erase_canvas)
        self.mouse.register_mouseaction("drag", on_middle=self.drag_canvas)
        self.msgbox = MsgWindow(textfactory.font())
        self.msgbox.padding = 2
        self.msgbox.text = "Click to paint | Drag to move canvas"
        textfactory.register_text(
            "mouse_pos", pos=(0, self.msgbox.calculate_ultimate_size()[1]))
        textfactory.register_text(
            "mouse_pressed", pos=(0, self.msgbox.calculate_ultimate_size()[1]
                                  + textfactory.font().get_height()))

    def paint_canvas(self):
        camera_offset = self.camera.offset
        mouse_pos = pos_on_pixel_scale(pygame.mouse.get_pos())
        pos = map(sum, zip(mouse_pos, camera_offset))
        pygame.draw.rect(
            self.canvas_surf,
            (randint(0, 255), randint(0, 255), randint(0, 255)),
            (*pos, 2, 2), 2)

    def drag_canvas(self, drag_pos):
        self.camera.offset_x -= drag_pos[0] - \
            self.mouse.pos_prev_drag["middle"][0]
        self.camera.offset_y -= drag_pos[1] - \
            self.mouse.pos_prev_drag["middle"][1]

    def erase_canvas(self):
        camera_offset = self.camera.offset
        mouse_pos = map(lambda num: num//global_.PIXEL_SCALE,
                        pygame.mouse.get_pos())
        pos = map(sum, zip(mouse_pos, camera_offset))
        pygame.draw.rect(
            self.canvas_surf,
            (0, 0, 0),
            (*pos, 2, 2), 2)

    def update(self, dt):
        textfactory.rewrite_text("mouse_pos",
                                 text=f"{pygame.mouse.get_pos()}")
        textfactory.rewrite_text("mouse_pressed",
                                 text=f"{pygame.mouse.get_pressed()}")
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_LEFT)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_UP)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_RIGHT)
        self.keyboard.current_setup.do_action_on_keyinput(pygame.K_DOWN)

    def draw(self, screen):
        # screen.blit(self.canvas_surf, (0, 0))
        self.camera.projection_on_screen(
            screen, self.canvas_surf, global_.w_size)
        self.msgbox.draw(screen)
        textfactory.render("mouse_pos", screen)
        textfactory.render("mouse_pressed", screen)


scene_manager = SceneManager()
scene_manager.push(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager, fps=60)
