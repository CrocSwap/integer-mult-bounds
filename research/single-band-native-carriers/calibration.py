"""Set the physical ranks and check their complete price with rational arithmetic."""

from dataclasses import dataclass, replace
from fractions import Fraction

from upstream import install

install()
from staged_carriers import entrance_logs

COMPLEX_POWER = 128
COMPLEX_FLOOR = 1 << 15
COMPLEX_C = Fraction(2043, 524288)
GAP = Fraction(1, 10**14)
SETUP_DEGREE = 1024


@dataclass(frozen=True)
class Profile:
    rank_logs: tuple
    complex_log: int
    power: int
    floor: int
    bit_c: Fraction
    eta: Fraction
    ordinary: Fraction
    kappa: Fraction


COMPACT = Profile(
    (260_000, 1_600_000),
    610_000,
    128,
    1 << 15,
    Fraction(2039, 524288),
    Fraction(97, 25_000),
    Fraction("0.003879928035646"),
    Fraction("0.00387992803556"),
)
HIGH_RATE = Profile(
    (25_000_000, 160_000_000, 1_000_000_000, 6_000_000_000, 36_000_000_000, 224_000_000_000),
    1_600_000,
    228,
    1 << 35,
    Fraction(17108907955, 2**42),
    Fraction(39, 10_000),
    Fraction("0.003890115197377"),
    Fraction("0.00389011519729"),
)
PRICE_MATCH = replace(
    HIGH_RATE,
    rank_logs=tuple(7 * h for h in HIGH_RATE.rank_logs),
    ordinary=Fraction("0.003890115271496"),
    kappa=Fraction("0.00389011527141"),
)
PROFILES = {"compact": COMPACT, "high-rate": HIGH_RATE, "price-match": PRICE_MATCH}


def debit(ambient, largest_target, power, c, floor, outer_bits):
    # The dyadic carrier needs no final axes. The paid replication factor is below 9/4.
    assert 32 * floor * 4 < 9 * 15 * (floor - 2)
    assert 9**4 < 2**5 * 4**4
    scale = 4 * (ambient * largest_target) ** power * floor
    upper = Fraction(5, 4) + c * (scale - 1).bit_length() + outer_bits
    return -(-upper.numerator // upper.denominator)


def prices(profile):
    bit_loss = debit(134, 127, profile.power, profile.bit_c, profile.floor, 5)
    numeric_loss = debit(153, 129, COMPLEX_POWER, COMPLEX_C, COMPLEX_FLOOR, 1)
    result = []
    previous = Fraction(0)
    for i, height in enumerate(profile.rank_logs):
        covered = profile.bit_c - Fraction(bit_loss, height)
        limit = min((249 * covered + previous) / 250, profile.eta)
        rate = (
            profile.ordinary
            if i == len(profile.rank_logs) - 1
            else Fraction(int(limit * 10**18) - 1, 10**18)
        )
        if not previous < rate < limit:
            raise ArithmeticError("An ordinary stage has insufficient strict price headroom")
        result.append((height, covered, rate))
        previous = rate
    if not (
        profile.kappa + 4 * GAP < profile.ordinary
        and profile.kappa + 5 * GAP < COMPLEX_C - Fraction(numeric_loss, profile.complex_log)
    ):
        raise ArithmeticError("The numerical consumer cannot receive these prices")
    return bit_loss, numeric_loss, result


def entrance(profile):
    from linear_geometry import connected_exponent

    return connected_exponent(entrance_logs(profile.rank_logs)[-1], profile.complex_log)
