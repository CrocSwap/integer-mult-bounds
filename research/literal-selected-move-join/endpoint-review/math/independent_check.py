#!/usr/bin/env python3
"""Independent exact checks for PROOF-CANDIDATE.md.

Uses direct two-by-two matrix multiplication over Gaussian rationals. It does
not import or use the candidate's butterfly checker.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
import sys

if not __debug__:
    raise SystemExit("optimized Python is unsupported: exact-check assertions would be disabled")

Gaussian = tuple[Fraction, Fraction]


def q(re: int | Fraction = 0, im: int | Fraction = 0) -> Gaussian:
    return Fraction(re), Fraction(im)


def c_pair(a: Gaussian, b: Gaussian, inverse: bool = False) -> tuple[Gaussian, Gaussian]:
    # Directly multiply by C or C^-1, where
    # C = [[1+i, 1-i], [1-i, 1+i]] / 2 and C^-1 = C^3.
    ar, ai = a
    br, bi = b
    sr, si = ar + br, ai + bi
    dr, di = ar - br, ai - bi
    if inverse:
        return q((sr + di) / 2, (si - dr) / 2), q((sr - di) / 2, (si + dr) / 2)
    return q((sr - di) / 2, (si + dr) / 2), q((sr + di) / 2, (si - dr) / 2)


def apply_axis(v: list[Gaussian], f: int, axis: int, inverse: bool = False) -> list[Gaussian]:
    out = list(v)
    bit = 1 << axis
    for lo in range(1 << f):
        if lo & bit:
            continue
        a, b = c_pair(v[lo], v[lo | bit], inverse)
        out[lo], out[lo | bit] = a, b
    return out


def apply_subset(v: list[Gaussian], f: int, axes: set[int], inverse: bool = False) -> list[Gaussian]:
    out = list(v)
    ordered = sorted(axes)
    if inverse:
        ordered = list(reversed(ordered))
    for axis in ordered:
        out = apply_axis(out, f, axis, inverse)
    return out


def max_component(v: list[Gaussian]) -> Fraction:
    return max(max(abs(re), abs(im)) for re, im in v)


def integral(v: list[Gaussian]) -> bool:
    return all(re.denominator == 1 and im.denominator == 1 for re, im in v)


def witness(f: int, subset: set[int], endpoint_scale: int = 1) -> tuple[list[Gaussian], list[Gaussian], list[Gaussian], int]:
    comp = set(range(f)) - subset
    d = min(len(subset), len(comp))
    left_active = set(sorted(subset)[:d])
    right_active = set(sorted(comp)[:d])
    active_mask = sum(1 << axis for axis in left_active | right_active)
    lam = 1 << ((d + 1) // 2)
    z = [q(endpoint_scale * lam if (address & active_mask) == 0 else 0) for address in range(1 << f)]
    x = apply_subset(z, f, subset, inverse=True)
    y = apply_subset(z, f, comp)
    return x, y, z, d


def check_induced_norms(max_f: int = 5) -> int:
    cases = 0
    for f in range(max_f + 1):
        n = 1 << f
        all_axes = set(range(f))
        for j in range(f + 1):
            for axes_tuple in combinations(range(f), j):
                axes = set(axes_tuple)
                columns = []
                for col in range(n):
                    e = [q(int(i == col)) for i in range(n)]
                    columns.append(apply_subset(e, f, axes))
                max_row_sum = Fraction(0)
                for row in range(n):
                    row_sum = sum(abs(columns[col][row][0]) + abs(columns[col][row][1]) for col in range(n))
                    max_row_sum = max(max_row_sum, row_sum)
                expected = Fraction(1 << ((j + 1) // 2))
                assert max_row_sum == expected, (f, axes, max_row_sum, expected)
                # The complementary inverse has the same exact row norm.
                inv_columns = []
                for col in range(n):
                    e = [q(int(i == col)) for i in range(n)]
                    inv_columns.append(apply_subset(e, f, all_axes - axes, inverse=True))
                inv_row_sum = max(
                    sum(abs(inv_columns[col][row][0]) + abs(inv_columns[col][row][1]) for col in range(n))
                    for row in range(n)
                )
                comp_j = f - j
                assert inv_row_sum == Fraction(1 << ((comp_j + 1) // 2))
                cases += 1
    return cases


def check_witnesses(max_f: int = 7) -> tuple[int, int]:
    cut_cases = 0
    width_cases = 0
    for f in range(max_f + 1):
        axes = set(range(f))
        for j in range(f + 1):
            for subset_tuple in combinations(range(f), j):
                subset = set(subset_tuple)
                x, y, z, d = witness(f, subset)
                pref = apply_subset(x, f, subset)
                whole = apply_subset(x, f, axes)
                assert integral(x) and integral(y) and integral(pref)
                assert whole == y
                assert pref == z
                assert max_component(x) == 1
                assert max_component(y) == 1
                assert max_component(pref) == 1 << ((d + 1) // 2)
                cut_cases += 1

        # Middle cut saturates the common-scale bound and the one-bit-lower
        # signed width counterexample for several input widths.
        mid = set(range(floor_half(f)))
        d = min(len(mid), f - len(mid))
        k = (floor_half(f) + 1) // 2
        for w in range(2, 6):
            m = (1 << (w - 1)) - 1
            x, y, z, d = witness(f, mid, endpoint_scale=m)
            pref = apply_subset(x, f, mid)
            scaled_pref = [q(re * (1 << k), im * (1 << k)) for re, im in pref]
            assert max_component(x) == m and max_component(y) == m
            assert integral(scaled_pref)
            sharp = (1 << (2 * k)) * m
            assert max_component(scaled_pref) == sharp
            max_wide = (1 << (w + 2 * k - 1)) - 1
            max_narrow = (1 << (w + 2 * k - 2)) - 1
            assert sharp <= max_wide
            assert sharp > max_narrow
            width_cases += 1
    return cut_cases, width_cases


def floor_half(n: int) -> int:
    return n // 2


def check_negative_controls() -> dict[str, bool]:
    # d=1 is exactly where floor(d/2) is too small.
    f, subset = 2, {0}
    x, y, z, d = witness(f, subset)
    pref = apply_subset(x, f, subset)
    assert d == 1 and max_component(pref) == 2
    rejected_floor_exponent = max_component(pref) > (1 << (d // 2))

    # Applying C instead of C^-1 on the S axes fails the joint endpoint.
    comp = set(range(f)) - subset
    bad_x = apply_subset(z, f, subset)
    bad_y = apply_subset(bad_x, f, set(range(f)))
    expected_y = apply_subset(z, f, comp)
    rejected_wrong_inverse = bad_y != expected_y

    # For w=2, f=2, k=1, the sharp output is 4; a 3-bit symmetric signed
    # field only holds through 3.
    w, k = 2, 1
    sharp = (1 << (2 * k)) * ((1 << (w - 1)) - 1)
    rejected_one_fewer_bit = sharp > ((1 << (w + 2 * k - 2)) - 1)

    assert rejected_floor_exponent
    assert rejected_wrong_inverse
    assert rejected_one_fewer_bit
    return {
        "ceil_to_floor_exponent_mutant_rejected": rejected_floor_exponent,
        "wrong_inverse_direction_mutant_rejected": rejected_wrong_inverse,
        "one_fewer_signed_bit_mutant_rejected": rejected_one_fewer_bit,
    }


def main() -> None:
    norm_cases = check_induced_norms()
    cut_cases, width_cases = check_witnesses()
    controls = check_negative_controls()
    print(
        "PASS_ENDPOINT_WIDTH_REVIEW "
        f"norm_matrices={norm_cases} cut_witnesses={cut_cases} "
        f"width_witnesses={width_cases} controls={len(controls)}"
    )
    for key, value in controls.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
