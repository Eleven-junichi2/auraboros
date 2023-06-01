from pathlib import Path

from src.auraboros.ui import (
    ButtonUI,
    UIFlowLayout,
    UI,
    MenuInterface,
    Option,
    TextUI,
    MenuUI,
)
from src.auraboros.gametext import GameText, Font2
from src.auraboros.utils.path import AssetFilePath

TESTS_ROOT_PATH = Path(__file__).parent.parent
AssetFilePath.set_root_dir(TESTS_ROOT_PATH / "assets")


class TestButtonUI:
    @staticmethod
    def test_making_instance():
        GameText.setup_font(
            Font2(AssetFilePath.get_asset("fonts/misaki_gothic.ttf"), 16), "testfont"
        )
        btn = ButtonUI([0, 0], GameText("test"), lambda: print("test"))
        assert btn.parts.calc_min_size
        assert btn.parts.calc_real_size


class TestFlowLayout:
    @staticmethod
    def test_calc_positions_for_children():
        flowlayout = UIFlowLayout([0, 0])
        flowlayout.add_child(UI([0, 0], [11, 11]))
        flowlayout.add_child(UI([0, 0], [11, 22]))
        flowlayout.add_child(UI([0, 0], [11, 33]))
        result = flowlayout.calc_positions_for_children()
        assert result[0] == (0, 0)
        assert result[1] == (0, 11)
        assert result[2] == (0, 33)

    @staticmethod
    def test_reposition_children():
        flowlayout = UIFlowLayout([0, 0], spacing=10)
        flowlayout.add_child(UI([0, 0], [11, 10]))
        flowlayout.add_child(UI([0, 0], [11, 20]))
        flowlayout.add_child(UI([0, 0], [11, 30]))
        flowlayout.reposition_children()
        assert flowlayout.children[0].parts.pos == [0, 0]
        assert flowlayout.children[1].parts.pos == [0, 20]
        assert flowlayout.children[2].parts.pos == [0, 50]

    @staticmethod
    def test_calc_entire_realsize():
        flowlayout = UIFlowLayout([0, 0], spacing=10)
        flowlayout.add_child(UI([0, 0], [11, 10]))
        flowlayout.add_child(UI([0, 0], [11, 20]))
        flowlayout.add_child(UI([0, 0], [11, 30]))
        flowlayout.reposition_children()
        assert flowlayout.calc_entire_realsize() == (11, 80)
        assert flowlayout.parts.real_size == (11, 80)


class TestMenuInterface:
    @staticmethod
    def test_add_option():
        interface = MenuInterface()
        interface.add_option(Option(TextUI("test1"), "test1"))
        interface.add_option(Option(TextUI("test2"), "test2"))
        assert interface.database.options[0].ui.parts.gametext == "test1"
        assert interface.database.options[1].ui.parts.gametext == "test2"

    @staticmethod
    def test_up_cursor():
        interface = MenuInterface()
        interface.add_option(Option(TextUI("test1"), "test1"))
        interface.add_option(Option(TextUI("test2"), "test2"))
        interface.add_option(Option(TextUI("test3"), "test3"))
        assert interface.current_selected.ui.parts.gametext == "test1"
        interface.up_cursor()
        assert interface.current_selected.ui.parts.gametext == "test3"
        interface.up_cursor()
        assert interface.current_selected.ui.parts.gametext == "test2"

    @staticmethod
    def test_down_cursor():
        interface = MenuInterface()
        interface.add_option(Option(TextUI("test1"), "test1"))
        interface.add_option(Option(TextUI("test2"), "test2"))
        interface.add_option(Option(TextUI("test3"), "test3"))
        assert interface.current_selected.ui.parts.gametext == "test1"
        interface.down_cursor()
        assert interface.current_selected.ui.parts.gametext == "test2"
        interface.down_cursor()
        assert interface.current_selected.ui.parts.gametext == "test3"

    @staticmethod
    def test_do_func_on_select():
        a = [1, 2, 3]
        interface = MenuInterface()
        interface.add_option(
            Option(TextUI("test1"), "test1", on_select=lambda: a.clear())
        )
        interface.do_func_on_select()
        assert a == []

    @staticmethod
    def test_do_func_on_highlight():
        a = [1, 2, 3]
        interface = MenuInterface()
        interface.add_option(
            Option(TextUI("test1"), "test1", on_highlight=lambda: a.clear())
        )
        interface.do_func_on_highlight()
        assert a == []

    @staticmethod
    def test_remove_option():
        interface = MenuInterface()
        test3 = Option(TextUI("test3"), "test3")
        interface.add_option(Option(TextUI("test1"), "test1"))
        interface.add_option(Option(TextUI("test2"), "test2"))
        interface.add_option(test3)
        interface.remove_option(1)
        assert len(interface.database.options) == 2
        assert interface.database.dict_from_options["test1"].key == "test1"
        assert interface.database.dict_from_options["test3"].key == "test3"
        assert interface.database.options[0].key == "test1"
        assert interface.database.options[1].key == "test3"
        interface.remove_option("test1")
        assert len(interface.database.options) == 1
        interface.remove_option(test3)
        assert len(interface.database.options) == 0


class TestMenuUI:
    @staticmethod
    def test_add_option():
        menu = MenuUI()
        menu.add_option(Option(TextUI("test1"), "test1"))
        assert menu.children[0]
