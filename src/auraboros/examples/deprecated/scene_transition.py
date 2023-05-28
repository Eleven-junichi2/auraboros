import setup_syspath  # noqa
from auraboros import engine
from auraboros.gamescene import Scene, SceneManager


engine.init(caption="Test scene transition")


class TestSceneA(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("this is scene A (__init__)")
        self.is_transition_done = False

    def setup(self):
        print("this is scene A (setup)")
        print("transition to 2 (C)")
        if not self.is_transition_done:
            self.is_transition_done = True
            self.manager.transition_to(2)


class TestSceneB(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("this is scene B (__init__)")

    def setup(self):
        print("this is scene B (setup)")
        print("transition to 0 (A)")
        self.dammy = False
        self.manager.transition_to(0)


class TestSceneC(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("this is scene C (__init__)")

    def setup(self):
        print("this is scene C (setup)")
        print("transition to 0 (B)")
        self.manager.transition_to(1)


scene_manager = SceneManager()
scene_manager.add(TestSceneA(scene_manager))
scene_manager.add(TestSceneB(scene_manager))
scene_manager.add(TestSceneC(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager)
