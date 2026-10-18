"""Closed logical-tape invoice; no predecessor code is imported."""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def countdown(value, digits):
    """PR2877's fully drained Counter identity, credited rather than new."""
    require(type(value) is int and value >= 0, "nonnegative countdown")
    require(
        type(digits) is int and digits >= max(1, value.bit_length()), "counter encoding"
    )
    if value == 0:
        return 14 * digits + 40
    return 15 * value + 14 * digits - 5 * value.bit_count() + 36


def suffix_probe(value):
    require(type(value) is int and value > 0, "positive suffix")
    if value % 2 == 0:
        return 4
    return 15 if value > 1 and value % 4 == 1 else 12


def invoice(modulus, before, suffix, digits=None):
    for value in (modulus, before, suffix):
        require(type(value) is int and value > 0, "positive integer extent")
    require(modulus >= 3 and modulus % 2 == 1, "odd modulus at least three")
    length = modulus.bit_length()
    digits = length + 1 if digits is None else digits
    require(type(digits) is int and digits >= length, "modulus word encoding")
    half = modulus // 2
    even = half + 1
    h, e = half.bit_length(), even.bit_length()
    trailing = (even & -even).bit_length() - 1
    volume = before * modulus * suffix
    setup = 43 * length + 5 * e + 5 * trailing + 92 + 3 * (trailing == h)
    return {
        "validation": 20 + (before % 2 == 0) + (suffix % 2 == 0),
        "setup_cleanup": setup + 18 * (digits - length - 1),
        "payload": 23 * volume + 32,
        "outer": 2 * countdown(before, before.bit_length()),
        "rows": before * (2 * countdown(half, h) + countdown(even, e)),
        "suffix": 2
        * before
        * modulus
        * (
            suffix_probe(suffix)
            + (countdown(suffix, suffix.bit_length()) if suffix > 1 else 0)
        ),
    }


def allocations(modulus, before, suffix):
    invoice(modulus, before, suffix)
    return 7 + 3 * before + (2 * before * modulus if suffix > 1 else 0)
