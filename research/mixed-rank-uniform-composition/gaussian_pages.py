"""Generate the dyadic Gaussian coefficients in physical row order."""

from functools import lru_cache
from math import isqrt


def ceil_div(number, divisor):
    return -(-number // divisor)


def ceil_sqrt(number):
    root = isqrt(number)
    return root + (root * root < number)


def width_parameter(p):
    return ceil_sqrt((16 * p - 1).bit_length())


def selected_source(r, t, v):
    """Return the unique original source at dyadic slot v, or None."""
    j = max(0, ceil_div(r * (2 * v - 1), 2 * t))
    if j < r and 2 * t * j < r * (2 * v + 1):
        return j
    return None


def atan_inverse_bounds(divisor, scale):
    """Bound atan(1/divisor) by the alternating power series."""
    low = high = 0
    power = divisor
    k = 0
    while True:
        denom = (2 * k + 1) * power
        a, b = scale // denom, ceil_div(scale, denom)
        if k % 2:
            low, high = low - b, high - a
        else:
            low, high = low + a, high + b
        k += 1
        power *= divisor * divisor
        if (2 * k + 1) * power >= scale:
            return (low - 1, high) if k % 2 else (low, high + 1)


@lru_cache(maxsize=16)
def pi_bounds(bits):
    scale = 1 << bits
    a, b = atan_inverse_bounds(5, scale)
    c, d = atan_inverse_bounds(239, scale)
    return 16 * a - 4 * d, 16 * b - 4 * c


def negative_exp_bounds(lo, hi, scale):
    """Bound exp(-x) on x in [lo, hi]/scale on the same grid."""
    squares = 0
    while hi > scale // 2:
        lo, hi = lo // 2, ceil_div(hi, 2)
        squares += 1
    term_lo = term_hi = scale
    result_lo = result_hi = scale
    k = 0
    while True:
        k += 1
        term_lo = term_lo * lo // (scale * k)
        term_hi = ceil_div(term_hi * hi, scale * k)
        if k % 2:
            result_lo, result_hi = result_lo - term_hi, result_hi - term_lo
        else:
            result_lo, result_hi = result_lo + term_lo, result_hi + term_hi
        if term_hi <= 1:
            if k % 2:
                result_hi += 1
            else:
                result_lo -= 1
            break
    result_lo = max(0, result_lo)
    result_hi = min(scale, result_hi)
    for _ in range(squares):
        result_lo = result_lo * result_lo // scale
        result_hi = ceil_div(result_hi * result_hi, scale)
    return result_lo, result_hi


@lru_cache(maxsize=8192)
def encode_exp(bits, num, denom, divisor=1, positive=False):
    """Return a lower dyadic approximation to exp(±pi*num/denom)/divisor.

    The exact error is at most two units of the requested output grid.
    Each rounding operation below is outward on its private grid.
    """
    if num < 0 or min(denom, divisor) <= 0:
        raise ValueError('invalid exponential input')
    if num == 0:
        return (1 << bits) // divisor
    if not positive and 3 * num >= (bits + 3) * denom:
        return 0
    work = bits + 4 * (bits + 1).bit_length() + 24
    while True:
        scale = 1 << work
        a, b = pi_bounds(work)
        xlo, xhi = a * num // denom, ceil_div(b * num, denom)
        lo, hi = negative_exp_bounds(xlo, xhi, scale)
        if positive:
            if lo == 0:
                work += 16
                continue
            lo, hi = scale * scale // hi, ceil_div(scale * scale, lo)
        unit = (1 << (work - bits)) * divisor
        lower = lo // unit
        if hi - lower * unit <= 2 * unit:
            return lower
        work += 16


def physical_row(p, bits, r, t, v, window):
    """Yield (source slot, period, broad numerator, narrow numerator).

    v and each returned source slot are in the original dyadic rectangle.
    The signed period separates distinct occurrences at the same address.
    The generator visits zero-valued occurrences and omits their stored zeros.
    The principal narrow diagonal is exactly one, including hole rows.
    """
    alpha = width_parameter(p)
    unit = 1 << bits
    row_selected = selected_source(r, t, v) is not None
    for offset in range(-window, window + 1):
        period, col = divmod(v + offset, t)
        j = selected_source(r, t, col)
        if j is None:
            if offset == 0:
                yield col, period, unit, unit
            continue
        beta = t * j - r * col
        delta = r * offset + beta
        broad = encode_exp(bits, delta * delta, (t * alpha) ** 2, alpha)
        if col == v:
            narrow = unit if offset == 0 else 0
        elif row_selected:
            narrow = encode_exp(bits, alpha**2 * (delta * delta - beta * beta), r * r)
        else:
            narrow = 0
        if broad or narrow:
            yield col, period, broad, narrow


def admitted_row(p, bits, r, t, v, window):
    """Return one physical row after checking the two inverse bounds."""
    entries = tuple(physical_row(p, bits, r, t, v, window))
    unit = 1 << bits
    diagonal = sum(narrow for col, _, _, narrow in entries if col == v)
    mass = sum(abs(narrow) for col, _, _, narrow in entries if col != v)
    gap = 16 * p * p
    normalizer = 1 << (p**100 - 1).bit_length()
    if diagonal != unit or unit + gap * mass > gap * unit:
        raise ValueError("narrow row fails the inverse bound")
    if unit + normalizer * mass > normalizer * unit:
        raise ValueError("narrow row fails the normalized radius bound")
    return entries


def recovery_diagonal(p, bits, r, t, slot):
    j = selected_source(r, t, slot)
    if j is None:
        return 1 << bits
    beta = t * j - r * slot
    return encode_exp(bits, (width_parameter(p) * beta) ** 2, r * r, positive=True)
