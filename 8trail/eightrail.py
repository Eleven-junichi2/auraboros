from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import List
import functools
import sys

from pygame.math import Vector2
import pygame


pygame.init()

clock = pygame.time.Clock()
clock_counter = 0  # use to implement interval
fps = 60
all_sprites = pygame.sprite.Group()


def init(window_size=(960, 640), caption="", pixel_scale=2):
    """This function initialize pygame and game engine.
    Where to configure settings of game system is here."""
    global screen
    global w_size
    global w_size_unscaled
    pixel_scale = pixel_scale
    w_size_unscaled = window_size
    w_size = tuple([length // pixel_scale for length in window_size])
    pygame.display.set_mode(w_size_unscaled)
    screen = pygame.Surface(w_size)
    pygame.display.set_caption(caption)
    pygame.key.set_repeat(10, 10)


init()


def schedule_interval(interval):
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            if clock_counter % interval == 0:
                return func(*args, **kwargs)
        return _wrapper
    return _decorator


def schedule_instance_method_interval(
        name_of_variable, interval_ignorerer=None):
    """
    Args:
        name_of_variable:
            The name of the variable as interval.
        interval_ignorerer:
            The name of the bool variable that is the condition for ignoring
            interval.
            If interval_ignorer is true, the decorated function is executed
            regardless of the interval.

    Examples:
        class ClassA:
            def __init__(self):
                self.interval_a = 3

            @schedule_interval_self("interval_a")
            def func_a(self):
                pass

        while True:
            instance_a = ClassA()
            instance_a.func_a()
            if clock_counter < 60:
                clock_counter += 1
            else:
                clock_counter = 0
    """
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(self, *args, **kwargs):
            if clock_counter % getattr(
                    self, name_of_variable) == 0 or getattr(
                    self, interval_ignorerer):
                return func(self, *args, **kwargs)
        return _wrapper
    return _decorator


@dataclass
class Arrow:
    """Arrow symbol"""
    up = 0
    down = 1
    right = 2
    left = 3


@dataclass
class ArrowToTurnToward:
    """Use to set direction"""
    is_up: bool = False
    is_down: bool = False
    is_right: bool = False
    is_left: bool = False

    def set(self, direction: Arrow):
        if direction is Arrow.up:
            self.is_up = True
        elif direction is Arrow.down:
            self.is_down = True
        elif direction is Arrow.right:
            self.is_right = True
        elif direction is Arrow.left:
            self.is_left = True

    def unset(self, direction: Arrow):
        if direction is Arrow.up:
            self.is_up = False
        elif direction is Arrow.down:
            self.is_down = False
        elif direction is Arrow.right:
            self.is_right = False
        elif direction is Arrow.left:
            self.is_left = False

    def switch(self, direction: Arrow):
        if direction is Arrow.up:
            self.is_up = not self.is_up
        elif direction is Arrow.down:
            self.is_down = not self.is_down
        elif direction is Arrow.right:
            self.is_right = self.is_right
        elif direction is Arrow.left:
            self.is_left = self.is_left


class AssetFilePath:
    root = Path(sys.argv[0]).parent / "assets"
    img_dirname = "imgs"
    sound_dirname = "sounds"
    font_dirname = "fonts"

    @classmethod
    def img(cls, filename):
        return cls.root / cls.img_dirname / filename

    @classmethod
    def font(cls, filename):
        return cls.root / cls.font_dirname / filename


class TextToDebug:
    @staticmethod
    def arrow_keys(key):
        key_text = f"↑{key[pygame.K_UP]}"
        key_text += f"↓{key[pygame.K_DOWN]}"
        key_text += f"←{key[pygame.K_LEFT]}"
        key_text += f"→{key[pygame.K_RIGHT]}"
        return key_text

    @staticmethod
    def arrow_keys_from_event(event_key):
        key_text = f"↑{event_key == pygame.K_UP}"
        key_text += f"↓{event_key == pygame.K_DOWN}"
        key_text += f"←{event_key == pygame.K_LEFT}"
        key_text += f"→{event_key == pygame.K_RIGHT}"
        return key_text

    @staticmethod
    def movement_speed(movement_speed):
        return f"speed:{movement_speed}"


class Sprite(pygame.sprite.Sprite):
    def __init__(self, root_group: pygame.sprite.Group = all_sprites,
                 *args, **kwargs):
        super().__init__(root_group, *args, **kwargs)
        self.root_group = root_group
        self.direction_of_movement = ArrowToTurnToward()
        self.movement_speed = 1


class ShooterSprite(Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shot_max_num = 1
        self.shot_que: deque = deque()
        self.shot_interval = 1
        self.shot_interval_counter = self.shot_interval
        self.is_shot_allowed = True


class PlayerShot(Sprite):
    def __init__(self, shooter_sprite: ShooterSprite, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load(AssetFilePath.img("shot1.png"))
        self.shooter = shooter_sprite
        self.rect = self.image.get_rect()
        self.reset_pos()
        self.movement_speed = 3
        self.adjust_movement_speed = 0
        self.is_launching = False
        self.kill()

    def reset_pos(self):
        self.rect.x = \
            self.shooter.rect.x + \
            self.shooter.rect.width / 2 - self.rect.width / 2
        self.rect.y = self.shooter.rect.y + \
            self.shooter.rect.height / 2 - self.rect.height

    def will_launch(self, direction: Arrow):
        self.direction_of_movement.set(direction)
        self.root_group.add(self)
        self.is_launching = True
        if (self.direction_of_movement.is_up and
                self.shooter.direction_of_movement.is_up):
            self.adjust_movement_speed = self.shooter.movement_speed
        else:
            self.adjust_movement_speed = 0

    def _fire(self):
        if self.is_launching:
            if self.direction_of_movement.is_up:
                self.rect.y -= self.movement_speed + self.adjust_movement_speed
            if self.direction_of_movement.is_down:
                self.rect.y += self.movement_speed
            if self.rect.y < 0:
                self.direction_of_movement.unset(Arrow.up)
                self.is_launching = False
                self.reset_pos()
                self.allow_shooter_to_fire()
                self.shooter.shot_que.pop()
                # self.shooter.shot_interval_counter = 0
                self.kill()

    def allow_shooter_to_fire(self):
        self.shooter.is_shot_allowed = True

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)

    def update(self):
        if not self.is_launching:
            self.reset_pos()
        self._fire()


class Player(ShooterSprite):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load(AssetFilePath.img("fighter_a.png"))
        self.rect = self.image.get_rect()
        self.movement_speed = 1
        self.shot_max_num = 4
        self.shot_interval = 3
        self.shot_que: deque = deque()
        self.ignore_shot_interval = True
        self.is_shot_triggered = False

    def trigger_shot(self):
        self.is_shot_triggered = True

    def release_trigger(self):
        self.is_shot_triggered = False

    @schedule_instance_method_interval(
        "shot_interval", "ignore_shot_interval")
    def _shooting(self):
        if (self.is_shot_allowed and (len(self.shot_que) < self.shot_max_num)):
            shot = PlayerShot(self)
            shot.will_launch(Arrow.up)
            self.shot_que.append(shot)

    def will_move_to(self, direction: Arrow):
        self.direction_of_movement.set(direction)

    def stop_moving_to(self, direction: Arrow):
        self.direction_of_movement.unset(direction)

    def move_on(self):
        # if diagonal movement
        if ((self.direction_of_movement.is_up and
            self.direction_of_movement.is_right) or
            (self.direction_of_movement.is_up and
            self.direction_of_movement.is_left) or
            (self.direction_of_movement.is_down and
            self.direction_of_movement.is_right) or
            (self.direction_of_movement.is_down and
                self.direction_of_movement.is_left)):
            vec = Vector2(self.movement_speed, self.movement_speed)
            # Correct the speed of diagonal movement
            movement_speed = vec.normalize().x
        else:
            movement_speed = self.movement_speed
        movement_speed = self.movement_speed
        if self.direction_of_movement.is_up:
            self.rect.y -= movement_speed
        if self.direction_of_movement.is_down:
            self.rect.y += movement_speed
        if self.direction_of_movement.is_right:
            self.rect.x += movement_speed
        if self.direction_of_movement.is_left:
            self.rect.x -= movement_speed

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)

    def update(self):
        self.move_on()
        if self.shot_que:
            self.is_shooting = True
            self.ignore_shot_interval = False
        else:
            self.is_shooting = False
            self.ignore_shot_interval = True
        if self.is_shot_triggered:
            self._shooting()


@dataclass
class Scene(object):
    def __init__(self):
        pass

    def event(self, event: pygame.event):
        pass

    def draw(self, screen: pygame.surface.Surface):
        pass

    def update(self):
        pass


class SceneManager:
    def __init__(self):
        self.scenes: List[Scene] = []
        self.current: int = 0

    def event(self, event: pygame.event):
        self.scenes[self.current].event(event)

    def update(self):
        self.scenes[self.current].update

    def draw(self, screen: pygame.surface.Surface):
        self.scenes[self.current].draw(screen)

    def push(self, scene: Scene):
        self.scenes.append(scene)

    def pop(self):
        self.scenes.pop()


class GameScene(Scene):
    player = Player()
    player.rect.x = w_size[0] / 2 - player.rect.width
    player.rect.y = w_size[1] - player.rect.height
    gamefont = pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16)
    debugtext1 = gamefont.render("", True, (255, 255, 255))

    def __init__(self):
        super().__init__()

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            self.debugtext1 = self.gamefont.render(
                TextToDebug.arrow_keys_from_event(event.key),
                True, (255, 255, 255))
            if event.key == pygame.K_UP:
                self.player.will_move_to(Arrow.up)
            if event.key == pygame.K_DOWN:
                self.player.will_move_to(Arrow.down)
            if event.key == pygame.K_RIGHT:
                self.player.will_move_to(Arrow.right)
            if event.key == pygame.K_LEFT:
                self.player.will_move_to(Arrow.left)
            if event.key == pygame.K_z:
                self.player.trigger_shot()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self.player.stop_moving_to(Arrow.up)
            if event.key == pygame.K_DOWN:
                self.player.stop_moving_to(Arrow.down)
            if event.key == pygame.K_RIGHT:
                self.player.stop_moving_to(Arrow.right)
            if event.key == pygame.K_LEFT:
                self.player.stop_moving_to(Arrow.left)
            if event.key == pygame.K_z:
                self.player.release_trigger()

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.debugtext1, (0, 0))


def run(fps_num=60):
    global fps
    global clock_counter
    fps = fps_num
    running = True
    scene_manager = SceneManager()
    scene_manager.push(GameScene())
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.event(event)
        scene_manager.update()
        scene_manager.draw(screen)
        all_sprites.update()
        all_sprites.draw(screen)
        # resize pixel size
        pygame.transform.scale(screen, w_size_unscaled,
                               pygame.display.get_surface())
        pygame.display.update()
        clock.tick(fps)
        if clock_counter < fps:
            clock_counter += 1
        else:
            clock_counter = 0
    pygame.quit()
