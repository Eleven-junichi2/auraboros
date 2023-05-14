from src.auraboros.utilities import (
    is_flat,
    joint_stritems_in_range_a_to_b,
    joint_two_stritems_by_indexpair_list,
    search_consecutive_pairs_of_list,
    is_typed_sequence,
)


def test_is_typed_sequence():
    assert is_typed_sequence(int, [1, 3, 7])
    assert not is_typed_sequence(int, [1, "abc", 7])


def test_search_consecutive_pairs_of_list():
    itempair_list, indexpair_list = search_consecutive_pairs_of_list(
        sequence=("abcdefg", "\n", "\n", "\n", "abc", "\n", "DEFG", "\n"),
        item_a="\n",
        item_b="[^\n]",
        regular_expression=True,
    )
    assert indexpair_list[0] == (3, 4)
    assert itempair_list[0] == ("\n", "abc")
    assert indexpair_list[1] == (5, 6)
    assert itempair_list[1] == ("\n", "DEFG")


def test_joint_stritems_in_range_a_to_b():
    assert joint_stritems_in_range_a_to_b(
        str_sequence=("abcdefg", "\n", "\n", "\n", "hi"), index_a=3, index_b=4
    ) == ["abcdefg", "\n", "\n", "\nhi"]


def test_joint_two_stritems_by_indexpair_list():
    assert joint_two_stritems_by_indexpair_list(
        str_sequence=("abcdefg", "\n", "\n", "\n", "abc", "\n", "DEFG", "\n"),
        indexpair_list=((3, 4), (5, 6)),
    ) == ["abcdefg", "\n", "\n", "\nabc", "\nDEFG", "\n"]


def test_is_flat():
    assert not is_flat([(0, 1), "abc", 3, 22])
    assert is_flat((0, 1, 2))
    assert is_flat(["abcdefg"], consider_str_as_sequence=False)
    assert not is_flat([["abcdefg", ""], "\n", "\n", ["hi"]])
