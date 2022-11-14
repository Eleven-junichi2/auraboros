from inspect import isclass
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
    def __init__(self, shooter_sprite: ShooterSprite,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load(AssetFilePath.img("shot1.png"))
        self.shooter = shooter_sprite
        self.rect = self.image.get_rect()
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
                self._destruct()

    def _destruct(self):
        """Remove sprite from group and que of shooter."""
        self.shooter.shot_que.remove(self)
        self.entity_container.kill_living_entity(self)
        self.is_launching = False

    def allow_shooter_to_fire(self):
        self.shooter.is_shot_allowed = True

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)

    def update(self, dt):
        if not self.is_launching:
            self.reset_pos_x()
            self.reset_pos_y()
        self._fire(dt)

    def collide(self, sprite):
        if pygame.sprite.collide_rect(self, sprite):
            self._destruct()


class PlayerLaser(PlayerShot):
    def __init__(self, shooter_sprite: ShooterSprite,
                 *args, **kwargs):
        super().__init__(shooter_sprite=shooter_sprite, *args, **kwargs)
        self.image = pygame.image.load(AssetFilePath.img("laser1.png"))
        self.shooter = shooter_sprite
        self.rect = self.image.get_rect()
        self.reset_pos_x()
        self.reset_pos_y()
        self.movement_speed = 6

    def move_on(self, dt):
        self.reset_pos_x()
        super().move_on(dt)


class PlayerMissile(PlayerShot):
    def __init__(self, shooter_sprite: ShooterSprite,
                 *args, **kwargs):
        super().__init__(shooter_sprite=shooter_sprite, *args, **kwargs)
        self.image = pygame.image.load(AssetFilePath.img("shot2.png"))
        self.shooter = shooter_sprite
        self.rect = self.image.get_rect()
        self.reset_pos_x()
        self.reset_pos_y()
        self.movement_speed = 2.5

    def move_on(self, dt):
        # if self.move_target_x and self.move_target_y:
        self.move_aim_to_enemy()
        super().move_on(dt)

    def _destruct(self):
        """Remove sprite from group and que of shooter."""
        self.shooter.missile_que.remove(self)
        self.entity_container.kill_living_entity(self)
        self.is_launching = False

    def allow_shooter_to_fire(self):
        self.shooter.is_missile_allowed = True

    def move_aim_to_enemy(self):
        is_exist_destination = self.set_destination_to_enemy()
        if not is_exist_destination:
            return
        if (self.move_target_x - self.movement_speed
            <= self.x <=
                self.move_target_x + self.movement_speed):
            self.direction_of_movement.unset(Arrow.right)
            self.direction_of_movement.unset(Arrow.left)
            self.set_destination_to_enemy()
        elif self.x < self.move_target_x:
            self.direction_of_movement.set(Arrow.right)
            self.direction_of_movement.unset(Arrow.left)
        elif self.move_target_x < self.x:
            self.direction_of_movement.set(Arrow.left)
            self.direction_of_movement.unset(Arrow.right)
        if (self.move_target_y - self.movement_speed
            <= self.y <=
                self.move_target_y + self.movement_speed):
            self.direction_of_movement.unset(Arrow.up)
            self.direction_of_movement.unset(Arrow.down)
            self.set_destination_to_enemy()
        elif self.y < self.move_target_y:
            self.direction_of_movement.set(Arrow.down)
            self.direction_of_movement.unset(Arrow.up)
        elif self.move_target_y < self.y:
            self.direction_of_movement.set(Arrow.up)
            self.direction_of_movement.unset(Arrow.down)

    def set_destination_to_enemy(self) -> bool:
        enemy_list = [entity for entity in self.gameworld.entities
                      if isinstance(entity, Enemy)]
        # if len(enemy_list) == 1:
        #     enemy = enemy_list[0]
        #     self.move_target_x = enemy.x
        #     self.move_target_y = enemy.y
        #     return True
        if len(enemy_list) >= len(self.shooter.missile_que):
            for i, missile in enumerate(self.shooter.missile_que):
                enemy = enemy_list[i]
                missile.move_target_x = enemy.x
                missile.move_target_y = enemy.y
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
        self.movement_speed = 2
        self.behavior_pattern = None
        self.behavior_pattern_dict[
            "strike_to_player"] = self.move_strike_to_player

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


class WeaponBulletFactory:
    def __init__(self, *args, **kwargs):
        self.__dict__: dict[Any, pygame.mixer.PlayerShot]
        self.__dict__.update(*args, **kwargs)

    def __getitem__(self, key) -> pygame.mixer.Sound:
        return self.__dict__[key]

    def __setitem__(self, key, value: pygame.mixer.Sound):
        if isclass(value):
            self.__dict__[key] = {}
            self.__dict__[key]["entity"] = value
            self.__dict__[key]["max_num"] = 1
            self.__dict__[key]["interval"] = 1
        else:
            raise ValueError("The value must not be instance.")

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


