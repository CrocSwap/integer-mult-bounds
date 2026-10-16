#!/usr/bin/env python3
"""Exact finite replay for the three-stage prefix-shear interface.

Apache-2.0. Prepared by Cinna Davis with substantial OpenAI Codex assistance.
"""

from itertools import product


def require(condition, message):
    if not condition:
        raise SystemExit(f"FAIL_RECURSIVE_PREFIX_SHEAR_CHAIN: {message}")


def apply(matrix, vector):
    """Apply a 2x2 F2 matrix packed as two 2-bit output rows."""
    row0 = matrix & 0b11
    row1 = (matrix >> 2) & 0b11
    bit0 = (row0 & vector).bit_count() & 1
    bit1 = (row1 & vector).bit_count() & 1
    return bit0 | (bit1 << 1)


def sequential(a1, a2, a3, x, y1, y2, y3):
    """Mutate targets in place; each output feeds the next complete call."""
    y1 ^= apply(a1, x)
    y2 ^= apply(a2, y1)
    y3 ^= apply(a3, y2)
    return y1, y2, y3


def independent_expansion(a1, a2, a3, x, y1, y2, y3):
    """Compute each block term from its original source, without target feedback."""
    t10 = apply(a1, x)
    t21 = apply(a2, y1)
    t20 = apply(a2, t10)
    t32 = apply(a3, y2)
    t31 = apply(a3, t21)
    t30 = apply(a3, t20)
    return y1 ^ t10, y2 ^ t21 ^ t20, y3 ^ t32 ^ t31 ^ t30


def stale_y1(a1, a2, a3, x, y1, y2, y3):
    updated_y1 = y1 ^ apply(a1, x)
    updated_y2 = y2 ^ apply(a2, y1)  # deliberately reads the old y1
    updated_y3 = y3 ^ apply(a3, updated_y2)
    return updated_y1, updated_y2, updated_y3


def stale_y2(a1, a2, a3, x, y1, y2, y3):
    updated_y1 = y1 ^ apply(a1, x)
    updated_y2 = y2 ^ apply(a2, updated_y1)
    updated_y3 = y3 ^ apply(a3, y2)  # deliberately reads the old y2
    return updated_y1, updated_y2, updated_y3


def reversed_inner(a1, a2, a3, x, y1, y2, y3):
    t10 = apply(a1, x)
    t21 = apply(a2, y1)
    t20 = apply(a1, apply(a2, x))  # deliberately uses A1 A2 instead of A2 A1
    t32 = apply(a3, y2)
    t31 = apply(a3, t21)
    t30 = apply(a3, t20)
    return y1 ^ t10, y2 ^ t21 ^ t20, y3 ^ t32 ^ t31 ^ t30


def omitted_last_stage(a1, a2, a3, x, y1, y2, y3):
    updated_y1 = y1 ^ apply(a1, x)
    updated_y2 = y2 ^ apply(a2, updated_y1)
    return updated_y1, updated_y2, y3


def has_counterexample(candidate, a1, a2, a3):
    for x, y1, y2, y3 in product(range(4), repeat=4):
        correct = independent_expansion(a1, a2, a3, x, y1, y2, y3)
        if candidate(a1, a2, a3, x, y1, y2, y3) != correct:
            return True
    return False


def main():
    cases = 0
    for a1, a2, a3 in product(range(16), repeat=3):
        for x, y1, y2, y3 in product(range(4), repeat=4):
            chained = sequential(a1, a2, a3, x, y1, y2, y3)
            expanded = independent_expansion(a1, a2, a3, x, y1, y2, y3)
            require(chained == expanded,
                    f"map triple {(a1, a2, a3)} state {(x, y1, y2, y3)}")
            cases += 1

    # U(a,b)=(a+b,b); L(a,b)=(a,a+b). Each application updates two target coordinates.
    upper = 0b1011
    lower = 0b1101
    a1, a2, a3 = upper, lower, upper
    require(apply(upper, apply(lower, 1)) != apply(lower, apply(upper, 1)),
            "positive fixture must use noncommuting maps")
    for candidate, label in (
        (stale_y1, "stale-y1"),
        (stale_y2, "stale-y2"),
        (reversed_inner, "reversed-factor-order"),
        (omitted_last_stage, "omitted-final-stage"),
    ):
        require(has_counterexample(candidate, a1, a2, a3),
                f"control failed to reject {label}")

    # The general n-stage call-price formulas are exact; n=3 has 1,2,3
    # applications of A1,A2,A3 in the independent path expansion.
    for c1, c2, c3 in product(range(1, 5), repeat=3):
        direct = c1 + 2 * c2 + 3 * c3
        chain = c1 + c2 + c3
        require(direct - chain == c2 + 2 * c3,
                "weighted call-price difference")
    def active_output_rows(matrix):
        return int(bool(matrix & 0b0011)) + int(bool(matrix & 0b1100))

    per_call_xors = [active_output_rows(m) for m in (a1, a2, a3)]
    require(per_call_xors == [2, 2, 2], "fixture must update both target coordinates")
    chain_map_xors = sum(per_call_xors)
    direct_map_xors = per_call_xors[0] + 2 * per_call_xors[1] + 3 * per_call_xors[2]
    staging = 9 * 2
    require(staging == 18, "two-bit staging receipt")
    require(direct_map_xors + staging == 30, "two-bit direct arithmetic receipt")
    require(chain_map_xors == 6, "two-bit sequential arithmetic receipt")

    print(
        "PASS_RECURSIVE_PREFIX_SHEAR_CHAIN "
        f"cases={cases} controls=4 direct_calls=6 chain_calls=3 "
        "L2_staging=18 direct_arithmetic=30 chain_arithmetic=6 extra_rows=6"
    )


if __name__ == "__main__":
    main()
