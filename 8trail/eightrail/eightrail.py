from collections import UserDict
from inspect import isclass
# import math
from typing import Any
from .utilities import Arrow, AssetFilePath, TextToDebug  # noqa
from .schedule import IntervalCounter, schedule_instance_method_interval
from .sound import SoundDict
from .gamelevel import Level
from .gamescene import Scene, SceneManager
from .gametext import TextSurfaceFactory
from .entity import Sprite, ShooterSprite, Enemy

import pygame

from .animation import (
    AnimationDict, AnimationImage, AnimationFactory, SpriteSheet
)

from .__init__ import init, w_size, screen, w_size_unscaled  # noqa

# TODO: Game Level

pygame.init()
pygame.mixer.init()
# pygame.mixer.set_num_channels(8)

clock = pygame.time.Clock()
fps = 60

textfactory = TextSurfaceFactory()
textfactory.register_font(
    "misaki_gothic",
    pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16))

sound_dict = SoundDict()
sound_dict["explosion"] = pygame.mixer.Sound(
    AssetFilePath.sound("explosion1.wav"))
sound_dict["player_death"] = pygame.mixer.Sound(
    AssetFilePath.sound("explosion2.wav"))
sound_dict["shot"] = pygame.mixer.Sound(
    AssetFilePath.sound("shot1.wav"))
sound_dict["laser"] = pygame.mixer.Sound(
    AssetFilePath.sound("laser2.wav"))


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


