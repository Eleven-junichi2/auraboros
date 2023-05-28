from auraboros.old_ui import UI, MenuInterface, MenuDatabase  # noqa


class ExampleUI(UI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calc_real_size = self._calc_real_size

    def _calc_real_size(self):
        return [32, 32]


class TestMenuDatabase:
    def test_option_count(self):
        menu = MenuInterface()
        menu.add_option("test1")
        menu.add_option("test2")
        menu.add_option("test3")
        assert menu.options_count == 3


class TestMenuInterface:
    def test_add_option(self):
        menu = MenuInterface()
        menu.add_option("test")
        assert menu.database.options.get("test", False)
        menu.add_option("test1", "This is test1")
        assert menu.database.options.get("test1", False)
        assert menu.database.options["test1"] == "This is test1"
        menu1 = MenuInterface(database=MenuDatabase())
        assert not menu1.database.options.get("test", False)

    def test_cursor_control(self):
        menu = MenuInterface(loop_cursor=True)
        menu.add_option("test1")
        menu.add_option("test2")
        menu.add_option("test3")
        assert menu.selected_index == 0
        assert menu.get_option_text() == "test1"
        menu.down_cursor()
        assert menu.selected_index == 1
        assert menu.get_option_text() == "test2"
        menu.down_cursor()
        assert menu.selected_index == 2
        assert menu.get_option_text() == "test3"
        menu.down_cursor()
        assert menu.selected_index == 0
        assert menu.get_option_text() == "test1"
        menu.up_cursor()
        assert menu.selected_index == 2
        assert menu.get_option_text() == "test3"
