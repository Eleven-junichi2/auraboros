from src.auraboros.gametext import (
    split_multiline_text,
    line_count_of_multiline_text,
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


def test_line_count_of_multiline_text():
    height = line_count_of_multiline_text("AaBbCcDdEe\nFfGg\nHhIiJjKkLlMmNnOoPp", 12)
    assert height == 4
    height = line_count_of_multiline_text("", 12)
    assert height == 1
    height = line_count_of_multiline_text(
        "AaBbCcDdEe\n\n\nFfGg\nHhIiJjKkLlMmNnOoPp", 12
    )
    # AaBbCcDdEe
    #
    #
    # FfGg
    # HhIiJjKkLlMm
    # NnOoPp
    assert height == 6
