import pygame

from auraboros import engine
from auraboros.gamescene import Scene, SceneManager


engine.init(caption="Test scene transition", pixel_scale=1,
            set_mode_flags=pygame.DOUBLEBUF | pygame.OPENGL)


class TestSceneA(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("transition to 2")
        self.manager.transition_to(2)
        print("this is scene A (setup)")

    def setup(self):
        print("this is scene A (setup)")


class TestSceneB(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("this is scene B (__init__)")

    def setup(self):
        print("this is scene B (setup)")


class TestSceneC(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager.transition_to(1)
        print("this is scene C (__init__)")

    def setup(self):
        print("this is scene C (setup)")


scene_manager = SceneManager()
scene_manager.push(TestSceneA(scene_manager))
scene_manager.push(TestSceneB(scene_manager))
scene_manager.push(TestSceneC(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager)
