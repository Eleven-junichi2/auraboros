from dataclasses import dataclass
from typing import Any, Callable

import pygame

from .core import Global
# from .animation import AnimationImage
# from .gameinput import KeyboardManager, Mouse


@dataclass
class State:
    script: Callable


class StateMachine:
    def __init__(self):
        self.states: dict[str, State] = {}
        self.current_state_name: str = ""

    @property
    def current_state(self) -> State:
        return self.states[self.current_state_name]

    def add_state(self, name: str, state: State):
        self.states[name] = state

    def is_state_exist(self, name: str) -> bool:
        return name in self.states.keys()

    def is_current_state(self, name: str) -> bool:
        return self.current_state_name == name

    def trans_to(self, state_name: str):
        if self.is_state_exist(state_name):
            self.current_state_name = state_name

    def run_script_on_state(self) -> Any:
        return self.current_state.script()


class Scene:
    """
    Examples:
        class ExampleScene(Scene):
            def setup(self):
                """"use instead of __init__""""

            def event(self, event: pygame.event.Event):
                pass

            def update(self):
                pass

            def draw(self):
                pass
    """

    def __init__(self, manager: "SceneManager"):
        self.manager = manager
        self.statemachine: StateMachine = StateMachine()
        self._is_setup_finished = False  # turn True by SceneManager

    def setup(self):
        """
        This method is called on scene transitions
        or if this scene is the first scene.
        """
        pass

    def event(self, event: pygame.event.Event):
        pass

    def draw(self, screen: pygame.surface.Surface):
        pass

    def update(self, dt):
        pass


class SceneManager:
    def __init__(self):
        self.scenes: list[Scene] = []
        self._current: int = 0  # -1 means exit app
        self.__is_finished_setup_of_first_scene = False

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, value):
        self._current = value

    def event(self, event: pygame.event.Event) -> bool:
        """return False to notify whether quit event is fired"""
        if event.type == pygame.QUIT:
            return False
        if self.current == -1:
            return False
        if self.scenes == []:
            return True
        if not self.scenes[self.current]._is_setup_finished:
            return True
        self.scenes[self.current].event(event)
        return True

    def update(self, dt):
        if self.scenes == []:
            return
        if not self.__is_finished_setup_of_first_scene:
            if Global.is_initialized:
                self.scenes[0].setup()
                self.__is_finished_setup_of_first_scene = True
                self.scenes[0]._is_setup_finished = True
        self.scenes[self.current].update(dt)

    def draw(self, screen: pygame.surface.Surface):
        if self.scenes == []:
            return
        self.scenes[self.current].draw(screen)

    def add(self, scene: Scene):
        self.scenes.append(scene)

    def pop(self):
        self.scenes.pop()

    def transition_to(self, index: int):
        self.current = index
        self.scenes[self.current].setup()
        self.scenes[self.current]._is_setup_finished = True
