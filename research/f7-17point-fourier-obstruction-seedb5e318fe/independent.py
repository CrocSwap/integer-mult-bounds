"""Independent re-derivation of the KB3d Fourier/Parseval obstruction.

Second code path (no import of fourier17): a Walsh-Hadamard transform instead
of direct character loops, Parseval by direct double counting of pairs, and an
exhaustive control of the |rho_hat| <= sum rho bound over every multiplicity
shape of total 2 on the 64 odd masks.  Positive control: the real 10-point
cover of F2^5 must pass every check (no false contradiction).

Marker: PASS_FOURIER_INDEPENDENT {...}
"""

import itertools
import json
import sys


# ------------------------------------------- Walsh-Hadamard (different path)


def fwht(values):
    """In-place-style Walsh-Hadamard transform over (Z/2)^n, exact ints."""
    out = list(values)
    size = len(out)
    width = 1
    while width < size:
        for base in range(0, size, 2 * width):
            for k in range(width):
                u = out[base + k]
                v = out[base + k + width]
                out[base + k] = u + v
                out[base + k + width] = u - v
        width *= 2
    return out


def indicator(points, n):
    vec = [0] * (1 << n)
    for p in points:
        vec[p] += 1
    return vec


def cross_r(A, B, n):
    vec = [0] * (1 << n)
    for a in A:
        for b in B:
            vec[a ^ b] += 1
    return vec


def check_ft_convolution(A, B, n):
    """r_hat == f_hat * g_hat through the transform, all s."""
    r_hat = fwht(cross_r(A, B, n))
    f_hat = fwht(indicator(A, n))
    g_hat = fwht(indicator(B, n))
    for s in range(1 << n):
        if r_hat[s] != f_hat[s] * g_hat[s]:
            return False
    return True


def parseval_by_pairs(points, n):
    """sum_s c_hat(s)^2 == 2^n * |{(p,q) in P^2 : p == q}| = 2^n * |P|."""
    vec = fwht(indicator(points, n))
    lhs = sum(v * v for v in vec)
    rhs = (1 << n) * len(points)
    return lhs == rhs, lhs, rhs


# ------------------------------------------------------ the obstruction, again


def obstruction_numbers(n, s_count, t_count):
    """Re-derived by explicit formulas (opposite parity required)."""
    half = 1 << (n - 1)
    excess = s_count * t_count - half
    if excess < 0:
        return {"contradiction": True, "reason": "counting"}
    if s_count % 2 == t_count % 2:
        return {
            "odd_excess": excess,
            "bounded_card": None,
            "max_char": None,
            "parseval_remainder": None,
            "max_allowed": None,
            "deficit": None,
            "contradiction": False,
            "reason": "equal character parities: no parity squeeze",
        }
    card = s_count if s_count % 2 == 0 else t_count
    max_char = 2 * (excess // 2)
    remainder = (1 << n) * card - 2 * card * card
    allowed = ((1 << n) - 2) * max_char * max_char
    return {
        "odd_excess": excess,
        "bounded_card": card,
        "max_char": max_char,
        "parseval_remainder": remainder,
        "max_allowed": allowed,
        "deficit": remainder - allowed,
        "contradiction": remainder > allowed,
    }


# --------------------------------------------------------------- controls


def rho_shapes_total_two():
    """Every rho of total 2 on the 64 odd masks (own enumeration)."""
    masks = list(range(64))
    for p in masks:
        yield {p: 2}
    for p, q in itertools.combinations(masks, 2):
        yield {p: 1, q: 1}


def rho_hat_bound_ok():
    """|rho_hat(s)| <= sum rho for every shape of total 2, all s in F2^6."""
    worst = 0
    count = 0
    for rho in rho_shapes_total_two():
        count += 1
        total = sum(rho.values())
        for s in range(64):
            v = 0
            for x, c in rho.items():
                if bin(s & x).count("1") % 2 == 0:
                    v += c
                else:
                    v -= c
            worst = max(worst, abs(v))
            if abs(v) > total:
                return False, count, worst
    return True, count, worst


def exhaustive_small_group_ft():
    """Every A, B subset of F2^3: r_hat == f_hat * g_hat (256 x 256)."""
    n = 3
    N = 1 << n
    sets = [tuple(x for x in range(N) if m >> x & 1) for m in range(1 << N)]
    checked = 0
    for A in sets:
        for B in sets:
            if not check_ft_convolution(A, B, n):
                return False, checked
            checked += 1
    return True, checked


def main():
    out = {}

    # 1. the obstruction numbers, re-derived
    for split in ((11, 6), (6, 11)):
        out["obstruction_%d_%d" % split] = obstruction_numbers(7, *split)
    assert out["obstruction_11_6"]["contradiction"]
    assert out["obstruction_11_6"] == {
        "odd_excess": 2,
        "bounded_card": 6,
        "max_char": 2,
        "parseval_remainder": 696,
        "max_allowed": 504,
        "deficit": 192,
        "contradiction": True,
    }
    assert out["obstruction_6_11"] == out["obstruction_11_6"]
    # non-vacuity: the four other 17-point splits do not fire
    for split in ((10, 7), (7, 10), (9, 8), (8, 9)):
        assert obstruction_numbers(7, *split)["contradiction"] is False, split
    out["other_splits_no_contradiction"] = True

    # 2. FT convolution identity, exhaustive on F2^3
    ok, checked = exhaustive_small_group_ft()
    assert ok
    out["ft_convolution_exhaustive_f2_3"] = checked

    # 3. |rho_hat| <= sum rho on every total-2 shape over the 64 odd masks
    ok, count, worst = rho_hat_bound_ok()
    assert ok
    out["rho_shapes_checked"] = count
    out["rho_hat_worst_abs"] = worst

    # 4. Parseval by direct double counting on concrete sets
    for name, pts, n in (
        ("B6", [1, 2, 4, 8, 16, 31], 7),
        ("A11", [0, 3, 5, 6, 9, 17, 33, 58, 65, 92, 12], 7),
    ):
        ok, lhs, rhs = parseval_by_pairs(pts, n)
        assert ok, (name, lhs, rhs)
    out["parseval_double_counting"] = "ok (B6: 768 == 768, A11: 1408 == 1408)"

    # 5. positive control: the real 10-point cover of F2^5
    cover = [0, 1, 2, 3, 4, 5, 6, 8, 16, 31]
    A = [x for x in cover if bin(x).count("1") % 2 == 0]
    B = [x for x in cover if bin(x).count("1") % 2 == 1]
    assert (len(A), len(B)) == (4, 6)
    assert check_ft_convolution(A, B, 5)
    r = cross_r(A, B, 5)
    odd_masks = [x for x in range(32) if bin(x).count("1") % 2 == 1]
    assert all(r[o] >= 1 for o in odd_masks)  # the cover is real
    assert sum(r) == 24 and len(odd_masks) == 16  # excess 8
    assert obstruction_numbers(5, 4, 6)["contradiction"] is False
    out["positive_control_cover_n5"] = {
        "split": (4, 6),
        "covers_odd": True,
        "odd_excess": 8,
        "no_false_contradiction": True,
    }

    print("PASS_FOURIER_INDEPENDENT " + json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