class Player(ShooterSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weapon = WeaponBulletFactory()
        self.weapon["normal"] = PlayerShot
        self.weapon["normal"]["max_num"] = 3
        self.weapon["normal"]["interval"] = 3
        self.weapon["laser"] = PlayerLaser
        self.weapon["laser"]["max_num"] = 6
        self.weapon["laser"]["interval"] = 4
        self.change_weapon("normal")

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
        self.movement_speed = 3

        self.shot_que: list = []
        self.ignore_shot_interval = True
        self.is_shot_triggered = False
        self.is_shot_allowed = True

        self.missile_que: list = []
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
            shot = self.weapon[self.current_weapon]["entity"](self)
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
                self)
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

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)

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

    def collide_with_enemy(self, enemy: Enemy) -> bool:
        if not isinstance(enemy, Enemy):
            raise TypeError("Given entity is not Enemy.")
        if pygame.sprite.collide_rect(enemy, self):
            self.death()
            return True


class GameScene(Scene):

    gamefont = pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16)
    instruction_text = gamefont.render(
        "z:主砲 x:ミサイル c:主砲切り替え v:やり直す", True, (255, 255, 255))

    def __init__(self):
        super().__init__()
        self.gameworld = Level(AssetFilePath.level("stage1.json"), self)
        self.gameworld.set_background()
        self.gameworld.enemy_factory["scoutdisk"] = ScoutDiskEnemy
        self.player = Player(self.gameworld.entities)
        self.player.center_x_on_screen()
        self.player.y = w_size[1] - self.player.rect.height
        # self.player.entity_container = self.gameworld.entities
        self.gameworld.entities.append(self.player)
        self.gamelevel_running = True
        self.gamescore_pos = (0, 16)
        self.scoreboard = []
        self.scoreboard_surflist = []
        self.scoreboard_textlist = []
        self.num_of_remaining_enemies = len(self.gameworld.level)

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

    def collide_player_weapon_with_enemy(self, enemy, weapon: PlayerShot):
        if enemy.collide(weapon):
            self.gameworld.gamescore += 10
            self.num_of_remaining_enemies -= 1
        weapon.collide(enemy)

    def update(self, dt):
        self.elapsed_time_text = self.gamefont.render(
            str(self.gameworld.elapsed_time_in_level), True, (255, 255, 255))
        self.gamescore_text = self.gamefont.render(
            "スコア:" + str(self.gameworld.gamescore), True, (255, 200, 255))
        num_of_remaining_enemies = self.num_of_remaining_enemies
        self.enemycounter_text = self.gamefont.render(
            f"敵機:{len(self.gameworld.enemies)}/{num_of_remaining_enemies}",
            True, (255, 255, 200))
        self.scoreboard_headline_text = self.gamefont.render(
            "-スコアボード-", True, (255, 200, 255))
        for enemy in self.gameworld.enemies:
            for shot in self.player.shot_que:
                self.collide_player_weapon_with_enemy(enemy, shot)
            for missile in self.player.missile_que:
                self.collide_player_weapon_with_enemy(enemy, missile)
            if self.player.collide_with_enemy(enemy):
                self.stop_game_and_show_result()
                self.gameworld.clear_enemies()
            enemy.collide(self.player)
            if enemy.y > w_size[1]:
                enemy.death()
        self.stop_move_of_player_on_wall()
        if self.gameworld.all_enemy_on_level_was_summoned:
            if len(self.gameworld.enemies) == 0 and self.gamelevel_running:
                self.stop_game_and_show_result()
        if self.gamelevel_running:
            self.gameworld.run_level()
            self.gameworld.scroll()

    def reset_game(self):
        self.gamelevel_running = True
        self.gameworld.initialize_level()
        self.gamescore_pos = (0, 16)
        self.player.center_x_on_screen()
        self.player.y = w_size[1] - self.player.rect.height
        if self.player not in self.gameworld.entities:
            self.gameworld.entities.append(self.player)
        self.num_of_remaining_enemies = len(self.gameworld.level)

    def stop_game_and_show_result(self):
        self.gamelevel_running = False
        self.gamescore_pos = (w_size[0] / 2, w_size[1] / 2)
        self.scoreboard.append(self.gameworld.gamescore)
        self.scoreboard.sort(reverse=True)
        if len(self.scoreboard) > 10:
            self.scoreboard.pop()
        self.scoreboard_surflist = []
        self.scoreboard_textlist = []
        for rank, score in enumerate(self.scoreboard):
            scoreboard_text = f"{rank+1}:{score}"
            score_surf = self.gamefont.render(
                scoreboard_text, True, (255, 200, 255))
            self.scoreboard_textlist.append(scoreboard_text)
            self.scoreboard_surflist.append(score_surf)

    def draw(self, screen):
        screen.blit(self.gameworld.bg_surf,
                    (0, self.gameworld.bg_scroll_y - w_size[1]))
        screen.blit(self.instruction_text, (0, 0))
        # screen.blit(self.elapsed_time_text, (0, 16))
        screen.blit(self.gamescore_text, self.gamescore_pos)
        screen.blit(self.enemycounter_text, (0, 16 * 2))
        screen.blit(self.scoreboard_headline_text,
                    (w_size[0] - self.gamefont.size("-スコアボード-")[0], 0))
        for i, text_surf in enumerate(self.scoreboard_surflist):
            screen.blit(
                text_surf,
                (w_size[0] - self.gamefont.size(
                    str(self.scoreboard_textlist[i]))[0], 16 + 16 * i))


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
