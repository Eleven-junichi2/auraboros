
from dataclasses import dataclass
# from typing import Optional, Union

import pygame

from auraboros import global_

from .animation import AnimationImage
from .gameinput import KeyboardManager, Mouse


@dataclass
class Scene(object):

    def __init__(self, manager: "SceneManager"):
        from .gamelevel import Level
        self.manager = manager
        self.gameworld: Level = None
        self.keyboard: KeyboardManager = KeyboardManager()
        self.mouse: Mouse = Mouse()
        # self._joystick: Joystick2 = None
        self.visual_effects: list[AnimationImage] = []
        attrs_of_class = set(dir(self.__class__)) - set(dir(Scene))
        for attr_name in attrs_of_class:
            attrs_of_object = set(
                getattr(self, attr_name).__class__.__mro__) - {object, }
            is_gameworld = Level in attrs_of_object
            if is_gameworld:
                getattr(self, attr_name).scene = self
        self._is_setup_finished = False  # turn True by SceneManager

    def setup(self):
        """
        This method is called on scene transitions
        or if this scene is the first scene.
        """
        pass

    # @property
    # def joystick(self) -> Optional[Joystick2]:
    #     return self._joystick

    # @joystick.setter
    # def joystick(self, value: Union[Joystick2, None]):
    #     self._joystick = value

    def event(self, event: pygame.event):
        pass

    def draw(self, screen: pygame.surface.Surface):
        pass

    def update(self, dt):
        pass


class SceneManager:
    def __init__(self):
        self.scenes: list[Scene] = []
        self._current: int = 0
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
        # if self.scenes[self.current].joystick is not None:
        #     self.scenes[self.current].joystick.event(event)
        return True

    def is_current_scene_has_gameworld(self) -> bool:
        if self.scenes[self.current].gameworld is None:
            return False
        else:
            return True

    def update(self, dt):
        if not self.__is_finished_setup_of_first_scene:
            if global_.is_init_called:
                self.scenes[0].setup()
                self.__is_finished_setup_of_first_scene = True
                self.scenes[0]._is_setup_finished = True
        self.scenes[self.current].update(dt)
        if self.is_current_scene_has_gameworld():
            if not self.scenes[self.current].gameworld.pause:
                [entity.update()
                 for entity in self.scenes[self.current].gameworld.entities]
        [visual_effect.update()
         for visual_effect in self.scenes[self.current].visual_effects]

    def draw(self, screen: pygame.surface.Surface):
        self.scenes[self.current].draw(screen)
        if self.is_current_scene_has_gameworld():
            if not self.scenes[self.current].gameworld.pause:
                [entity.draw(screen)
                 for entity in self.scenes[self.current].gameworld.entities]
        [visual_effect.draw(screen)
         for visual_effect in self.scenes[self.current].visual_effects]
        # Delete finished animations
        [self.scenes[self.current].visual_effects.pop(i)
         for i, visual_effect in enumerate(
            self.scenes[self.current].visual_effects)
         if visual_effect.was_played_once]

    def push(self, scene: Scene):
        self.scenes.append(scene)

    def pop(self):
        self.scenes.pop()

    def transition_to(self, index: int):
        if self.scenes[self.current].keyboard.current_setup is not None:
            self.scenes[
                self.current].keyboard.current_setup.release_all_of_keys()
        self.current = index
        self.scenes[self.current].setup()
        self.scenes[self.current]._is_setup_finished = True
