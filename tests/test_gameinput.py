import pygame

from src.auraboros.gameinput import Keyboard, Mouse


class TestKeyboard:

    @staticmethod
    def keydown_(): return 2

    @staticmethod
    def keyup_(): return 4

    @staticmethod
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

    def test_do_action_by_keyinput(self):
        keyboard = Keyboard()
        delay = 0
        interval = 0
        first_interval = 0
        keyboard.register_keyaction(
            pygame.K_z, delay, interval, first_interval,
            self.keydown_, self.keyup_)
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


class TestMouse:

    @staticmethod
    def on_mouse_left(): return 1

    @staticmethod
    def on_mouse_right(): return 3

    @staticmethod
    def on_mouse_wheel_down(): return 5

    def test__init__(self):
        mouse = Mouse()
        keys_event_type = ("down", "up", "motion")
        keys_event_btn = ("left", "middle", "right", "wheel_up", "wheel_down")
        for key in keys_event_type:
            for i, key_ in enumerate(keys_event_btn):
                if key == "motion" and i >= 3:
                    continue
                assert mouse._funcs_on_event[key][key_]() is None

    def test_register_mouseaction(self):
        mouse = Mouse()
        mouse.register_mouseaction(
            pygame.MOUSEBUTTONDOWN, on_left=self.on_mouse_left)
        assert mouse._funcs_on_event["down"]["left"]() == 1
        mouse.register_mouseaction(
            "up", on_right=self.on_mouse_right)
        mouse.register_mouseaction(
            "motion", on_right=self.on_mouse_right,
            on_wheel_down=self.on_mouse_wheel_down)
        assert mouse._funcs_on_event["up"]["right"]() == 3
        try:
            mouse._funcs_on_event["motion"]["wheel_down"]()
        except KeyError:
            assert True
