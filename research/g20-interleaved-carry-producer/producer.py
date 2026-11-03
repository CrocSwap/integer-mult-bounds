"""Produce one G20 carry packet from an interleaved low-digit stream.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The fused carry identity and packet ABI retain the source credits.
"""
from fractions import Fraction
from math import lcm


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compile_column(column):
    values = tuple(map(Fraction, column))
    require(len(values) == 8, 'eight source coordinates')
    denominator = lcm(*(x.denominator for x in values))
    require(denominator in (1, 4), 'released whole-column denominator')
    coefficients = tuple(int(denominator*x) for x in values)
    lower = sum(min(a, 0) for a in coefficients)
    positive = sum(max(a, 0) for a in coefficients)
    upper = max(0, positive-1)
    require(-16 <= (lower-denominator+1)*(4//denominator)
            and upper*(4//denominator) <= 12, 'released packet envelope')
    thresholds = tuple(range(lower+1, upper+1))
    bounds = tuple((lower-max(j, 0), positive-min(j, 0)) for j in thresholds)
    return coefficients, denominator, lower, thresholds, bounds


def produce(plan, rows):
    """Read nine bits per row, least significant row first; emit five bits.

    The final row contains the leading radix bit. Each low digit has the
    same padded width as the radix. No input row is retained or reread.
    """
    coefficients, denominator, lower, thresholds, bounds = plan
    carries = [0]*len(thresholds)
    comparisons = [0]*8
    residue = radix_residue = phase = 0
    last_radix = 0
    seen = False
    for row in rows:
        require(type(row) in (tuple, list) and len(row) == 9
                and all(type(x) is int and x in (0, 1) for x in row), 'nine binary symbols')
        bits, radix = row[:8], row[8]
        if not seen:
            require(radix == 1, 'odd radix')
        seen, last_radix = True, radix
        digit = sum(a*b for a, b in zip(coefficients, bits))
        for i, (j, (lo, hi)) in enumerate(zip(thresholds, bounds)):
            carries[i] = (carries[i]+digit-j*radix)//2
            require(lo <= carries[i] <= hi, 'finite comparison state')
        for i, bit in enumerate(bits):
            comparisons[i] = (comparisons[i]+bit-radix)//2
            require(comparisons[i] in (-1, 0), 'finite input comparison')
        if phase < 2:
            residue = (residue+(digit << phase)) % denominator
            radix_residue = (radix_residue+(radix << phase)) % denominator
            phase += 1
    require(seen and last_radix == 1, 'canonical radix ending')
    require(all(x == -1 for x in comparisons), 'low digits below radix')
    quotient = lower+sum(c >= 0 for c in carries)
    # The inverse of either odd residue modulo four is that residue itself.
    congruence = residue*radix_residue % denominator
    carry = quotient-(quotient-congruence) % denominator
    code = carry*(4//denominator)
    require(-16 <= code <= 12, 'five-bit consumer domain')
    return tuple(((code+16) >> i) & 1 for i in range(5))


def state_bits(plan):
    """Bound an explicit state encoding; this is not a minimum."""
    return 16+sum((hi-lo).bit_length() for lo, hi in plan[4])
