from pathlib import Path

from src.auraboros.ui import ButtonUI, UIFlowLayout, UI
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
