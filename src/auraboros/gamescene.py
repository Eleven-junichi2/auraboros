from dataclasses import dataclass
from typing import Any, Callable

import pygame

from .core import Global
from .animation import AnimationImage
from .gameinput import KeyboardManager, Mouse


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
    def __init__(self, manager: "SceneManager"):
        self.manager = manager
        self.statemachine: StateMachine = StateMachine()
        self.keyboard: KeyboardManager = KeyboardManager()
        self.mouse: Mouse = Mouse()
        self.visual_effects: list[AnimationImage] = []
        self._is_setup_finished = False  # turn True by SceneManager

    def setup(self):
        """
        This method is called on scene transitions
        or if this scene is the first scene.
        """
        pass

    def event(self, event: pygame.event):
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

    def event(self, event: pygame.event) -> bool:
        """return False as a signal of quit app"""
        if event.type == pygame.QUIT:
            return False
        if self.current == -1:
            return False
        if not self.scenes[self.current]._is_setup_finished:
            return True
        self.scenes[self.current].event(event)
        if self.scenes[self.current].keyboard.current_setup is not None:
            self.scenes[self.current].keyboard.current_setup.event(event)
        if self.scenes[self.current].mouse is not None:
            self.scenes[self.current].mouse.event(event)
        return True

    def update(self, dt):
        if not self.__is_finished_setup_of_first_scene:
            if Global.is_initialized:
                self.scenes[0].setup()
                self.__is_finished_setup_of_first_scene = True
                self.scenes[0]._is_setup_finished = True
        self.scenes[self.current].update(dt)

    def draw(self, screen: pygame.surface.Surface):
        self.scenes[self.current].draw(screen)

    def add(self, scene: Scene):
        self.scenes.append(scene)

    def pop(self):
        self.scenes.pop()

    def transition_to(self, index: int):
        if self.scenes[self.current].keyboard.current_setup is not None:
            self.scenes[self.current].keyboard.current_setup.release_all_of_keys()
        self.current = index
        self.scenes[self.current].setup()
        self.scenes[self.current]._is_setup_finished = True
