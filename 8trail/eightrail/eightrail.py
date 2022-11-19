from collections import UserDict
from inspect import isclass
import math
# from typing import Any
# from .keyboard import Keyboard
from .entity import EntityList, Sprite, ShooterSprite, Enemy
from .gamelevel import Level
from .gamescene import Scene, SceneManager
from .gametext import TextSurfaceFactory
from .utilities import Arrow, ArrowToTurnToward, AssetFilePath, TextToDebug  # noqa
from .schedule import IntervalCounter, schedule_instance_method_interval
from .sound import SoundDict

import pygame

from .animation import (
    AnimationDict, AnimationImage, AnimationFactory, SpriteSheet
)

from .__init__ import init, w_size, screen, w_size_unscaled  # noqa

# TODO: Fix game reset bug

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


class TrumplaIdle(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("enemy_b.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 0, 16, 16), ]
        self.anim_interval = 5


class TrumplaRollLeft(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("enemy_b.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 16 * 3, 16, 16), ]
        self.anim_interval = 10


class TrumplaRollRight(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("enemy_b.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 16, 16, 16), ]
        self.anim_interval = 10


class EnemyShotAnim(AnimationImage):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = SpriteSheet(AssetFilePath.img("enemy_b.png"))
        self.anim_frames: list[pygame.surface.Surface] = [
            self.sprite_sheet.image_by_area(0, 0, 4, 4),
            self.sprite_sheet.image_by_area(0, 4, 4, 4),
            self.sprite_sheet.image_by_area(0, 4*2, 4, 4),
            self.sprite_sheet.image_by_area(0, 4*3, 4, 4), ]
        self.anim_interval = 6


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
        self.movement_speed = 4.5
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

    def update(self, dt):
        self.do_pattern(dt)
        if self.is_moving:
            self.action = "move"
        else:
            self.action = "idle"
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


class TrumplaEnemy(ScoutDiskEnemy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation = AnimationDict()
        self.animation["idle"] = TrumplaIdle()
        self.animation["roll_left"] = TrumplaRollLeft()
        self.animation["roll_right"] = TrumplaRollRight()
        self.image = self.animation[self.action].image
        self.rect = self.image.get_rect()
        self.hitbox = self.image.get_rect()
        self.hitbox.width = 10
        self.hitbox.height = 8
        self.movement_speed = 2.25
        self.gamescore = 10
        self.is_able_to_shot = True
        self.shot_interval = 75

    def update(self, dt):
        self.do_pattern(dt)
        if self.is_moving:
            if self.direction_of_movement.is_left:
                self.action = "roll_left"
            elif self.direction_of_movement.is_right:
                self.action = "roll_right"
        else:
            self.action = "idle"
        self.animation[self.action].let_continue_animation()
        self.image = self.animation[self.action].image
        self.animation[self.action].update(dt)
        self.launch_shot()

    @schedule_instance_method_interval("shot_interval")
    def launch_shot(self):
        player_list = [entity for entity in self.gameworld.entities
                       if isinstance(entity, Player)]
        if player_list:
            distance_to_player_list = []
            for player in player_list:
                distance_to_player_list.append(
                    math.sqrt(
                        (player.x - self.x) ** 2 + (player.y - self.y) ** 2))
            target_player = player_list[
                distance_to_player_list.index(min(distance_to_player_list))]
            if (self.is_able_to_shot and
                (abs(target_player.y - self.y) <= 150) and
                    (abs(target_player.x - self.x) <= self.rect.width * 4)):
                shot = EnemyShot()
                shot.x = self.x
                shot.y = self.y
                self.gameworld.entities.append(shot)
                shot.set_destination_to_entity(Player)


class EnemyShot(Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation = AnimationDict()
        self.animation["idle"] = EnemyShotAnim()
        self.animation["move"] = EnemyShotAnim()
        self.action = "move"
        self.image = self.animation[self.action].image
        self.rect = self.image.get_rect()
        self.hitbox = self.image.get_rect()
        self.hitbox.width = 2
        self.hitbox.height = 2
        self.invincible_to_entity = True
        self.movement_speed = 2
        self.behavior_pattern = "launching_aim_at_player"
        self.behavior_pattern_dict = {}
        self.behavior_pattern_dict[
            "launching_aim_at_player"] = self.move_launching_aim_at_player
        self.gamescore = 10

    def update(self, dt):
        self.do_pattern(dt)
        self.animation[self.action].let_continue_animation()
        self.image = self.animation[self.action].image
        self.animation[self.action].update(dt)

    def do_pattern(self, dt):
        if self.behavior_pattern is not None:
            self.behavior_pattern_dict[self.behavior_pattern](dt)
            self.move_on(dt)

    def move_launching_aim_at_player(self, dt):
        self.direction_of_movement.set(Arrow.down)
        self.direction_of_movement.unset(Arrow.up)
        # self.move_to_destination(dt, stop_when_arrived=False)


class WeaponBulletFactory(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if isclass(value):
            self.data[key] = {}
            self.data[key]["entity"]: PlayerShot(value) = value
            self.data[key]["max_num"] = 1
            self.data[key]["interval"] = 1
        else:
            raise ValueError("The value must not be instance.")


class Player(ShooterSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shot_que = EntityList()
        self.weapon = WeaponBulletFactory()
        self.weapon["normal"] = PlayerShot
        self.weapon["normal"]["max_num"] = 4
        self.weapon["normal"]["interval"] = 3
        self.weapon["laser"] = PlayerLaser
        self.weapon["laser"]["max_num"] = 6
        self.weapon["laser"]["interval"] = 4
        self.change_weapon("normal")

        self.missile_que = EntityList()
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
        self.is_shot_allowed = True

        self.ignore_missile_interval = True
        self.is_missile_allowed = True

    def change_weapon(self, weapon):
        self.current_weapon = weapon
        self.shot_interval = self.weapon[self.current_weapon]["interval"]

    def change_second_weapon(self, weapon):
        self.current_second_weapon = weapon
        self.missile_interval = self.second_weapon[
            self.current_second_weapon]["interval"]

    @ schedule_instance_method_interval(
        "shot_interval", interval_ignorerer="ignore_shot_interval")
    def shooting(self):
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

    def on_release_trigger(self):
        if self.current_weapon == "laser":
            self.laser_shot_sound.stop()

    @ schedule_instance_method_interval(
        "missile_interval", interval_ignorerer="ignore_missile_interval")
    def shooting_missile(self):
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

        if self.missile_que:
            self.ignore_missile_interval = False
        else:
            self.ignore_missile_interval = True

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gameworld = Level(AssetFilePath.level("debug1"), self)
        self.gameworld.set_background()
        self.gameworld.enemy_factory["scoutdisk"] = ScoutDiskEnemy
        self.gameworld.enemy_factory["trumpla"] = TrumplaEnemy
        self.init_player()
        self.gamelevel_running = True
        textfactory.register_text(
            "tutorial", "z:主砲 x:ミサイル c:主砲切り替え v:やり直す")
        # self.gameworld.show_hitbox()

    def init_player(self):
        self.player = Player()
        self.player.center_x_on_screen()
        self.player.y = w_size[1] - self.player.rect.height
        self.gameworld.entities.append(self.player)
        self.keyboard.register_keyaction(
            pygame.K_UP,
            0, 0,
            lambda: self.player.will_move_to(Arrow.up),
            lambda: self.player.stop_moving_to(Arrow.up))
        self.keyboard.register_keyaction(
            pygame.K_DOWN,
            0, 0,
            lambda: self.player.will_move_to(Arrow.down),
            lambda: self.player.stop_moving_to(Arrow.down))
        self.keyboard.register_keyaction(
            pygame.K_RIGHT,
            0, 0,
            lambda: self.player.will_move_to(Arrow.right),
            lambda: self.player.stop_moving_to(Arrow.right))
        self.keyboard.register_keyaction(
            pygame.K_LEFT,
            0, 0,
            lambda: self.player.will_move_to(Arrow.left),
            lambda: self.player.stop_moving_to(Arrow.left))
        self.keyboard.register_keyaction(
            pygame.K_z,
            4, 4,
            self.player.shooting, self.player.on_release_trigger)
        self.keyboard.register_keyaction(
            pygame.K_x,
            4, 4,
            self.player.shooting_missile)
        self.keyboard.register_keyaction(
            pygame.K_c,
            10, 10,
            self.switch_weapon)
        self.keyboard.register_keyaction(
            pygame.K_v,
            10, 10,
            self.reset_game)

    def switch_weapon(self):
        if self.player.current_weapon == "normal":
            self.player.change_weapon("laser")
        else:
            self.player.change_weapon("normal")

    def update(self, dt):
        textfactory.register_text(
            "gamescore", f"スコア:{self.gameworld.gamescore}")
        textfactory.register_text(
            "highscore", f"ハイスコア:{self.gameworld.highscore()}")
        textfactory.set_text_pos_to_right("highscore")
        textfactory.register_text(
            "num_of_enemy",
            f"敵:{self.gameworld.num_of_remaining_enemies}")
        textfactory.register_text(
            "elapsed_time_in_level",
            f"経過時間:{round(self.gameworld.elapsed_time_in_level)}")
        textfactory.register_text(
            "count_of_enemies_summoned",
            f"敵生成数:{self.gameworld.count_of_enemies_summoned}")

        self.keyboard.do_action_by_keyinput(pygame.K_v)
        if not self.gameworld.pause:
            self.keyboard.do_action_by_keyinput(pygame.K_UP)
            self.keyboard.do_action_by_keyinput(pygame.K_DOWN)
            self.keyboard.do_action_by_keyinput(pygame.K_RIGHT)
            self.keyboard.do_action_by_keyinput(pygame.K_LEFT)
            self.keyboard.do_action_by_keyinput(pygame.K_z)
            self.keyboard.do_action_by_keyinput(pygame.K_x)
            self.keyboard.do_action_by_keyinput(pygame.K_c)

            self.gameworld.stop_entity_from_moving_off_screen(self.player)

            if self.gameworld.count_of_enemies_summoned > 0:
                if (not (self.player in self.gameworld.entities) or
                        self.gameworld.num_of_remaining_enemies == 0):
                    self.stop_game_and_show_result()

            self.gameworld.run_level(dt)
            self.gameworld.process_collision(
                (self.player, ),
                self.player.shot_que + self.player.missile_que)

            self.gameworld.clear_enemies_off_screen()
            self.gameworld.scroll(dt)

    def reset_game(self):
        self.gameworld.pause = False
        self.gameworld.initialize_level()
        self.init_player()

    def stop_game_and_show_result(self):
        self.gameworld.pause = True
        self.gameworld.register_gamescore()

    def draw(self, screen):
        screen.blit(self.gameworld.bg_surf,
                    (0, self.gameworld.bg_scroll_y - w_size[1]))
        textfactory.render("tutorial", screen, (0, 0))
        textfactory.render("highscore", screen)
        textfactory.render("gamescore", screen, (0, 32))
        textfactory.render("num_of_enemy", screen, (0, 48))
        textfactory.render("elapsed_time_in_level", screen, (0, 64))
        textfactory.render("count_of_enemies_summoned", screen, (0, 80))


class OptionsScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textfactory.set_current_font("misaki_gothic")
        textfactory.register_text("title_start", "START")
        textfactory.register_text("title_options", "OPTIONS")
        textfactory.register_text("title_exit", "EXIT")
        textfactory.register_text("menu_cursor_>", ">")
        self.menu_cursor_pos = [0, 0]
        self.arrow_for_menu_cursor = ArrowToTurnToward()
        self.gamemenu = [2, 1, 0]
        self.index_of_menu_item_selected = 0
        self.keyboard.register_keyaction(
            pygame.K_UP,
            10, 10, self.go_up_menu_cursor)
        self.keyboard.register_keyaction(
            pygame.K_DOWN,
            10, 10, self.go_down_menu_cursor)
        self.keyboard.register_keyaction(
            pygame.K_z,
            0, 0, self.command_menu_item)

    def process_menu_cursor(self):
        if self.arrow_for_menu_cursor.is_up:
            self.go_up_menu_cursor()
        elif self.arrow_for_menu_cursor.is_down:
            self.go_down_menu_cursor()

    def go_up_menu_cursor(self):
        if 0 < self.index_of_menu_item_selected:
            self.menu_cursor_pos[1] -= 16
            self.index_of_menu_item_selected -= 1

    def go_down_menu_cursor(self):
        if self.index_of_menu_item_selected < len(self.gamemenu) - 1:
            self.menu_cursor_pos[1] += 16
            self.index_of_menu_item_selected += 1

    def command_menu_item(self):
        self.manager.transition_to(
            self.gamemenu[self.index_of_menu_item_selected])

    def update(self, dt):
        self.keyboard.do_action_by_keyinput(pygame.K_UP)
        self.keyboard.do_action_by_keyinput(pygame.K_DOWN)
        self.keyboard.do_action_by_keyinput(pygame.K_z)
        self.process_menu_cursor()

    def draw(self, screen):
        textfactory.render("option_switch_debug", screen, (16, 0))
        textfactory.render("title_options", screen, (16, 16))
        textfactory.render("return", screen, (16, 32))
        textfactory.render("menu_cursor_>", screen, self.menu_cursor_pos)


class TitleMenuScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textfactory.set_current_font("misaki_gothic")
        textfactory.register_text("title_start", "START")
        textfactory.register_text("title_options", "OPTIONS")
        textfactory.register_text("title_exit", "EXIT")
        textfactory.register_text("menu_cursor_>", ">")
        self.menu_cursor_pos = [0, 0]
        self.arrow_for_menu_cursor = ArrowToTurnToward()
        self.gamemenu = [2, 1, 0]
        self.index_of_menu_item_selected = 0
        self.keyboard.register_keyaction(
            pygame.K_UP,
            10, 10, self.go_up_menu_cursor)
        self.keyboard.register_keyaction(
            pygame.K_DOWN,
            10, 10, self.go_down_menu_cursor)
        self.keyboard.register_keyaction(
            pygame.K_z,
            0, 0, self.command_menu_item)

    def process_menu_cursor(self):
        if self.arrow_for_menu_cursor.is_up:
            self.go_up_menu_cursor()
        elif self.arrow_for_menu_cursor.is_down:
            self.go_down_menu_cursor()

    def go_up_menu_cursor(self):
        if 0 < self.index_of_menu_item_selected:
            self.menu_cursor_pos[1] -= 16
            self.index_of_menu_item_selected -= 1

    def go_down_menu_cursor(self):
        if self.index_of_menu_item_selected < len(self.gamemenu) - 1:
            self.menu_cursor_pos[1] += 16
            self.index_of_menu_item_selected += 1

    def command_menu_item(self):
        self.manager.transition_to(
            self.gamemenu[self.index_of_menu_item_selected])

    def update(self, dt):
        self.keyboard.do_action_by_keyinput(pygame.K_UP)
        self.keyboard.do_action_by_keyinput(pygame.K_DOWN)
        self.keyboard.do_action_by_keyinput(pygame.K_z)
        self.process_menu_cursor()

    def draw(self, screen):
        textfactory.render("title_start", screen, (16, 0))
        textfactory.render("title_options", screen, (16, 16))
        textfactory.render("title_exit", screen, (16, 32))
        textfactory.render("menu_cursor_>", screen, self.menu_cursor_pos)


def run(fps_num=fps):
    global fps
    fps = fps_num
    running = True
    scene_manager = SceneManager()
    scene_manager.push(TitleMenuScene(scene_manager))
    scene_manager.push(OptionsScene(scene_manager))
    scene_manager.push(GameScene(scene_manager))
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
