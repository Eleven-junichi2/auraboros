import pygame

pygame.init()

clock = pygame.time.Clock()


def init(window_size=(1200, 800), caption=""):
    global screen
    screen = pygame.display.set_mode((window_size[0], window_size[1]))
    pygame.display.set_caption(caption)


def run(fps=60):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()
