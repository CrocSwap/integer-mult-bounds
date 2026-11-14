#!/usr/bin/env python3
"""Exact rounded-MOVE bit and tensor preflight; no project code imported."""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from math import floor

if not __debug__:
    raise SystemExit("optimized Python is unsupported: assertions are required")

PROOF_SHA256 = "b9dcc7361a05518f117c6e653ef8e5035e4fb5a296cbf54eb43b997f2f1db081"
PROOF_PATH = "/workspace/scratch/92c9920affc2/reference/sharp-rounded-move-PROOF.md"
if sha256(open(PROOF_PATH, "rb").read()).hexdigest() != PROOF_SHA256:
    raise SystemExit("pinned sharp-rounded-move proof changed")


def signed(value: int, width: int) -> int:
    value &= (1 << width) - 1
    return value - (1 << width) if value >> (width - 1) else value


def qfit(value: int, width: int) -> bool:
    return -(1 << (width - 1)) <= value <= (1 << (width - 1)) - 1


def round_bits(z: int, w: int, k: int) -> tuple[bool, int, int]:
    width = w + 2 * k + 1
    prefix_width = width - k
    bits = z & ((1 << width) - 1)
    prefix = bits >> k
    first_discarded = (bits >> (k - 1)) & 1
    if first_discarded:
        prefix = (prefix + 1) & ((1 << prefix_width) - 1)
    low = prefix & ((1 << w) - 1)
    high = prefix >> w
    sign = low >> (w - 1)
    expected_high = (1 << (k + 1)) - 1 if sign else 0
    return high == expected_high, signed(low, w), prefix


def exact_up(z: int, k: int) -> int:
    return floor(Fraction(z, 1 << k) + Fraction(1, 2))


def check_rounding_domain() -> tuple[int, int, int]:
    count = tie_cases = accepted = 0
    for w in range(2, 6):
        for k in range(1, 5):
            radius = 1 << (w + 2 * k - 1)
            for z in range(-radius, radius + 1):
                expected = exact_up(z, k)
                expected_fit = qfit(expected, w)
                got_fit, got, _ = round_bits(z, w, k)
                assert got_fit == expected_fit, (w, k, z, expected, got_fit)
                if got_fit:
                    assert got == expected, (w, k, z, expected, got)
                    accepted += 1
                count += 1
                if (z & ((1 << k) - 1)) == (1 << (k - 1)):
                    tie_cases += 1
    return count, accepted, tie_cases


def check_prefix_margins() -> tuple[int, int]:
    # Gaussian rational arithmetic: each number is (real, imaginary).
    G = tuple[Fraction, Fraction]

    def gmul(a: G, b: G) -> G:
        ar, ai = a
        br, bi = b
        return ar * br - ai * bi, ar * bi + ai * br

    half = Fraction(1, 2)
    cmat = [
        [(half, half), (half, -half)],
        [(half, -half), (half, half)],
    ]

    def kron(a: list[list[G]], b: list[list[G]]) -> list[list[G]]:
        rows_a, cols_a = len(a), len(a[0])
        rows_b, cols_b = len(b), len(b[0])
        out = [[(Fraction(0), Fraction(0)) for _ in range(cols_a * cols_b)]
               for _ in range(rows_a * rows_b)]
        for i in range(rows_a):
            for j in range(cols_a):
                for u in range(rows_b):
                    for v in range(cols_b):
                        out[i * rows_b + u][j * cols_b + v] = gmul(a[i][j], b[u][v])
        return out

    matrix = [[(Fraction(1), Fraction(0))]]
    rows_checked = 0
    integer_prefixes = 0
    for f in range(1, 9):
        matrix = kron(matrix, cmat)
        denom = 1 << ((f + 1) // 2)
        norm = denom
        for row in matrix:
            row_l1 = sum(abs(re) + abs(im) for re, im in row)
            assert row_l1 == norm, (f, row_l1, norm)
            assert all((re * denom).denominator == 1 and (im * denom).denominator == 1
                       for re, im in row)
            rows_checked += 1
        k = (f + 1) // 2
        assert all((re * (1 << k)).denominator == 1 and (im * (1 << k)).denominator == 1
                   for row in matrix for re, im in row)
        integer_prefixes += len(matrix) ** 2

        # For w=2..5, include the most-negative endpoint in the universal
        # row-norm margin calculation; M is 2^(w-1), not the positive max.
        for w in range(2, 6):
            M = 1 << (w - 1)
            W = w + 2 * k + 1
            bound = (1 << (2 * k)) * M
            signed_W_min, signed_W_max = -(1 << (W - 1)), (1 << (W - 1)) - 1
            assert bound == 1 << (W - 2)
            assert signed_W_min < -bound < 0 < bound <= signed_W_max
    return rows_checked, integer_prefixes


def check_mutants() -> dict[str, tuple[int, int]]:
    # At exact +1/2, nearest-up must return one; truncation and ties-to-even
    # both return zero.
    w, k = 3, 2
    z = 1 << (k - 1)
    target = exact_up(z, k)
    assert target == 1
    truncation = z >> k
    ties_to_even = round(Fraction(z, 1 << k))
    assert truncation != target
    assert ties_to_even != target

    # A real C-prefix counterexample for early pre-round sign checking.
    # w>=2, f=1, k=1, M=2^(w-1), input components are a=-M+i and b=-M.
    # The first scaled C output is (1+i)a+(1-i)b = -(2M+1)+i.
    M = 1 << (w - 1)
    a = (-M, 1)
    b = (-M, 0)
    z_re = a[0] - a[1] + b[0] + b[1]
    z_im = a[0] + a[1] - b[0] + b[1]
    assert (z_re, z_im) == (-(2 * M + 1), 1)
    qpre = z_re >> 1
    assert qpre == -M - 1 and not qfit(qpre, w)
    rounded = exact_up(z_re, 1)
    assert rounded == -M and qfit(rounded, w)
    # The proposed widened prefix algorithm accepts the rounded minimum.
    got_fit, got, _ = round_bits(z_re, w, 1)
    assert got_fit and got == -M

    # The universal permitted z radius contains this reachable value.
    radius = 1 << (w + 2 * 1 - 1)
    assert abs(z_re) <= radius
    return {
        "positive_half_target_vs_truncation": (target, truncation),
        "positive_half_target_vs_ties_even": (target, ties_to_even),
        "reachable_early_precheck": (qpre, rounded),
    }


def main() -> None:
    count, accepted, ties = check_rounding_domain()
    rows, integral_matrix_entries = check_prefix_margins()
    mutants = check_mutants()
    print(
        "PASS_ROUNDED_MOVE_PREFLIGHT "
        f"z_values={count} accepted={accepted} ties={ties} "
        f"tensor_rows={rows} scaled_integral_entries={integral_matrix_entries}"
    )
    for name, witness in mutants.items():
        print(f"{name}={witness}")


if __name__ == "__main__":
    main()
