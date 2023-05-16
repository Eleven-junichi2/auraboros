from src.auraboros.utils.string import (
    count_fullwidth_char,
    count_halfwidth_char,
    len_str_contain_fullwidth_char,
)


def test_count_fullwidth_char():
    assert count_fullwidth_char("abcdefgあいう") == 3


def test_count_halfwidth_char():
    assert count_halfwidth_char("abcdefgあいう") == 7


def test_len_str_contain_fullwidth_char():
    assert len_str_contain_fullwidth_char("abcdefgあいう") == 7 + 2 * 3
