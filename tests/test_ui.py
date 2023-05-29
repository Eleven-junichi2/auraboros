from pathlib import Path

from auraboros.ui import ButtonUI
from auraboros.gametext import GameText, Font2
from auraboros.utils.path import AssetFilePath

TESTS_ROOT_PATH = Path(__file__).parent.parent
AssetFilePath.set_root_dir(TESTS_ROOT_PATH / "assets")


class TestButtonUI:
    def test_making_instance(self):
        GameText.setup_font(
            Font2(AssetFilePath.get_asset("fonts/misaki_gothic.ttf"), 16), "testfont"
        )
        btn = ButtonUI([0, 0], GameText("test"), lambda: print("test"))
        assert btn.parts.calc_min_size
        assert btn.parts.calc_real_size
