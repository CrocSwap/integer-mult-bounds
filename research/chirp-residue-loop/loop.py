"""Bounded specialization of PR3806's complete one-axis replay loop."""


def one_axis(radius, length, slope, *, initial=None):
    """Visit every source state, with the original check order and failures."""
    if (type(radius) is not int or not 4 <= radius <= 4096
            or radius & (radius - 1) or type(length) is not int
            or length not in (radius // 2, radius) or type(slope) is not int
            or not 0 < slope < length or slope % 2 != 1):
        raise ValueError("outside the retained one-axis replay domain")
    modulus = 2 * radius
    factor = (-slope * (radius // length)) % modulus
    index, value, difference, total = 0, 0, factor, 0
    if initial is not None:
        if (not isinstance(initial, tuple) or len(initial) != 4
                or any(type(x) is not int or abs(x).bit_length() > 64 for x in initial)
                or not 0 <= initial[0] < length):
            raise ValueError("invalid initial-state control")
        index, value, difference, total = initial
    steps = 0
    for _ in range(length):
        if value != (factor * index * index) % modulus:
            raise SystemExit("FAIL_CHIRP_RESIDUE_STEP value")
        if difference != (factor * (2 * index + 1)) % modulus:
            raise SystemExit("FAIL_CHIRP_RESIDUE_STEP difference")
        if total != value:
            raise SystemExit("FAIL_CHIRP_RESIDUE_STEP one-axis total")
        steps += 1
        if index + 1 < length:
            total = (total + difference) % modulus
            value = (value + difference) % modulus
            difference = (difference + 2 * factor) % modulus
            index += 1
            continue
        total = (total - value) % modulus
        index, value, difference = 0, 0, factor
        break
    if total != 0 or index != 0 or value != 0:
        raise SystemExit("FAIL_CHIRP_RESIDUE_STEP rollover")
    if steps != length:
        raise SystemExit("FAIL_CHIRP_RESIDUE_STEP step count")
    return steps
