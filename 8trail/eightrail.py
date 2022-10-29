import pygame

pygame.init()

clock = pygame.time.Clock()


class Player(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self, *args, **kwargs):
        # Call the parent class (Sprite) constructor
        super(Player, self).__init__(args, kwargs)
        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.Surface([32, 32])
        self.image.fill(pygame.Color("#6495ed"))
        self.rect = self.image.get_rect()

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.image, self.rect)


def init(window_size=(960, 640), caption=""):
    global screen
    global w_size
    w_size = window_size
    screen = pygame.display.set_mode((w_size[0], w_size[1]))
    pygame.display.set_caption(caption)


def run(fps=60):
    player = Player()
    player.rect.x = w_size[0] / 2
    player.rect.y = w_size[1] - player.rect.height
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.rect.x -= 1
                if event.key == pygame.K_RIGHT:
                    player.rect.x += 1
        screen.fill((0, 0, 0))
        player.draw(screen)
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()
