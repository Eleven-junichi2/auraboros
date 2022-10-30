from dataclasses import dataclass
from pathlib import Path
import sys
import pygame

pygame.init()

clock = pygame.time.Clock()


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

    def arrow_keys_from_event(event_key):
        key_text = f"↑{event_key == pygame.K_UP}"
        key_text += f"↓{event_key == pygame.K_DOWN}"
        key_text += f"←{event_key == pygame.K_LEFT}"
        key_text += f"→{event_key == pygame.K_RIGHT}"
        return key_text


class PlayerShot(pygame.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.image = pygame.image.load(AssetFilePath.img("shot1.png"))
        self.rect = self.image.get_rect()
        self.shooting_speed = 5

    def move(self, direction: Arrow):
        if direction is Arrow.up:
            self.rect.y -= self.shooting_speed
        if direction is Arrow.down:
            self.rect.y += self.shooting_speed

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.image = pygame.image.load(AssetFilePath.img("fighter_a.png"))
        self.shot_sprite = PlayerShot()
        self.rect = self.image.get_rect()
        self.flight_speed = 1
        self.direction_of_movement = ArrowToTurnToward()

    def will_move_to(self, direction: Arrow):
        self.direction_of_movement.set(direction)

    def stop_moving_to(self, direction: Arrow):
        self.direction_of_movement.unset(direction)

    def move_on(self):
        if self.direction_of_movement.is_up:
            self.rect.y -= self.flight_speed
        if self.direction_of_movement.is_down:
            self.rect.y += self.flight_speed
        if self.direction_of_movement.is_right:
            self.rect.x += self.flight_speed
        if self.direction_of_movement.is_left:
            self.rect.x -= self.flight_speed

    def shot(self, screen):
        self.shot_sprite.draw(screen)

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)


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
                key = pygame.key.get_pressed()
                debugtext1 = gamefont.render(
                    TextToDebug.arrow_keys(key=key), True, (255, 255, 255))
                if event.key == pygame.K_UP:
                    player.will_move_to(Arrow.up)
                if event.key == pygame.K_DOWN:
                    player.will_move_to(Arrow.down)
                if event.key == pygame.K_RIGHT:
                    player.will_move_to(Arrow.right)
                if event.key == pygame.K_LEFT:
                    player.will_move_to(Arrow.left)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    player.stop_moving_to(Arrow.up)
                if event.key == pygame.K_DOWN:
                    player.stop_moving_to(Arrow.down)
                if event.key == pygame.K_RIGHT:
                    player.stop_moving_to(Arrow.right)
                if event.key == pygame.K_LEFT:
                    player.stop_moving_to(Arrow.left)
        player.move_on()
        screen.blit(debugtext1, (0, 0))
        player.draw(screen)
        # resize pixel size
        pygame.transform.scale(screen, w_size_unscaled,
                               pygame.display.get_surface())
        pygame.display.update()
        clock.tick(fps)
    pygame.quit()
