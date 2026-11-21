"""Choose coprime square sides with complete binary windows for the numerical supplier."""

from math import gcd, isqrt

from outer_schedule import Shape, ceil_log2


def minimum_window(s):
    """Keep the finite selector. On the proved tail expose 128 complete digit positions."""
    return 64 * s * s if s < 512 else 128 * (4 * (s + 1) + 6)


def public_shape(public, extent):
    s = ceil_log2(public + 2)
    capacity = extent // minimum_window(s)
    return Shape(public, extent, 1 << (capacity.bit_length() - 1)) if capacity else None


def parameters(input_bits):
    if input_bits < 2:
        return None
    b = ceil_log2(input_bits)
    return public_shape(6 * b, ceil_log2((4 * input_bits + b - 1) // b))


def square_sides(shape):
    """Emit each actual side. The running product includes 2 and all previous bases."""
    modulus = 2
    for index, width in enumerate(shape.axes()):
        denominator = (16 if index % 2 else 4) * shape.count
        side = 1 << width
        low_square = side - side // denominator
        high_square = side - (side + 2 * denominator - 1) // (2 * denominator)
        first = max(3, (1 + isqrt(low_square - 1)) | 1)
        for base in range(first, isqrt(high_square) + 1, 2):
            if gcd(base, modulus) == 1:
                modulus *= base
                yield base * base
                break
        else:
            raise ArithmeticError("The square interval has no admissible odd base")


def connected_exponent(ordinary_width_log, complex_rank_log):
    """Return A with p >= 2**A sufficient for a real complex-to-ordinary invocation."""
    if min(ordinary_width_log, complex_rank_log) < 1:
        raise ValueError("Both native logarithms must be positive")
    target = ordinary_width_log + complex_rank_log + 102
    s = max(512, target)
    while s < target + 7 * ceil_log2(s):
        s = target + 7 * ceil_log2(s)
    dyadic_log = ceil_log2(s)
    after_jump = target + 7 * (dyadic_log + 1)
    if (1 << dyadic_log) + 1 < after_jump:
        s = after_jump
    return s - 1


def entrance_geometry(exponent, *, quadratic=False):
    """Compute the exact largest side throughout the first certified public precision."""
    if exponent < 511:
        raise ValueError("Use a controller exponent of at least 511")
    s = exponent + 1
    minimum = 64 * s**2 if quadratic else minimum_window(s)
    q = ceil_log2(6 * minimum)
    if exponent - q < (6 * exponent).bit_length():
        raise ArithmeticError("The controller correction exceeds the dyadic gap")
    largest = ((1 << q) + 5) // 6
    # The older compiler used a uniform bound in s. The linear picker pays the actual width.
    private = (1 << 20) * (s + 1) ** 2 if quadratic else 1024 * (largest + s + 67) + s
    return {
        "public_offset_above_2_to_A": (-pow(2, exponent, 6)) % 6,
        "first_extent_bits_minus_b": 4 - exponent,
        "last_extent_bits_minus_b": 5 - exponent,
        "minimum_width": minimum,
        "log2_axis_count": exponent - q,
        "largest_axis_width": largest,
        "private_clock_log2_upper": private,
        "actual_dense_root_entry_log2": 2 * largest,
    }
