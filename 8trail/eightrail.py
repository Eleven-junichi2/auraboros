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


class AssetFilePath:
    root = Path(sys.argv[0]).parent / "assets"
    img_dirname = "imgs"
    sound_dirname = "sounds"

    @classmethod
    def img(cls, filename):
        return cls.root / cls.img_dirname / filename


class Player(pygame.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(args, kwargs)
        self.image = pygame.image.load(AssetFilePath.img("fighter_a.png"))
        self.rect = self.image.get_rect()
        self.flight_speed = 1

    def move(self, direction: Arrow):
        if direction is Arrow.up:
            self.rect.y -= self.flight_speed
        if direction is Arrow.down:
            self.rect.y += self.flight_speed
        if direction is Arrow.right:
            self.rect.x += self.flight_speed
        if direction is Arrow.left:
            self.rect.x -= self.flight_speed

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
    pygame.key.set_repeat(1, 1)


def run(fps=60):
    player = Player()
    player.rect.x = w_size[0] / 2 - player.rect.width
    player.rect.y = w_size[1] - player.rect.height
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                key = pygame.key.get_pressed()
                if key[pygame.K_UP]:
                    player.move(Arrow.up)
                if key[pygame.K_DOWN]:
                    player.move(Arrow.down)
                if key[pygame.K_LEFT]:
                    player.move(Arrow.left)
                if key[pygame.K_RIGHT]:
                    player.move(Arrow.right)
        screen.fill((0, 0, 0))
        player.draw(screen)
        # resize pixel size
        pygame.transform.scale(screen, w_size_unscaled,
                               pygame.display.get_surface())
        pygame.display.update()
        clock.tick(fps)
    pygame.quit()
