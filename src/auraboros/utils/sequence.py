from typing import Sequence, Union, Any

import re


def is_flat(sequence: Union[list, tuple, Sequence], consider_str_as_sequence=True):
    """This func used to check whether a given Sequence value is flat."""
    for item in sequence:
        if isinstance(item, Sequence):
            if not consider_str_as_sequence and isinstance(item, str):
                continue
            return False
    return True


def is_typed_sequence(type_: type, sequence: Sequence):
    """
    This function is used to check whether the elements of a given Sequence are of the
    same type.
    """
    return all(
        [
            all([isinstance(item, type_) for item in sequence])
            if isinstance(sequence, Sequence)
            else False
        ]
    )


def joint_stritems_by_indexpair_list(
    str_sequence: Sequence[str],
    indexpair_list: Sequence[tuple[int, int]],
) -> list[str]:
    result = []
    MAX_INDEX = len(str_sequence) - 1
    step_to_joint = 0
    for index_a, index_b in indexpair_list:
        if (index_a or index_b) > MAX_INDEX or (index_a or index_b) < 0:
            raise ValueError("Index out of range")
        parts_not_to_be_joint = str_sequence[step_to_joint:index_a]
        result += [*parts_not_to_be_joint]
        step_to_joint = index_b + 1
        jointed_parts = str_sequence[index_a] + str_sequence[index_b]
        result += [jointed_parts]
    else:
        result += str_sequence[step_to_joint:]
    return result


def search_consecutive_pairs_of_list(
    sequence: Sequence,
    item_a,
    item_b,
    regular_expression: bool = False,
) -> tuple[list[tuple[Any, Any]], list[tuple[int, int]]]:
    """
    item_a and item_b are considered regular expression patterns
    if regular_expression is True.
    Returns:
        tuple[list[tuple[Any, Any]], list[tuple[int, int]]]:
            list[tuple[Any, Any]]:
                this is list of found consecutive item pairs,
            list[tuple[int, int]]:
                this is list of consecutive index pairs.
    """
    if len(sequence) < 2:
        ValueError("count_consecutive_items must have at least 2 items")
    if regular_expression:
        if not (isinstance(item_a, str) or isinstance(item_b, str)):
            ValueError(" item_a and item_b must be str if regular_expression is True")
        if not all([isinstance(item, str) for item in sequence]):
            ValueError(
                "type of items of 'sequence' must be str if regular_expression is True"
            )
    indexpair_list = []
    itempair_list = []
    for index, item in enumerate(sequence):
        if index > 0:
            if regular_expression:
                if re.match(item_a, sequence[index - 1]) and re.match(item_b, item):
                    indexpair_list.append((index - 1, index))
                    itempair_list.append((sequence[index - 1], item))
            else:
                if sequence[index - 1] == item_a and item == item_b:
                    indexpair_list.append((index - 1, index))
                    itempair_list.append((sequence[index - 1], item))
    if itempair_list == []:
        itempair_list = None
    if indexpair_list == []:
        indexpair_list = None
    return itempair_list, indexpair_list


def joint_stritems_in_range_a_to_b(
    str_sequence: Sequence[str],
    index_a: int,
    index_b: int,
) -> list[str]:
    jointed_list = []
    MAX_INDEX = len(str_sequence) - 1
    if (index_a or index_b) > MAX_INDEX or (index_a or index_b) < 0:
        raise ValueError(
            f"Index out of range: index_a and index_b must be between 0 and {MAX_INDEX}"
        )
    for index, str_ in enumerate(str_sequence):
        if index < index_a:
            jointed_list.append(str_)
        elif index < index_b:
            str_to_append = ""
            for index_ in range(index_a, index_b + 1):
                str_to_append += str_sequence[index_]
            jointed_list.append(str_to_append)
    return jointed_list
