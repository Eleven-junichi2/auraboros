import pytest

from src.auraboros.ui import GameMenuSystem, MenuHasNoItemError


class TestGameMenuSystem:
    gamemenu: GameMenuSystem

    @classmethod
    def setup_class(cls):
        cls.gamemenu1 = GameMenuSystem()
        cls.gamemenu1.add_menu_item("test1", lambda: True)
        cls.gamemenu1.add_menu_item("test2", lambda: False)
        cls.gamemenu2 = GameMenuSystem()

    @pytest.mark.run(order=1)
    def test_do_selected_action(self):
        assert self.gamemenu1.do_selected_action()

    @pytest.mark.run(order=2)
    def test_menu_cursor_down(self):
        self.gamemenu1.menu_cursor_down()
        assert self.gamemenu1.menu_selected_index == 1
        assert not self.gamemenu1.do_selected_action()

    @pytest.mark.run(order=3)
    def test_menu_cursor_up(self):
        self.gamemenu1.menu_cursor_up()
        assert self.gamemenu1.menu_selected_index == 0
        assert self.gamemenu1.do_selected_action()

    @pytest.mark.run(order=4)
    def test_replace_menu_item_by_index(self):
        self.gamemenu1.replace_menu_item_by_index(1, "replaced")
        assert self.gamemenu1.menu_option_keys[1] == "replaced"
        assert self.gamemenu1.menu_option_texts[1] == "replaced"

    @pytest.mark.run(order=5)
    def test_replace_menu_item_by_key(self):
        self.gamemenu1.replace_menu_item_by_key("replaced", "new")
        assert self.gamemenu1.menu_option_keys[1] == "new"
        assert self.gamemenu1.menu_option_texts[1] == "new"

    def test_do_action_when_menu_is_empty(self):
        with pytest.raises(MenuHasNoItemError):
            self.gamemenu2.do_selected_action()

    def test_add_menu_item(self):
        self.gamemenu2.add_menu_item("test1", lambda: True)
        assert self.gamemenu2.menu_option_keys == ["test1"]
        assert self.gamemenu2.menu_option_texts == ["test1"]
