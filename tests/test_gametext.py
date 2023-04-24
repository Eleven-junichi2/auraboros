from src.auraboros.gametext import split_multiline_text, \
    line_count_of_multiline_text


def test_split_multiline_text():
    texts = split_multiline_text("AaBbCcDdEe\nFfGg\nHhIiJjKkLlMmNnOoPp", 12)
    assert texts[0] == "AaBbCcDdEe"
    assert texts[1] == "FfGg"
    assert texts[2] == "HhIiJjKkLlMm"
    assert texts[3] == "NnOoPp"
    # assert texts[1] == "HhIJj"


def test_line_count_of_multiline_text():
    height = line_count_of_multiline_text(
        "AaBbCcDdEe\nFfGg\nHhIiJjKkLlMmNnOoPp", 12)
    assert height == 4
