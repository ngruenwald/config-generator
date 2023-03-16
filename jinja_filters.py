from spec_types import Type


def case_input_split(input):
    SEP_C = '_'
    SEP_L = [' ', '-']
    for sep in SEP_L:
        input = input.replace(sep, SEP_C)
    return input.split(SEP_C)


def j2_camel_case(input):
    first, *others = case_input_split(input)
    return ''.join([first.lower(), *map(str.title, others)])


def j2_pascal_case(input):
    parts = map(str.title, case_input_split(input))
    return ''.join(parts)


def j2_snake_case(input):
    parts = map(str.lower, case_input_split(input))
    return '_'.join(parts)


def j2_title_case(input):
    return input.title()


def j2_base(input, base):
    if isinstance(input, int):
        if base == 2:
            return f'0b{input:b}'
        if base == 8:
            return f'0{input:o}'
        if base == 10:
            return f'{input:d}'
        if base == 16:
            return f'0x{input:X}'
        return f'{input}'
    return input


def j2_is_type(input):
    return isinstance(input, Type)
