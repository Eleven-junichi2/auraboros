from dataclasses import dataclass

import pygame

from .animation import AnimationImage


@dataclass
class Scene(object):

    def __init__(self):
        from .gamelevel import Level
        self.gameworld: Level = None
        self.visual_effects: list[AnimationImage] = []
        attrs_of_class = set(dir(self.__class__)) - set(dir(Scene))
        for attr_name in attrs_of_class:
            attrs_of_object = set(
                getattr(self, attr_name).__class__.__mro__) - {object, }
            is_gameworld = Level in attrs_of_object
            if is_gameworld:
                getattr(self, attr_name).scene = self

    def event(self, event: pygame.event):
        pass

    def draw(self, screen: pygame.surface.Surface):
        pass

    def update(self, dt):
        pass


class SceneManager:
    def __init__(self):
        self.scenes: list[Scene] = []
        self.current: int = 0

    def event(self, event: pygame.event):
        self.scenes[self.current].event(event)

    def update(self, dt):
        self.scenes[self.current].update(dt)
        # self.scenes[self.current].sprites.update(dt)
        [entity.update(dt)
         for entity in self.scenes[self.current].gameworld.entities]
        [visual_effect.update(dt)
         for visual_effect in self.scenes[self.current].visual_effects]
        # print(self.scenes[self.current].gameworld.entities)

    def draw(self, screen: pygame.surface.Surface):
        # Delete finished animations
        [self.scenes[self.current].visual_effects.pop(i)
         for i, visual_effect in enumerate(
            self.scenes[self.current].visual_effects)
         if visual_effect.was_played_once]
        self.scenes[self.current].draw(screen)
        [entity.draw(screen)
         for entity in self.scenes[self.current].gameworld.entities]
        # [sprite.draw(screen)
        #  for sprite in self.scenes[self.current].sprites.sprites()]
        [visual_effect.draw(screen)
         for visual_effect in self.scenes[self.current].visual_effects]

    def push(self, scene: Scene):
        self.scenes.append(scene)

    def pop(self):
        self.scenes.pop()