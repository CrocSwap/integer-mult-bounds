"""Independent closed invoices for the unchanged pooled route_packet wrapper."""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def positive(value):
    require(type(value) is int and value > 0, "positive integer cardinality")


def countdown(value):
    """PR2877's fully drained canonical Counter bill, without pool acquisition."""
    positive(value)
    return 15 * value + 14 * value.bit_length() - 5 * value.bit_count() + 36


def suffix_probe(value):
    positive(value)
    if value % 2 == 0:
        return 4
    return 15 if value > 1 and value % 4 == 1 else 12


def copy_rows(highs, fibre):
    """Include all nested countdowns and one blank read per scratch acquisition."""
    positive(highs)
    positive(fibre)
    per_slice = suffix_probe(fibre) + 5 * fibre
    if fibre > 1:
        per_slice += countdown(fibre) + 1
    return countdown(highs) + 1 + highs * per_slice


def wrapper(prefixes, highs, fibre, disposed=False):
    positive(prefixes)
    positive(highs)
    positive(fibre)
    require(type(disposed) is bool, "disposal mode")
    cube = highs * fibre
    result = prefixes * (2 * copy_rows(highs, fibre) + 18 * cube + 19)
    result += countdown(prefixes) + 12
    if disposed:
        result += 5 * prefixes * cube + 7
    return result


def predict(single, prefixes, disposed=False, cube_bits=0):
    """Exact prefix law when the complete cube trace is invariant across prefixes."""
    require(type(single) is int and single > countdown(1) + 12, "single-prefix bill")
    positive(prefixes)
    require(type(disposed) is bool, "disposal mode")
    result = prefixes * (single - countdown(1) - 12) + countdown(prefixes) + 12
    if disposed:
        positive(cube_bits)
        result += 5 * prefixes * cube_bits + 7
    return result
