import setup_syspath  # noqa
from auraboros import engine
from auraboros.gamescene import Scene, SceneManager

engine.init()


class HelloworldScene(Scene):
    pass


scene_manager = SceneManager()
scene_manager.push(HelloworldScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
