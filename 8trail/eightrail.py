from pathlib import Path
import sys
import pygame

pygame.init()

clock = pygame.time.Clock()


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

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)


def init(window_size=(960, 640), caption="", pixel_scale=2):
    global screen
    global w_size
    global w_size_unscaled
    pixel_scale = pixel_scale
    w_size_unscaled = window_size
    w_size = tuple([length // pixel_scale for length in window_size])
    pygame.display.set_mode(w_size_unscaled)
    screen = pygame.Surface(w_size)

    pygame.display.set_caption(caption)


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
                if event.key == pygame.K_UP:
                    player.rect.y -= 1
                if event.key == pygame.K_DOWN:
                    player.rect.y += 1
                if event.key == pygame.K_LEFT:
                    player.rect.x -= 1
                if event.key == pygame.K_RIGHT:
                    player.rect.x += 1

        screen.fill((0, 0, 0))
        player.draw(screen)
        # ↓ resize pixel size
        pygame.transform.scale(screen, w_size_unscaled,
                               pygame.display.get_surface())
        pygame.display.update()
        clock.tick(fps)
    pygame.quit()
