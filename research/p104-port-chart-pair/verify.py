#!/usr/bin/env python3
"""Every port-dependent C_u pair fails the adjacent data-line match.

Address space F_2^4. Charts are the published diagonal family
C_u = ((1+i) I + (1-i) X_u) / 2. An exit chart C_a followed by an entrance
chart C_b matches every data character if and only if a = b. No new kappa.
"""

from __future__ import annotations

M = 4
DIM = 1 << M
ONE = (1, 0)
I_UNIT = (0, 1)
NEG_I = (0, -1)


def parity(u: int, z: int) -> int:
    return (u & z).bit_count() & 1


def x_eigenvalue(u: int, z: int) -> int:
    """X_u |z> = (-1)^{u·z} |z>, returned as ±1."""
    return -1 if parity(u, z) else 1


def c_eigenvalue(u: int, z: int):
    """Evaluate C_u on character z from the displayed formula, not from a case table."""
    x = x_eigenvalue(u, z)
    # ((1+i) + (1-i) x) / 2. For x = ±1 both coordinates are even.
    real = 1 + x
    imag = 1 - x
    if real % 2 or imag % 2:
        raise AssertionError((u, z, real, imag))
    return (real // 2, imag // 2)


def inverse_unit(value):
    norm = value[0] * value[0] + value[1] * value[1]
    if norm != 1:
        raise AssertionError(value)
    return (value[0], -value[1])


def multiply(left, right):
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def transport(a: int, b: int, z: int):
    """Eigenvalue of C_b C_a^{-1} on |z>."""
    return multiply(c_eigenvalue(b, z), inverse_unit(c_eigenvalue(a, z)))


def closed_transport(a: int, b: int, z: int):
    """Same multiplier from the four dot-product cases in PROOF.md."""
    pa, pb = parity(a, z), parity(b, z)
    if pa == pb:
        return ONE
    if pa == 0:
        return I_UNIT
    return NEG_I


def failures(a: int, b: int):
    return [z for z in range(DIM) if transport(a, b, z) != ONE]


def classify():
    equal = []
    unequal = []
    for a in range(DIM):
        for b in range(DIM):
            bad = failures(a, b)
            for z in range(DIM):
                if transport(a, b, z) != closed_transport(a, b, z):
                    raise AssertionError((a, b, z))
            if a == b:
                if bad:
                    raise AssertionError((a, b, bad))
                equal.append((a, b))
            else:
                if len(bad) != DIM // 2:
                    raise AssertionError((a, b, bad))
                gap = a ^ b
                if gap == 0 or any(parity(gap, z) != 1 for z in bad):
                    raise AssertionError((a, b, gap, bad))
                if any(parity(gap, z) == 1 for z in range(DIM) if z not in bad):
                    raise AssertionError((a, b, bad))
                unequal.append((a, b))
    if len(equal) != DIM or len(unequal) != DIM * DIM - DIM:
        raise AssertionError((len(equal), len(unequal)))
    # The #4136 slice is the entrance-I column, every nonzero exit.
    entrance_i = [a for a in range(1, DIM) if failures(a, 0)]
    if len(entrance_i) != DIM - 1:
        raise AssertionError(len(entrance_i))
    return {
        "address_bits": M,
        "charts": DIM,
        "ordered_pairs": DIM * DIM,
        "matching_pairs": len(equal),
        "failing_pairs": len(unequal),
        "failures_per_unequal_pair": DIM // 2,
        "entrance_identity_failures": len(entrance_i),
    }


def forgotten_phase_multiplier(u: int, z: int):
    """The false chart that stores the odd eigenvalue as 1 instead of i."""
    del u, z
    return ONE


def phase_forgotten_matches():
    """That false chart makes every ordered pair look like a match."""
    matches = 0
    for a in range(DIM):
        for b in range(DIM):
            if all(
                multiply(
                    forgotten_phase_multiplier(b, z),
                    inverse_unit(forgotten_phase_multiplier(a, z)),
                )
                == ONE
                for z in range(DIM)
            ):
                matches += 1
    return matches


def main():
    row = classify()
    if phase_forgotten_matches() != DIM * DIM:
        raise SystemExit("phase-forgotten control did not match every pair")
    if row["matching_pairs"] != 16 or row["failing_pairs"] != 240:
        raise SystemExit(row)
    if row["entrance_identity_failures"] != 15:
        raise SystemExit(row)
    print(
        "PASS_P104_PORT_CHART_PAIR "
        f"address=F2^{row['address_bits']} charts={row['charts']} "
        f"ordered_pairs={row['ordered_pairs']} "
        f"matching_pairs={row['matching_pairs']} "
        f"failing_pairs={row['failing_pairs']} "
        f"failures_per_unequal_pair={row['failures_per_unequal_pair']} "
        f"entrance_I_failures={row['entrance_identity_failures']} "
        "data_match_iff_equal_charts=true helpers=out_of_model no_new_kappa"
    )


if __name__ == "__main__":
    main()
