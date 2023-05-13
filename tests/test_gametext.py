from src.auraboros.gametext import (
    split_multiline_text,
    line_count_of_multiline_text,
)


def test_split_multiline_text():
    texts = split_multiline_text("abcDEFghiJKLmnoPQRstuVWXyz\n\n\n01234\n", 12)
    print(texts)
    assert texts[0] == "abcDEFghiJKL"
    assert texts[1] == "mnoPQRstuVWX"
    assert texts[2] == "yz"
    assert texts[3] == ""
    assert texts[4] == ""
    assert texts[5] == ""
    assert texts[6] == "01234"
    assert texts[7] == ""
    texts = split_multiline_text("", 12)
    assert texts[0] == ""


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
