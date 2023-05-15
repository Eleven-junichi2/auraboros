from pathlib import Path

# from array import array
import sys

import pygame

# import moderngl

import setup_syspath  # noqa
from auraboros import engine
from auraboros.gamescene import Scene, SceneManager
from auraboros.shader import Shader2D, VERTEX_DEFAULT
from auraboros.utils.path import AssetFilePath
from auraboros.utils.surface import draw_grid

engine.init(base_pixel_scale=1, display_set_mode_flags=pygame.DOUBLEBUF | pygame.OPENGL)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")


class DebugScene(Scene):
    def setup(self):
        shader2d = Shader2D()
        with open(Path(sys.argv[0]).parent / "vignette.frag", "r") as f:
            vignette_frag = f.read()
        shader2d.compile_and_register_program(VERTEX_DEFAULT, vignette_frag, "vignette")
        shader2d.set_uniform("vignette", "radius", 0.67)
        shader2d.set_uniform("vignette", "softness", 0.33)

    def draw(self, screen):
        draw_grid(screen, 32, (178, 178, 178))


scene_manager = SceneManager()
scene_manager.add(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
