from pathlib import Path
import sys

import pygame

import init_for_dev  # noqa
from auraboros import engine
from auraboros import global_
from auraboros.gamescene import Scene, SceneManager
from auraboros.entity import Entity
from auraboros.utilities import AssetFilePath, draw_grid_background
from auraboros.animation import AnimationImage, SpriteSheet, AnimationDict
from auraboros.gameinput import Keyboard

engine.init(pixel_scale=1)

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")


class EntityIdle(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("testsprite.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 0, 32, 32),
            self.sprite_sheet.image_by_area(0, 32, 32, 32),
            self.sprite_sheet.image_by_area(0, 32*2, 32, 32),
            self.sprite_sheet.image_by_area(0, 32*3, 32, 32),
            self.sprite_sheet.image_by_area(0, 32*4, 32, 32),
            self.sprite_sheet.image_by_area(0, 32*3, 32, 32),
            self.sprite_sheet.image_by_area(0, 32*2, 32, 32),
            self.sprite_sheet.image_by_area(0, 32, 32, 32)]
        self.anim_interval = 500
        self.loop_count = 2


class TestEntity(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation = AnimationDict()
        self.animation["idle"] = EntityIdle()
        self.image = self.animation["idle"].image
        self.rect = self.image.get_rect()


class DebugScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.testentity = TestEntity()
        self.testentity.x = global_.w_size[0] // 2 - \
            self.testentity.image.get_rect().width//2
        self.testentity.y = global_.w_size[1] // 2 - \
            self.testentity.image.get_rect().height//2
        self.keyboard["player"] = Keyboard()

    def draw(self, screen):
        draw_grid_background(screen, 32, (178, 178, 178))
        self.testentity.draw(screen)


scene_manager = SceneManager()
scene_manager.push(DebugScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
