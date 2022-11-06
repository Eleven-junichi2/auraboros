from collections import deque
from collections.abc import MutableMapping
from dataclasses import dataclass
from pathlib import Path
from random import randint
from typing import Iterator, Optional
from inspect import isclass
import functools
import sys

from pygame.math import Vector2
import pygame


# TODO: Delay second shooting
# TODO: Kill shot sprite on hit
# TODO: Clean visual effect que

pygame.init()

clock = pygame.time.Clock()
clock_counter = 0  # use to implement interval
fps = 60


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
        variable_as_interval: str, interval_ignorerer=None):
    """
    Args:
        variable_as_interval:
            The name of the variable as interval.
        interval_ignorerer:
            The name of the bool variable that is the condition for ignoring
            interval.
            If interval_ignorer is True, the decorated function is executed
            regardless of the interval.

    Examples:
        class ClassA:
            def __init__(self):
                self.interval_a = 3

            @schedule_instance_method_interval("interval_a")
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
            if interval_ignorerer:
                bool_from_interval_ignorerer = getattr(
                    self, interval_ignorerer)
            else:
                bool_from_interval_ignorerer = False
            if (clock_counter % getattr(
                    self, variable_as_interval) == 0 or
                    bool_from_interval_ignorerer):
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


class SpriteSheet:
    def __init__(self, filename):
        self.image = pygame.image.load(filename)

    def image_by_area(self, x, y, width, height) -> pygame.surface.Surface:
        """"""
        image = pygame.Surface((width, height))
        image.blit(self.image, (0, 0), (x, y, width, height))
        # image = pg.transform.scale(image, (width // 2, height // 2))
        return image


class Sprite(pygame.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene: Scene
        self.direction_of_movement = ArrowToTurnToward()
        self.movement_speed = 1

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

    def center_x_on_screen(self, ):
        """Center the posistion on the screen"""
        self.rect.x = w_size[0] / 2 - self.rect.width

    def center_y_on_screen(self, ):
        """Center the posistion on the screen"""
        self.rect.y = w_size[1] / 2 - self.rect.height


class ShooterSprite(Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shot_max_num = 1
        self.shot_que: deque = deque()
        self.shot_interval = 1
        self.is_shot_allowed = True


class AnimationImage:
    def __init__(self):
        self.anim_frames: list[pygame.surface.Surface] = [
            pygame.surface.Surface((0, 0)), ]
        self.anim_frame_id = 0
        self.anim_interval = 1
        self.playing_animation = False
        self.image = self.anim_frames[self.anim_frame_id]

    def draw_while_playing(self, screen: pygame.surface.Surface):
        if self.playing_animation:
            screen.blit(self.image, self.rect)

    @schedule_instance_method_interval("anim_interval")
    def update_frame_at_interval(self):
        return self.update_frame()

    def update_frame(self) -> Optional[bool]:
        """Returns:
            True or False: Whether the animation is playing or not."""
        # update while playing animation
        if self.playing_animation:
            self.image = self.anim_frames[self.anim_frame_id]
            if self.anim_frame_id < len(self.anim_frames) - 1:
                self.anim_frame_id += 1
                is_finished = False
            else:
                self.anim_frame_id = 0
                self.playing_animation = False
                is_finished = True
            return is_finished

    def set_current_frame_to_image(self):
        self.image = self.anim_frames[self.anim_frame_id]

    def set_current_action_id(self, id: int):
        self.anim_action_id = id

    def let_play_animation(self):
        """Active update and draw function"""
        self.playing_animation = True
        # self.anim_frame_id = 0

    def let_continue_animation(self):
        """Active update and draw function without reset animation"""
        self.playing_animation = True

    def draw(self, screen):
        self.draw_while_playing(screen)

    def update(self):
        return self.update_frame_at_interval()


class AnimationFactory(MutableMapping):
    """
    Examples:
        class ExampleAnimation(AnimationImage):
            pass
        a = AnimationFactory()
        a["animation_a"] = ExampleAnimation
        animation = a["jump_animation"]
        animation.let_play_animation()
    """

    def __init__(self, *args, **kwargs):
        self.__dict__: dict[int, AnimationImage]
        self.__dict__.update(*args, **kwargs)
        # self.anim_action_id = 0

    # def register(self, animation: AnimationImage):
        # self.__setitem__()

    def __getitem__(self, key) -> AnimationImage:
        return self.__dict__[key]()

    def __setitem__(self, key, value: AnimationImage):
        if isclass(value):
            self.__dict__[key] = value
        else:
            raise ValueError("The value must not be instance.")

    def __delitem__(self, key: int):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


class Explosion(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("explosion_a.png"))
        self.anim_frames: list[pygame.surface.Surface] = \
            [self.sprite_sheet.image_by_area(0, 0, 16, 16),
             self.sprite_sheet.image_by_area(0, 16, 16, 16),
             self.sprite_sheet.image_by_area(0, 16*2, 16, 16),
             self.sprite_sheet.image_by_area(0, 16*3, 16, 16),
             self.sprite_sheet.image_by_area(0, 16*4, 16, 16),
             self.sprite_sheet.image_by_area(0, 16*5, 16, 16)]
        self.anim_interval = 2
        # self.image = self.anim_frames[0]
        self.rect = self.image.get_rect()


class Enemy(Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load(AssetFilePath.img("enemy_a.png"))
        self.rect = self.image.get_rect()
        self.animation = AnimationFactory()
        self.animation["death"] = Explosion

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)

    def death(self):
        animation = self.animation["death"]
        animation.rect = self.rect
        animation.let_play_animation()
        self.scene.visual_effects.append(animation)
        self.kill()


class PlayerShot(Sprite):
    def __init__(self, shooter_sprite: ShooterSprite,
                 groups_to_show_bullet: Iterator[pygame.sprite.Group],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load(AssetFilePath.img("shot1.png"))
        self.shooter = shooter_sprite
        self.groups_to_show = groups_to_show_bullet
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
        [group.add(self) for group in self.groups_to_show]
        self.is_launching = True
        # Accelerate if the direction is the same as that of the shooter.
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
        self.shot_current_interval = self.shot_interval
        self.shot_que: deque = deque()
        self.ignore_shot_interval = True
        self.is_shot_triggered = False

    def trigger_shot(self):
        self.is_shot_triggered = True

    def release_trigger(self):
        self.is_shot_triggered = False

    @schedule_instance_method_interval(
        "shot_current_interval", "ignore_shot_interval")
    def _shooting(self):
        if (self.is_shot_allowed and (len(self.shot_que) < self.shot_max_num)):
            shot = PlayerShot(self, self.groups())
            shot.will_launch(Arrow.up)
            self.shot_que.append(shot)

    def will_move_to(self, direction: Arrow):
        self.direction_of_movement.set(direction)

    def stop_moving_to(self, direction: Arrow):
        self.direction_of_movement.unset(direction)

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
        self.sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.visual_effects: deque[AnimationImage] = []

        # --- Add attributes of Sprite defined in subclass to self.sprites ---
        attrs_of_class = set(dir(self.__class__)) - set(dir(Scene))
        for attr_name in attrs_of_class:
            attrs_of_object = \
                set(getattr(self, attr_name).__class__.__mro__) - {object, }
            is_sprite = Sprite in attrs_of_object
            if is_sprite:
                self.sprites.add(getattr(self, attr_name))
                getattr(self, attr_name).scene = self

    def event(self, event: pygame.event):
        pass

    def draw(self, screen: pygame.surface.Surface):
        pass

    def update(self):
        pass


class SceneManager:
    def __init__(self):
        self.scenes: list[Scene] = []
        self.current: int = 0

    def event(self, event: pygame.event):
        self.scenes[self.current].event(event)

    def update(self):
        self.scenes[self.current].update()
        self.scenes[self.current].sprites.update()
        [self.pop_played_visual_effect(visual_effect.update())
         for visual_effect in self.scenes[self.current].visual_effects]

    def draw(self, screen: pygame.surface.Surface):
        self.scenes[self.current].draw(screen)
        [sprite.draw(screen)
         for sprite in self.scenes[self.current].sprites.sprites()]
        [visual_effect.draw(screen)
         for visual_effect in self.scenes[self.current].visual_effects]

    def pop_played_visual_effect(self, is_played: Optional[bool]):
        if is_played:
            self.scenes[self.current].visual_effects.pop()

    def push(self, scene: Scene):
        self.scenes.append(scene)

    def pop(self):
        self.scenes.pop()


class GameScene(Scene):
    player = Player()
    player.center_x_on_screen()
    player.rect.y = w_size[1] - player.rect.height
    enemy_a = Enemy()
    enemy_a.rect.x = w_size[0] / 2 - enemy_a.rect.width
    enemy_a.rect.y = w_size[1] / 4 - enemy_a.rect.height
    gamefont = pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16)
    debugtext1 = gamefont.render("", True, (255, 255, 255))
    debugtext2 = gamefont.render("", True, (255, 255, 255))
    background = pygame.surface.Surface((w_size[0], w_size[1] * 2))
    bg_scroll_y = 0
    density_of_stars_on_bg = randint(100, 500)
    # explosion_effect = Explosion()

    def __init__(self):
        super().__init__()
        self.set_background()

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
            if event.key == pygame.K_x:
                self.sprites.add(self.enemy_a)
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
        print(self.visual_effects)
        self.scroll_background()
        if self.is_player_shot_hit_enemy():
            self.destory_enemy()

    def draw(self, screen):
        screen.blit(self.background, (0, self.bg_scroll_y - w_size[1]))
        screen.blit(self.debugtext1, (0, 0))
        screen.blit(self.debugtext2, (0, 16))

    def is_player_shot_hit_enemy(self):
        return True in {
            pygame.sprite.collide_rect(shot, self.enemy_a)
            for shot in self.player.shot_que} and self.enemy_a.alive()

    def destory_enemy(self):
        self.enemy_a.death()

    def set_background(self):
        [self.background.fill(
            (randint(0, 255), randint(0, 255), randint(0, 255)),
            ((randint(0, w_size[0]), randint(0, w_size[1] * 2)), (1, 1)))
         for i in range(self.density_of_stars_on_bg)]

    def set_background_for_scroll(self):
        new_background = pygame.surface.Surface((w_size[0], w_size[1] * 2))
        new_background.blit(
            self.background, (0, w_size[1], w_size[0], w_size[1]))
        randomize_density = \
            randint(-self.density_of_stars_on_bg // 2,
                    self.density_of_stars_on_bg // 2)
        [new_background.fill(
            (randint(0, 255), randint(0, 255), randint(0, 255)),
            ((randint(0, w_size[0]), randint(0, w_size[1])),
             (1, 1)))
         for i in range(self.density_of_stars_on_bg + randomize_density)]
        self.background = new_background
        # draw line for debug
        # new_background.fill(
        #     (randint(0, 255), randint(0, 255), randint(0, 255)),
        #     ((0, 0),
        #      (w_size[0], 1)))

    def scroll_background(self):
        self.debugtext2 = self.gamefont.render(
            f"{self.bg_scroll_y}", True, (255, 255, 255))
        self.bg_scroll_y += 1
        if self.bg_scroll_y > w_size[1]:
            self.bg_scroll_y = 0
            self.set_background_for_scroll()


class TitleMenuScene(Scene):
    def __init__(self):
        super().__init__()


def run(fps_num=60):
    global fps
    global clock_counter
    fps = fps_num
    running = True
    scene_manager = SceneManager()
    # scene_manager.push(TitleMenuScene())
    scene_manager.push(GameScene())

    while running:
        time_delta = clock.tick(fps)  # noqa
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.event(event)
        scene_manager.update()
        scene_manager.draw(screen)
        # resize pixel size
        pygame.transform.scale(screen, w_size_unscaled,
                               pygame.display.get_surface())
        pygame.display.update()
        if clock_counter < fps:
            clock_counter += 1
        else:
            clock_counter = 0
    pygame.quit()
