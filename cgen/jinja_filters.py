from ast import literal_eval as ast_literal_eval

from .spec_types import Type


def case_input_split(input: str) -> list[str]:
    sep_c = "_"
    sep_l = [" ", "-"]
    for sep in sep_l:
        input = input.replace(sep, sep_c)
    return input.split(sep_c)


def j2_camel_case(input: str) -> str:
    first, *others = case_input_split(input)
    return "".join([first.lower(), *map(str.title, others)])


def j2_pascal_case(input: str) -> str:
    parts = map(str.title, case_input_split(input))
    return "".join(parts)


def j2_snake_case(input: str) -> str:
    parts = map(str.lower, case_input_split(input))
    return "_".join(parts)


def j2_title_case(input: str) -> str:
    return input.title()


def j2_base(input: str, base: int) -> str:
    if isinstance(input, int):
        if base == 2:
            return f"0b{input:b}"
        if base == 8:
            return f"0{input:o}"
        if base == 10:
            return f"{input:d}"
        if base == 16:
            return f"0x{input:X}"
        return f"{input}"
    return input


def j2_is_type(input):
    return isinstance(input, Type)


def j2_str_to_dict(input):
    return ast_literal_eval(input)