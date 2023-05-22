from pathlib import Path

from src.auraboros.utils.path import AssetFilePath

from src.auraboros.gametext import (
    split_multiline_text,
    Font2,
)

TESTS_ROOT_PATH = Path(__file__).parent.parent
AssetFilePath.set_root_dir(TESTS_ROOT_PATH / "assets")


class TestFont2:
    def test_charsize(self):
        font = Font2(AssetFilePath.get_asset("fonts/misaki_gothic.ttf"), 16)
        assert font.halfwidth_charsize()[0] * 2 == font.fullwidth_charsize()[0]

    def test_lines_and_sizes_of_multilinetext(self):
        font = Font2(AssetFilePath.get_asset("fonts/misaki_gothic.ttf"), 16)
        font.lines_and_sizes_of_multilinetext(
            "misaki_gothic is epiii\niiiic", is_window_size_default_for_length=False
        )


def test_split_multiline_text():
    texts = split_multiline_text("abcdefg", 20)
    assert len(texts) == 1
    texts = split_multiline_text("abcdefg\n", 20)
    assert len(texts) == 2
    texts = split_multiline_text("abcdefg\n\n\nhi\njk", 4)
    assert texts[0] == "abcd"
    assert texts[1] == "efg"
    assert texts[2] == ""
    assert texts[3] == ""
    assert texts[4] == "hi"
    texts = split_multiline_text("abcDEFghiJKLmnoPQRstuVWXyz\n\n\n01234\n", 12)
    assert texts[0] == "abcDEFghiJKL"
    assert texts[1] == "mnoPQRstuVWX"
    assert texts[2] == "yz"
    assert texts[3] == ""
    assert texts[4] == ""
    assert texts[5] == "01234"
    assert texts[6] == ""
    texts = split_multiline_text("", 3)
    assert texts[0] == ""
    texts = split_multiline_text("あああ\nいいい\nううう")
    assert texts[0] == "あああ"
    assert texts[1] == "いいい"
    assert texts[2] == "ううう"
