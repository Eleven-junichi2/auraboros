from src.auraboros.ui import UI, MenuInterface  # noqa


class ExampleUI(UI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calc_real_size = self._calc_real_size

    def _calc_real_size(self):
        return [32, 32]


class TestMenuInterface:
    def test_add_option(self):
        menu = MenuInterface()
        menu.add_option("test")
        assert menu.database.options.get("test", False)
        menu.add_option("test1", "This is test1")
        assert menu.database.options.get("test1", False)
        assert menu.database.options["test1"] == "This is test1"