class PlayerExplosion(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("explosion_b.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 0, 22, 22),
            self.sprite_sheet.image_by_area(
                0, 22, 22, 22),
            self.sprite_sheet.image_by_area(
                0, 22*2, 22, 22),
            self.sprite_sheet.image_by_area(
                0, 22*3, 22, 22),
            self.sprite_sheet.image_by_area(
                0, 22*4, 22, 22),
            self.sprite_sheet.image_by_area(0, 22*5, 22, 22)]
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
        self.anim_interval = 15
        self.is_loop = False


class FighterRollRight(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("fighter_a.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 22 * 3, 22, 22),
            self.sprite_sheet.image_by_area(0, 22 * 4, 22, 22), ]
        self.anim_interval = 15
        self.is_loop = False


class ScoutDiskIdle(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("enemy_a.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 0, 16, 16),
            self.sprite_sheet.image_by_area(0, 16, 16, 16),
            self.sprite_sheet.image_by_area(0, 16 * 2, 16, 16),
            self.sprite_sheet.image_by_area(0, 16 * 3, 16, 16), ]
        self.anim_interval = 5


class ScoutDiskMove(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("enemy_a.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 16 * 4, 16, 16),
            self.sprite_sheet.image_by_area(0, 16 * 5, 16, 16),
            self.sprite_sheet.image_by_area(0, 16 * 6, 16, 16),
            self.sprite_sheet.image_by_area(0, 16 * 7, 16, 16), ]
        self.anim_interval = 5


class PlayerShot(Sprite):
    def __init__(self, shooter_sprite: ShooterSprite, shot_que: list,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shot_que = shot_que
        self.image = pygame.image.load(AssetFilePath.img("shot1.png"))
        self.shooter = shooter_sprite
        self.rect = self.image.get_rect()
        self.hitbox = self.image.get_rect()
        self.reset_pos_x()
        self.reset_pos_y()
        self.movement_speed = 4
        self.adjust_movement_speed = 1
        self.is_launching = False

    def reset_pos_x(self):
        self.x = self.shooter.x + \
            self.shooter.rect.width / 2 - self.rect.width / 2

    def reset_pos_y(self):
        self.y = self.shooter.y + \
            self.shooter.rect.height / 2 - self.rect.height

    def will_launch(self, direction: Arrow):
        self.direction_of_movement.set(direction)
        self.entity_container.append(self)
        self.is_launching = True
        # set accelerater if the direction is the same as that of the shooter.
        if (self.direction_of_movement.is_up and
                self.shooter.direction_of_movement.is_up):
            self.adjust_movement_speed = self.shooter.movement_speed
        else:
            self.adjust_movement_speed = 0

    def _fire(self, dt):
        if self.is_launching:
            self.move_on(dt)
            if (self.y < 0 or w_size[1] < self.y or
                    self.x < 0 or w_size[0] < self.x):
                self.direction_of_movement.unset(Arrow.up)
                self.is_launching = False
                self.reset_pos_x()
                self.reset_pos_y()
                self.allow_shooter_to_fire()
                self.death()

    def death(self):
        """Remove sprite from group and que of shooter."""
        if self in self.shot_que:
            self.shot_que.remove(self)
            self.remove_from_container()
            self.is_launching = False

    def allow_shooter_to_fire(self):
        self.shooter.is_shot_allowed = True

    def update(self, dt):
        if not self.is_launching:
            self.reset_pos_x()
            self.reset_pos_y()
        self._fire(dt)


class PlayerLaser(PlayerShot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load(AssetFilePath.img("laser1.png"))
        self.rect = self.image.get_rect()
        self.hitbox = self.image.get_rect()
        self.movement_speed = 6
        self.reset_pos_x()
        self.reset_pos_y()

    def move_on(self, dt):
        self.reset_pos_x()
        super().move_on(dt)


class PlayerMissile(PlayerShot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load(AssetFilePath.img("shot2.png"))
        self.rect = self.image.get_rect()
        self.hitbox = self.image.get_rect()
        self.movement_speed = 2.75
        self.reset_pos_x()
        self.reset_pos_y()

    def move_on(self, dt):
        # if self.move_target_x and self.move_target_y:
        # self.move_aim_to_enemy()
        # self.move_strike_to_entity(dt, Enemy)
        self.set_destination_to_enemy()
        self.move_to_destination(dt)
        super().move_on(dt)

    def allow_shooter_to_fire(self):
        self.shooter.is_missile_allowed = True

    def set_destination_to_enemy(self) -> bool:
        enemy_list = [entity for entity in self.gameworld.entities
                      if isinstance(entity, Enemy)]
        if len(enemy_list) >= len(self.shot_que):
            for i, missile in enumerate(self.shot_que):
                enemy = enemy_list[i]
                self.shot_que[i].move_target_x = enemy.hitbox.x
                self.shot_que[i].move_target_y = enemy.hitbox.y
                print(self.move_target_x)
            return True
        else:
            self.move_target_x = None
            self.move_target_y = None
            return False


class ScoutDiskEnemy(Enemy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.explosion_sound = sound_dict["explosion"]
        self.visual_effects = AnimationFactory()
        self.visual_effects["death"] = Explosion
        self.animation = AnimationDict()
        self.animation["idle"] = ScoutDiskIdle()
        self.animation["move"] = ScoutDiskMove()
        self.image = self.animation[self.action].image
        self.rect = self.image.get_rect()
        self.hitbox = self.image.get_rect()
        self.hitbox.width = 10
        self.hitbox.height = 10
        self.movement_speed = 2
        self.behavior_pattern = None
        self.behavior_pattern_dict[
            "strike_to_player"] = self.move_strike_to_player
        self.gamescore = 10
        self.radian_for_behavior_pattern = 0

    def update(self, dt):
        super().update(dt)
        self.animation[self.action].let_continue_animation()
        self.image = self.animation[self.action].image
        self.animation[self.action].update(dt)

    def move_strike_to_player(self, dt):
        self.move_strike_to_entity(dt, Player)

    def death(self):
        visual_effect = self.visual_effects["death"]
        visual_effect.rect = self.rect
        visual_effect.let_play_animation()
        self.gameworld.scene.visual_effects.append(visual_effect)
        self.explosion_sound.play()
        super().death()


class WeaponBulletFactory(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data: dict[Any, PlayerShot]

    def __setitem__(self, key, value):
        if isclass(value):
            self.data[key] = {}
            self.data[key]["entity"] = value
            self.data[key]["max_num"] = 1
            self.data[key]["interval"] = 1
        else:
            raise ValueError("The value must not be instance.")


class Player(ShooterSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shot_que = []
        self.weapon = WeaponBulletFactory()
        self.weapon["normal"] = PlayerShot
        self.weapon["normal"]["max_num"] = 3
        self.weapon["normal"]["interval"] = 3
        self.weapon["laser"] = PlayerLaser
        self.weapon["laser"]["max_num"] = 6
        self.weapon["laser"]["interval"] = 4
        self.change_weapon("normal")

        self.missile_que = []
        self.second_weapon = WeaponBulletFactory()
        self.second_weapon["normal"] = PlayerMissile
        self.second_weapon["normal"]["max_num"] = 2
        self.second_weapon["normal"]["interval"] = 3

        self.animation = AnimationDict()
        self.animation["idle"] = FighterIdle()
        self.animation["roll_left"] = FighterRollLeft()
        self.animation["roll_right"] = FighterRollRight()
        self.change_second_weapon("normal")

        self.visual_effects = AnimationFactory()
        self.visual_effects["explosion"] = PlayerExplosion

        self.explosion_sound = sound_dict["player_death"]
        self.normal_shot_sound = sound_dict["shot"]
        self.laser_shot_sound = sound_dict["laser"]

        self.action = "idle"
        self.image = self.animation[self.action].image
        self.rect = self.image.get_rect()
        self.hitbox = self.image.get_rect()
        self.hitbox.width = 8
        self.hitbox.height = self.rect.height * 0.8
        self.movement_speed = 3

        self.ignore_shot_interval = True
        self.is_shot_triggered = False
        self.is_shot_allowed = True

        self.ignore_missile_interval = True
        self.is_missile_triggered = False
        self.is_missile_allowed = True

    def trigger_shot(self):
        self.is_shot_triggered = True

    def release_trigger(self):
        if self.current_weapon == "laser":
            self.laser_shot_sound.stop()
        self.is_shot_triggered = False

    def trigger_missile(self):
        self.is_missile_triggered = True

    def release_trigger_missile(self):
        self.is_missile_triggered = False

    def change_weapon(self, weapon):
        self.current_weapon = weapon
        self.shot_interval = self.weapon[self.current_weapon]["interval"]

    def change_second_weapon(self, weapon):
        self.current_second_weapon = weapon
        self.missile_interval = self.second_weapon[
            self.current_second_weapon]["interval"]

    @ schedule_instance_method_interval(
        "shot_interval", interval_ignorerer="ignore_shot_interval")
    def _shooting(self):
        if (self.is_shot_allowed and
                (len(self.shot_que) <
                 self.weapon[self.current_weapon]["max_num"])):
            if self.current_weapon == "normal":
                self.normal_shot_sound.play()
            elif self.current_weapon == "laser":
                if not pygame.mixer.get_busy():
                    self.laser_shot_sound.play()
            shot = self.weapon[self.current_weapon]["entity"](
                self, self.shot_que)
            shot.entity_container = self.entity_container
            shot.will_launch(Arrow.up)
            self.shot_que.append(shot)

    @ schedule_instance_method_interval(
        "missile_interval", interval_ignorerer="ignore_missile_interval")
    def _shooting_missile(self):
        if (self.is_missile_allowed and
                (len(self.missile_que) <
                 self.second_weapon[self.current_second_weapon]["max_num"])):
            if self.current_second_weapon == "normal":
                self.normal_shot_sound.play()
            missile = self.second_weapon[self.current_second_weapon]["entity"](
                self, self.missile_que)
            missile.entity_container = self.entity_container
            missile.will_launch(Arrow.up)
            self.missile_que.append(missile)

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

    def update(self, dt):
        if self.current_weapon == "laser":
            if pygame.mixer.get_busy():
                if len(self.shot_que) == 0:
                    self.laser_shot_sound.stop()
        if self.is_moving:
            self.move_on(dt)

        if self.shot_que:
            self.ignore_shot_interval = False
        else:
            self.ignore_shot_interval = True
        if self.is_shot_triggered:
            self._shooting()

        if self.missile_que:
            self.ignore_missile_interval = False
        else:
            self.ignore_missile_interval = True
        if self.is_missile_triggered:
            self._shooting_missile()

        self.do_animation(dt)

    def do_animation(self, dt):
        self.animation[self.action].update(dt)
        self.image = self.animation[self.action].image

    def death(self):
        if self in self.entity_container:
            explosion_effect = self.visual_effects["explosion"]
            explosion_effect.rect = self.rect
            explosion_effect.let_play_animation()
            self.gameworld.scene.visual_effects.append(explosion_effect)
            self.entity_container.kill_living_entity(self)
            self.explosion_sound.play()


class GameScene(Scene):

    gamefont = pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16)

    def __init__(self):
        super().__init__()
        self.gameworld = Level(AssetFilePath.level("stage1.json"), self)
        self.gameworld.set_background()
        self.gameworld.enemy_factory["scoutdisk"] = ScoutDiskEnemy
        self.player = Player()
        self.player.center_x_on_screen()
        self.player.y = w_size[1] - self.player.rect.height
        self.gameworld.entities.append(self.player)
        self.gamelevel_running = True
        textfactory.register_text(
            "tutorial", "z:主砲 x:ミサイル c:主砲切り替え v:やり直す")
        # self.gameworld.show_hitbox()

    def event(self, event):
        if event.type == pygame.KEYDOWN:
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
                self.player.trigger_missile()
            if event.key == pygame.K_v:
                self.reset_game()
            if event.key == pygame.K_c:
                if self.player.current_weapon == "normal":
                    self.player.change_weapon("laser")
                else:
                    self.player.change_weapon("normal")
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
            if event.key == pygame.K_x:
                self.player.release_trigger_missile()

    def stop_move_of_player_on_wall(self):
        if self.player.y < 0:
            self.player.stop_moving_to(Arrow.up)
        if w_size[1] - self.player.rect.height < self.player.y:
            self.player.stop_moving_to(Arrow.down)
        if w_size[0] - self.player.rect.width < self.player.x:
            self.player.stop_moving_to(Arrow.right)
        if self.player.x < 0:
            self.player.stop_moving_to(Arrow.left)

    def update(self, dt):
        textfactory.register_text(
            "gamescore", f"スコア:{self.gameworld.gamescore}")
        textfactory.register_text(
            "highscore", f"ハイスコア:{self.gameworld.highscore()}")
        textfactory.register_text(
            "elapsed_time_in_level",
            f"経過時間:{self.gameworld.elapsed_time_in_level}")
        if not self.gameworld.pause:
            self.gameworld.stop_entity_from_moving_off_screen(self.player)
            self.gameworld.run_level(dt)
            weapon_que = self.player.shot_que + self.player.missile_que
            self.gameworld.process_collision((self.player, ), weapon_que)
            if not (self.player in self.gameworld.entities):
                self.stop_game_and_show_result()
            self.gameworld.clear_enemies_off_screen()
            self.gameworld.scroll(dt)

    def reset_game(self):
        self.gameworld.pause = False
        self.gameworld.initialize_level()
        self.player.center_x_on_screen()
        self.player.y = w_size[1] - self.player.rect.height
        if self.player not in self.gameworld.entities:
            self.gameworld.entities.append(self.player)

    def stop_game_and_show_result(self):
        self.gameworld.pause = True
        self.gameworld.register_gamescore()

    def draw(self, screen):
        screen.blit(self.gameworld.bg_surf,
                    (0, self.gameworld.bg_scroll_y - w_size[1]))
        textfactory.render("tutorial", screen, (0, 0))
        textfactory.render("highscore", screen, (0, 16))
        textfactory.render("gamescore", screen, (0, 32))
        # textfactory.render("elapsed_time_in_level", screen, (0, 48))


class TitleMenuScene(Scene):
    def __init__(self):
        super().__init__()


def run(fps_num=fps):
    global fps
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
