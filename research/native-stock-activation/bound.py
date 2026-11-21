"""Replay the six-stage resource and full-parent input comparisons with integers."""

from fractions import Fraction
from json import dumps


H = 240_000_000_000_000
COMPLEX_H = 3_300_000_000
KAPPA = Fraction(387_992_803_556, 10**14)
STAGES = tuple(
    Fraction(x, 10**15)
    for x in (
        3_852_480_000_000,
        3_879_818_243_504,
        3_879_927_596_478,
        3_879_928_033_890,
        3_879_928_035_639,
        3_879_928_035_646,
    )
)
COVERED = Fraction(3_879_928_035_648, 10**15)
RHO = Fraction(1, 250)
CHUNKS = Fraction(3, 100)
HIGH = (1 - CHUNKS) * RHO


def ceiling(x):
    return -(-x.numerator // x.denominator)


def entrance_logs(rank_bits=H):
    first = ceiling(Fraction(2 * rank_bits + 12, 1 - HIGH))
    return tuple(first + j * (12 + 2 * rank_bits) for j in range(6))


def entered(ternary_digits, stage, rank_bits=H):
    """Compare a represented width with the power of two in the theorem."""
    if ternary_digits < 1 or not 1 <= stage <= 6 or rank_bits < 1:
        raise ValueError("Use a positive width, rank logarithm and stage in [1,6]")
    return ternary_digits.bit_length() - 1 >= entrance_logs(rank_bits)[stage - 1]


def first_axis(scale, degree):
    """Find the first nonempty geometry without allocating an operand."""
    for s in range(1, 1000):
        width = scale * s**degree
        low = max(1, (2 ** (s - 1) - 2) // 6 + 1, width - 2)
        high = (2**s - 2) // 6
        for b in range(low, min(high, width + width.bit_length() + 2) + 1):
            # b is the least ceiling logarithm with an admissible operand.
            if b - width + 3 >= b.bit_length():
                # Also enforce n > 2^{b-1}. Return the larger lower bound plus one.
                if b - 1 >= width - 3 + b.bit_length():
                    return s, b, 1, b - 1
                if width >= 3 and b << 1 >= 1 << max(0, b - width + 3):
                    return s, b, b, width - 3
                raise ArithmeticError("The first-length inequality needs an exact comparison")
    raise ArithmeticError("The axis entrance was not reached")


def census():
    seed = Fraction(12039, 3125000)
    assert STAGES[0] == seed
    prev = Fraction(0)
    for current in STAGES:
        assert prev < current < (1 - RHO) * COVERED + RHO * prev
        assert current < HIGH < RHO
        prev = current
    cuts = entrance_logs()
    for i, cut in enumerate(cuts):
        assert cut <= 13 * H and (1 - HIGH) * cut >= 2 * H + 12
        if i:
            assert cut == cuts[i - 1] + 12 + 2 * H
    old_one = Fraction(2 * H + 1, 1 - RHO)
    # Every old native child has at most ceil(e^(1/250))+1 trits.
    old_six = 250**5 * (old_one - Fraction(250, 249))
    old_guard = ceiling(Fraction(2 * H + 12, 1 - RHO))
    old_stage_sufficient = old_guard
    for _ in range(5):
        old_stage_sufficient = 250 * (old_stage_sufficient + 1)
    strong = 16 * H
    crt = cuts[-1] + 12
    # The new, complete six-stack upper bound against the old top stock alone.
    gain_bits = old_six * (RHO - HIGH) - 7
    old_top_high = old_six * RHO - 1 + 2 * H
    # At strong entry t < 16H+1, the top floor exceeds the growing term.
    # 24*20*N²*(E5+1) rows in log base three leave room for the final ceiling.
    assert HIGH * (strong + 1) < cuts[-2] and 2 * 24 * 20 + 1 < 2048
    # On the old six-active tail the growing term dominates all earlier floors.
    assert HIGH * old_six > cuts[-2] + 2
    # D_old >= (3+t/H)/2 there, and the new sum is bounded by 24(3+t/H).
    assert (1 - 2 * RHO) * old_six / H > 2
    return {
        "binary_log2_N": H,
        "complex_log2_M": COMPLEX_H,
        "kappa": "0.00387992803556",
        "log2_stage_threshold_trits": list(cuts),
        "old_one_stage_sufficient_stock_log2_trits": old_guard,
        "old_six_ordinary_sufficient_log2_trits": old_stage_sufficient,
        "old_six_necessary_log2_trits_floor": int(old_six),
        "old_nested_necessary_log2_public_precision_floor_safe": int(old_six) - 2,
        "new_crt_and_complex_log2_public_precision": crt,
        "new_six_inside_complex_log2_public_precision": strong,
        "ratio_old_required_to_new_sufficient_in_log2_precision_floor": (int(old_six) - 2)
        // strong,
        "new_log2_log3_rows_upper_at_strong_entry": cuts[-1] - 1,
        "old_log2_log3_rows_lower_floor_at_any_six_entry": int(old_top_high),
        "same_width_log2_ratio_of_log3_reserves_lower_floor": int(gain_bits),
        "old_first_axis_s_b_coefficient_exponent_before_plus_one": first_axis(2**16, 3),
        "new_first_axis_s_b_coefficient_exponent_before_plus_one": first_axis(64, 2),
    }


if __name__ == "__main__":
    print(dumps(census(), indent=2))
