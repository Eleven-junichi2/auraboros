import pygame

from src.auraboros.gameinput import Keyboard

keyboard = Keyboard()


def test_register_keyaction():
    delay = 0
    interval = 0
    keyboard.register_keyaction(pygame.K_z, delay, interval, lambda: 2)
    assert callable(keyboard[pygame.K_z]["keydown"])
    assert callable(keyboard[pygame.K_z]["keydown"])
    assert keyboard[pygame.K_z]["delay"] == delay
    assert keyboard[pygame.K_z]["interval"] == interval


def test_do_action_by_keyinput():
    pygame.init()
    testing = True
    pygame.event.post(
        pygame.event.Event(
            pygame.KEYDOWN,
            {"unicode": "z", "key": 122, "mod": 4096, "scancode": 29}))
    while testing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                testing = False
            keyboard.event(event)
            # if event.type == pygame.KEYDOWN:
            #     print(event)
        assert keyboard.do_action_by_keyinput(pygame.K_z) == 2
        break
