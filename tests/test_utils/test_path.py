from pathlib import Path

from src.auraboros.utils.path import AssetFilePath

TESTS_ROOT_PATH = Path(__file__).parent.parent


class TestAssetFilePath:
    def test_set_asset_root(self):
        AssetFilePath.set_root_dir(TESTS_ROOT_PATH / "assets")
        assert AssetFilePath.get_asset("fonts/misaki_gothic.ttf").exists()
