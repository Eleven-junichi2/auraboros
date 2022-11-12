from .utilities import Arrow, AssetFilePath, TextToDebug
from .schedule import IntervalCounter, schedule_instance_method_interval
from .gamescene import Scene, SceneManager
from .entity import Sprite, ShooterSprite
from collections import deque
from random import randint
from typing import Iterator

import pygame

from .animation import (
    AnimationDict, AnimationImage, AnimationFactory, SpriteSheet
)

from .__init__ import init, w_size, screen, w_size_unscaled  # noqa

# TODO: Delay second shooting

pygame.init()

clock = pygame.time.Clock()
fps = 60


class Explosion(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("explosion_a.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 0, 16, 16),
            self.sprite_sheet.image_by_area(
                0, 16, 16, 16),
            self.sprite_sheet.image_by_area(
                0, 16*2, 16, 16),
            self.sprite_sheet.image_by_area(
                0, 16*3, 16, 16),
            self.sprite_sheet.image_by_area(
                0, 16*4, 16, 16),
            self.sprite_sheet.image_by_area(0, 16*5, 16, 16)]
        self.anim_interval = 2


class FighterIdle(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("fighter_a.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 22 * 2, 22, 22), ]


class FighterRollLeft(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("fighter_a.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 0, 22, 22),
            self.sprite_sheet.image_by_area(0, 22, 22, 22), ]
        self.anim_interval = 20
        self.is_loop = False


class FighterRollRight(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("fighter_a.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 22 * 3, 22, 22),
            self.sprite_sheet.image_by_area(0, 22 * 4, 22, 22), ]
        self.anim_interval = 20
        self.is_loop = False
        # self.rect = self.image.get_rect()


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
        if self.alive():
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
        self.movement_speed = 4
        self.adjust_movement_speed = 1
        self.is_launching = False
        self.allow_to_destruct = False
        self.kill()

    def reset_pos(self):
        self.x = self.shooter.x + \
            self.shooter.rect.width / 2 - self.rect.width / 2
        self.y = self.shooter.y + \
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

    def _fire(self, dt):
        if self.is_launching:
            self.move_on(dt)
            if self.y < 0:
                self.direction_of_movement.unset(Arrow.up)
                self.is_launching = False
                self.reset_pos()
                self.allow_shooter_to_fire()
                self.allow_to_destruct = True

    def _destruct(self):
        """Remove sprite from group and que of shooter."""
        self.shooter.shot_que.pop()
        self.kill()

    def allow_shooter_to_fire(self):
        self.shooter.is_shot_allowed = True

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)

    def update(self, dt):
        if not self.is_launching:
            self.reset_pos()
        self._fire(dt)
        if self.allow_to_destruct:
            self._destruct()
            self.allow_to_destruct = False


class Player(ShooterSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation = AnimationDict()
        self.animation["idle"] = FighterIdle()
        self.animation["roll_left"] = FighterRollLeft()
        self.animation["roll_right"] = FighterRollRight()
        self.action = "idle"
        self.image = self.animation[self.action].image
        self.rect = self.image.get_rect()
        self.movement_speed = 2
        self.shot_max_num = 3
        self.shot_interval = 3
        self.shot_current_interval = self.shot_interval
        self.shot_que: deque = deque()
        self.ignore_shot_interval = True
        self.is_shot_triggered = False
        self.is_moving = True

    def trigger_shot(self):
        self.is_shot_triggered = True

    def release_trigger(self):
        self.is_shot_triggered = False

    @ schedule_instance_method_interval(
        "shot_current_interval", interval_ignorerer="ignore_shot_interval")
    def _shooting(self):
        if (self.is_shot_allowed and (len(self.shot_que) < self.shot_max_num)):
            shot = PlayerShot(self, self.groups())
            shot.will_launch(Arrow.up)
            self.shot_que.append(shot)

    def will_move_to(self, direction: Arrow):
        self.direction_of_movement.set(direction)
        if self.direction_of_movement.is_left:
            self.action = "roll_left"
        elif self.direction_of_movement.is_right:
            self.action = "roll_right"
        if not self.is_moving:
            self.animation[self.action].let_play_animation()
        self.is_moving = True

    def stop_moving_to(self, direction: Arrow):
        self.direction_of_movement.unset(direction)
        if not self.direction_of_movement.is_set_any():
            self.action = "idle"
            self.is_moving = False

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)

    def update(self, dt):
        if self.is_moving:
            self.move_on(dt)
        if self.shot_que:
            self.is_shooting = True
            self.ignore_shot_interval = False
        else:
            self.is_shooting = False
            self.ignore_shot_interval = True
        if self.is_shot_triggered:
            self._shooting()
        self.do_animation(dt)

    def do_animation(self, dt):
        self.animation[self.action].update(dt)
        self.image = self.animation[self.action].image


class GameScene(Scene):
    player = Player()
    player.center_x_on_screen()
    player.y = w_size[1] - player.rect.height
    enemy_a = Enemy()
    enemy_a.x = w_size[0] / 2 - enemy_a.rect.width
    enemy_a.y = w_size[1] / 4 - enemy_a.rect.height
    gamefont = pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16)
    background = pygame.surface.Surface((w_size[0], w_size[1] * 2))
    bg_scroll_y = 0
    density_of_stars_on_bg = randint(100, 500)
    debugtext1 = gamefont.render("", True, (255, 255, 255))
    shot_sound = pygame.mixer.Sound(AssetFilePath.sound("shot1.wav"))

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

    def update(self, dt):
        self.debugtext3 = self.gamefont.render(
            f"dt:{dt}", True, (255, 255, 255))
        self.scroll_background()
        shots = self.shots_that_hit_enemy()
        if shots:
            self.destroy_enemy()
            [self.destroy_shot_of_player(shot) for shot in shots]

    def draw(self, screen):
        self.debugtext2 = self.gamefont.render(
            TextToDebug.fps(clock), True, (255, 255, 255))
        self.debugtext4 = self.gamefont.render(
            f"Rect X:{self.player.rect.x} Rect Y:{self.player.rect.y}",
            True, (255, 255, 255))
        self.debugtext5 = self.gamefont.render(
            f"X:{self.player.x} Y:{self.player.y}",
            True, (255, 255, 255))
        screen.blit(self.background, (0, self.bg_scroll_y - w_size[1]))
        screen.blit(self.debugtext1, (0, 0))
        screen.blit(self.debugtext2, (0, 16))
        screen.blit(self.debugtext3, (0, 32))
        screen.blit(self.debugtext4, (0, 48))
        screen.blit(self.debugtext5, (0, 64))

    def shots_that_hit_enemy(self) -> list[PlayerShot]:
        shots = [shot for shot in self.player.shot_que
                 if pygame.sprite.collide_rect(shot, self.enemy_a)
                 and self.enemy_a.alive()]
        return shots

    def destroy_enemy(self):
        self.enemy_a.death()

    def destroy_shot_of_player(self, shot: PlayerShot):
        shot.allow_to_destruct = True

    def set_background(self):
        [self.background.fill(
            (randint(0, 255), randint(0, 255), randint(0, 255)),
            ((randint(0, w_size[0]), randint(0, w_size[1] * 2)), (1, 1)))
         for i in range(self.density_of_stars_on_bg)]

    def set_background_for_scroll(self):
        new_background = pygame.surface.Surface((w_size[0], w_size[1] * 2))
        new_background.blit(
            self.background, (0, w_size[1], w_size[0], w_size[1]))
        randomize_density = randint(-self.density_of_stars_on_bg // 2,
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
        self.bg_scroll_y += 1
        if self.bg_scroll_y > w_size[1]:
            self.bg_scroll_y = 0
            self.set_background_for_scroll()


class TitleMenuScene(Scene):
    def __init__(self):
        super().__init__()


def run(fps_num=fps):
    global fps
    global clock_counter
    fps = fps_num
    running = True
    scene_manager = SceneManager()
    # scene_manager.push(TitleMenuScene())
    scene_manager.push(GameScene())
    while running:
        dt = clock.tick(fps)/1000  # dt means delta time

        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.event(event)
        scene_manager.update(dt)
        scene_manager.draw(screen)
        # resize pixel size
        pygame.transform.scale(screen, w_size_unscaled,
                               pygame.display.get_surface())
        pygame.display.update()
        IntervalCounter.tick(dt)
    pygame.quit()
