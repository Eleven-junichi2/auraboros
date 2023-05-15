import unicodedata


def is_char_fullwidth(char: str):
    if unicodedata.east_asian_width(char) in ("F", "W", "A"):
        return True
    else:
        return False


def len_str_contain_fullwidth_char(str_: str) -> int:
    """
    This function considers the length of full-width characters to be twice the length
    of half-width characters.
    """
    return sum(2 if is_char_fullwidth(char) else 1 for char in str_)


def count_fullwidth_char(str_: str):
    return len(tuple(filter(is_char_fullwidth, str_)))


def count_halfwidth_char(str_: str):
    return len(tuple(filter(lambda char: not is_char_fullwidth(char), str_)))
