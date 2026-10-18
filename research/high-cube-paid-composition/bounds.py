"""Paid high-cube composition; exact setup equations credited to PR3265.

The 4096 ADD, 530 scaling and 2048 plain-sign bounds are predecessor
results. New transfer bounds retain every pooled and native call boundary.
Krzysztof Wójt with substantial OpenAI Codex assistance; Apache-2.0.
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def positive(value):
    require(type(value) is int and value > 0, "positive integer")
    return value


def digits(value):
    require(type(value) is int and value >= 0, "nonnegative integer")
    return max(1, value.bit_length())


def countdown(value, width=None):
    width = digits(value) if width is None else width
    require(type(width) is int and width >= digits(value), "counter width")
    if value == 0:
        return 14 * width + 40
    return 15 * value + 14 * width - 5 * value.bit_count() + 36


def close_count(value):
    return 5 * digits(value) + 12


def product(left, right):
    """PR3265's exact, asymmetric Count.product invoice, including probes."""
    positive(left)
    positive(right)
    total = 19 * digits(left) + 21 * digits(right) + 151
    current = 0
    for digit in bin(right)[2:]:
        bit = int(digit)
        total += 3 + (1 - bit) + (11 if current == 0 else 6 * digits(current) + 9)
        if bit:
            total += 23 * digits(left) + 2 * digits(2 * current) + 9 * digits(2 * current + left) + 50
        current = 2 * current + bit * left
    return total


def power(modulus, exponent):
    positive(modulus)
    require(type(exponent) is int and exponent >= 0, "compiled exponent")
    total, result, factor = 87 + 14 * digits(modulus), 1, modulus
    while exponent:
        if exponent & 1:
            total += product(result, factor) + close_count(result)
            result *= factor
        exponent >>= 1
        if exponent:
            total += product(factor, factor) + close_count(factor)
            factor *= factor
    return total + close_count(factor)


def extent(modulus, fibre, fields, operation):
    kind, first, *arguments = operation
    if kind in ("add", "swap"):
        first, second = sorted((first, arguments[0]))
        exponents = (first, second - first - 1, fields - second - 1)
    else:
        exponents = (first, fields - first - 1)
    values = tuple(modulus**exponent for exponent in exponents)
    return (
        sum(power(modulus, exponent) for exponent in exponents)
        + product(values[-1], fibre)
        + sum(close_count(value) for value in values)
        + close_count(values[-1] * fibre)
    )


def census(operations):
    counts = dict(add=0, scale=0, negate=0, translate=0, swap=0, reversed_add=0)
    for kind, target, *arguments in operations:
        if kind in ("double", "half"):
            counts["scale"] += 1
        else:
            require(kind in counts and kind != "reversed_add", "closed factor alphabet")
            counts[kind] += 1
        if kind == "add" and arguments[0] > target:
            counts["reversed_add"] += 1
    counts["native_calls"] = counts["swap"] + 2 * counts["reversed_add"]
    return counts


def exact_setup(modulus, fibre, dimension, input_width, roles, operations, copy_rows):
    """PR3265 equation, excluding whole direct kernels and swap adapters."""
    require(modulus != 1 or not operations, "Q=1 has an empty active sequence")
    highs = modulus ** (dimension * dimension)
    volume = highs * fibre
    total = copy_rows(highs, fibre) + 4 * volume + 27 * input_width + digits(modulus) + 61
    if modulus == 1:
        return total
    counts = census(operations)
    total += 10 * roles + 65 * digits(modulus) + 159
    total += sum(extent(modulus, fibre, dimension * dimension, op) for op in operations)
    total += (len(operations) + 2 * counts["reversed_add"]) * (5 * volume + 7)
    return total


def sign_acquisitions(modulus, before, suffix):
    require(modulus >= 3 and before >= 1 and suffix >= 1, "sign domain")
    return 2 + before * (4 * modulus - 5) + (suffix > 1) * before * modulus


def translation_bound(modulus, before, suffix):
    """Derived loop majorant for pooled translate_one (PROOF.md)."""
    positive(before)
    positive(suffix)
    require(modulus >= 3, "active high modulus")
    width = digits(modulus) + 1
    volume = before * modulus * suffix
    # Fixed-width subtraction/free, three constructor probes, two outer
    # countdowns, four complete block-copy calls per outer row, payload scans.
    pair = countdown(modulus - 1, width) + countdown(1, width) + 2
    per_suffix = countdown(suffix, digits(suffix) + 1) + 1 if suffix > 1 else 0
    return (
        200 * (width + 1) + 3
        + 2 * (countdown(before, digits(before) + 1) + 1)
        + 2 * before * (pair + 30 + 5 * modulus * suffix + modulus * per_suffix)
        + 13 * volume + 29
    )


def nonnative_bound(modulus, fibre, dimension, input_width, roles, operations):
    """Full cube bill less the complete native.run intervals; not native=0."""
    require(modulus != 1 or not operations, "Q=1 has an empty active sequence")
    volume = modulus ** (dimension * dimension) * fibre
    active = operations if modulus > 1 else ()
    counts = census(active)
    dimension_term = 716 + 933 * (2 * digits(dimension * dimension))
    setup = 27 * input_width + 10 * roles + (373 + len(active) * (3 * dimension_term + 36)) * volume
    kernels = 4096 * counts["add"] + 530 * counts["scale"] + 4096 * counts["negate"] + 32768 * counts["translate"]
    return setup + (kernels + 100000 * counts["native_calls"]) * volume
