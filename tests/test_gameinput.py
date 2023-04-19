import pygame

from src.auraboros.gameinput import Keyboard


def keydown_(): return 2
def keyup_(): return 4


def test_register_keyaction():
    keyboard = Keyboard()
    delay = 0
    interval = 0
    first_interval = 0
    keyboard.register_keyaction(
        pygame.K_z, delay, interval, first_interval)
    assert callable(keyboard[pygame.K_z].keydown)
    assert callable(keyboard[pygame.K_z].keyup)
    assert keyboard[pygame.K_z].delay == delay
    assert keyboard[pygame.K_z].interval == interval
    assert keyboard[pygame.K_z].first_interval == interval


def test_do_action_by_keyinput():
    keyboard = Keyboard()
    delay = 0
    interval = 0
    first_interval = 0
    keyboard.register_keyaction(
        pygame.K_z, delay, interval, first_interval, keydown_, keyup_)
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
        assert keyboard.do_action_on_keyinput(pygame.K_z) == 2
        break
