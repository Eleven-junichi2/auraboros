from collections import deque
from dataclasses import dataclass
from pathlib import Path
import sys

import pygame

pygame.init()

clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()


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


class Sprite(pygame.sprite.Sprite):
    def __init__(self, root_group: pygame.sprite.Group = all_sprites,
                 *args, **kwargs):
        super().__init__(root_group, *args, **kwargs)
        self.root_group = root_group
        self.direction_of_movement = ArrowToTurnToward()
        self.movement_speed = 1


class PlayerShot(Sprite):
    def __init__(self, shooter_sprite: Sprite, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load(AssetFilePath.img("shot1.png"))
        self.shooter = shooter_sprite
        self.rect = self.image.get_rect()
        self.reset_pos()
        self.movement_speed = 2
        self.adjust_movement_speed = 0
        self.is_launching = False
        self.kill()

    def reset_pos(self):
        self.rect.x = \
            self.shooter.rect.x + \
            self.shooter.rect.width / 2 - self.rect.width / 2
        self.rect.y = self.shooter.rect.y - self.rect.height

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
                self.shooter.shot_interval_counter = 0
                self.kill()

    def allow_shooter_to_fire(self):
        self.shooter.is_shot_allowed = True

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)

    def update(self):
        if not self.is_launching:
            self.reset_pos()
        self._fire()


class Player(Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load(AssetFilePath.img("fighter_a.png"))
        self.rect = self.image.get_rect()
        self.movement_speed = 1
        self.shot_max_num = 4
        self.shot_que: deque = deque()
        self.shot_interval = 3
        self.shot_interval_counter = self.shot_interval
        self.is_shot_allowed = True
        self.is_shot_triggered = False

    def trigger_shot(self):
        self.is_shot_triggered = True

    def release_trigger(self):
        self.is_shot_triggered = False

    def _shooting(self):
        if (self.is_shot_allowed and len(self.shot_que) < self.shot_max_num and
                self.shot_interval_counter % self.shot_interval == 0):
            shot = PlayerShot(self)
            shot.will_launch(Arrow.up)
            self.shot_que.append(shot)

    def will_move_to(self, direction: Arrow):
        self.direction_of_movement.set(direction)

    def stop_moving_to(self, direction: Arrow):
        self.direction_of_movement.unset(direction)

    def move_on(self):
        if self.direction_of_movement.is_up:
            self.rect.y -= self.movement_speed
        if self.direction_of_movement.is_down:
            self.rect.y += self.movement_speed
        if self.direction_of_movement.is_right:
            self.rect.x += self.movement_speed
        if self.direction_of_movement.is_left:
            self.rect.x -= self.movement_speed

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)

    def update(self):
        self.move_on()
        if self.is_shot_triggered:
            self._shooting()
        if self.shot_que:
            self.is_shooting = True
        else:
            self.is_shooting = False
            self.shot_interval_counter = 0
        if self.is_shooting:
            self.shot_interval_counter += 1
        if self.shot_interval_counter > self.shot_interval:
            self.shot_interval_counter = 0


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


def run(fps=60):
    player = Player()
    player.rect.x = w_size[0] / 2 - player.rect.width
    player.rect.y = w_size[1] - player.rect.height
    gamefont = pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16)
    debugtext1 = gamefont.render("", True, (255, 255, 255))
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                debugtext1 = gamefont.render(
                    TextToDebug.arrow_keys_from_event(event.key),
                    True, (255, 255, 255))
                if event.key == pygame.K_UP:
                    player.will_move_to(Arrow.up)
                if event.key == pygame.K_DOWN:
                    player.will_move_to(Arrow.down)
                if event.key == pygame.K_RIGHT:
                    player.will_move_to(Arrow.right)
                if event.key == pygame.K_LEFT:
                    player.will_move_to(Arrow.left)
                if event.key == pygame.K_z:
                    player.trigger_shot()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    player.stop_moving_to(Arrow.up)
                if event.key == pygame.K_DOWN:
                    player.stop_moving_to(Arrow.down)
                if event.key == pygame.K_RIGHT:
                    player.stop_moving_to(Arrow.right)
                if event.key == pygame.K_LEFT:
                    player.stop_moving_to(Arrow.left)
                if event.key == pygame.K_z:
                    player.release_trigger()
        all_sprites.update()
        screen.blit(debugtext1, (0, 0))
        all_sprites.draw(screen)
        # resize pixel size
        pygame.transform.scale(screen, w_size_unscaled,
                               pygame.display.get_surface())
        pygame.display.update()
        clock.tick(fps)
    pygame.quit()
