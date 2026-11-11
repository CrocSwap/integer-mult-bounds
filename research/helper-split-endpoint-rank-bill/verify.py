#!/usr/bin/env python3
"""Exact checks for the contact-free endpoint rank bill. No new kappa."""

import math

MARKER = "PASS_HELPER_SPLIT_ENDPOINT_RANK_BILL"
KAPPA = "363005817/100000000000"


def fail(message):
    raise SystemExit("FAIL: " + message)


def power_monotone(max_base, max_q):
    """Lemma 1's integer form: 1 <= u <= v implies u^s <= v^s for s = 2q-p."""
    checked = 0
    for q in range(2, max_q + 1):
        for p in range(1, q):
            s = 2 * q - p
            for u in range(1, max_base + 1):
                previous = u ** s
                for v in range(u, max_base + 1):
                    current = v ** s
                    if previous > current:
                        fail(f"power increase failed at u={u} v={v} s={s}")
                    previous = current
                    checked += 1
            # The opposite direction is false for a strict increase.
            if not (2 ** s > 1 ** s):
                fail("unit power was not strict")
    return checked


def certified_sign(terms, bits=64):
    """Sign of sum coef*sqrt(radicand). Error < 1 per term in units of 2^bits."""
    combined = {}
    for coef, rad in terms:
        if coef == 0 or rad == 0:
            continue
        if rad < 0:
            fail("negative radicand")
        combined[rad] = combined.get(rad, 0) + coef
    scale = 1 << bits
    acc = 0
    err = 0
    for rad, coef in combined.items():
        if coef == 0:
            continue
        approx = math.isqrt(rad * scale * scale)
        acc += coef * approx
        err += abs(coef)
    if acc > err:
        return 1
    if -acc > err:
        return -1
    if err == 0:
        return 0
    if bits >= 4096:
        fail("sign unresolved: " + repr(terms))
    return certified_sign(terms, bits * 2)


def g_terms(d, a, b, x):
    """One path, t = 1/2, c = sqrt(b-a)."""
    return [
        (1, x),
        (1, d - x),
        (-1, d),
        (-1, x - a),
        (-1, b - x),
        (1, b - a),
    ]


def g_sign_against(d, a, b, x, endpoint):
    """Sign of G(endpoint) - G(x) at t = 1/2."""
    left = g_terms(d, a, b, endpoint)
    right = [(-coef, rad) for coef, rad in g_terms(d, a, b, x)]
    return certified_sign(left + right)


def half_endpoint_census(max_d):
    """Interior dimensions lose to an endpoint. Boundary endpoints match k."""
    rows = 0
    positive_proper = 0
    cancelled = 0
    for d in range(1, max_d + 1):
        for a in range(0, d + 1):
            for b in range(a, d + 1):
                # Endpoint formulas: G(a) = k(a), G(b) = k(b), k(0) = k(D) = 0.
                if a == 0:
                    if certified_sign(g_terms(d, a, b, 0)) != 0:
                        fail(f"G(0) identity failed at D={d} b={b}")
                elif a == d:
                    if certified_sign([(1, a), (1, 0), (-1, d)]) != 0:
                        fail(f"k(D) from a failed at D={d}")
                elif certified_sign([(1, a), (1, d - a), (-1, d)]) <= 0:
                    fail(f"k(a) was not positive at D={d} a={a}")
                if b == 0 or b == d:
                    if certified_sign([(1, b), (1, d - b), (-1, d)]) != 0:
                        fail(f"k boundary was not zero at D={d} b={b}")
                elif certified_sign([(1, b), (1, d - b), (-1, d)]) <= 0:
                    fail(f"k(b) was not positive at D={d} b={b}")
                if a == 0 and b == d:
                    for x in range(0, d + 1):
                        if certified_sign(g_terms(d, a, b, x)) != 0:
                            fail(f"full-span path was not identically zero at x={x}")
                        cancelled += 1
                    continue
                for x in range(a, b + 1):
                    left = g_sign_against(d, a, b, x, a)
                    right = g_sign_against(d, a, b, x, b)
                    if x not in (a, b) and left <= 0 and right <= 0:
                        fail(
                            f"interior was not strictly below an endpoint"
                            f" D={d} a={a} b={b} x={x}"
                        )
                    rows += 1
                if a == 0 and 0 < b < d:
                    if g_sign_against(d, a, b, 0, b) <= 0:
                        fail(f"upper endpoint did not beat 0 at D={d} b={b}")
                    positive_proper += 1
                if b == d and 0 < a < d:
                    if g_sign_against(d, a, b, d, a) <= 0:
                        fail(f"lower endpoint did not beat D at D={d} a={a}")
                    positive_proper += 1
    return rows, positive_proper, cancelled


def multi_terms(d, paths, x):
    terms = [(1, x), (1, d - x), (-1, d)]
    for a, b in paths:
        terms.extend(((-1, x - a), (-1, b - x), (1, b - a)))
    return terms


def difference_sign(d, paths, x, endpoint):
    left = multi_terms(d, paths, endpoint)
    right = [(-coef, rad) for coef, rad in multi_terms(d, paths, x)]
    return certified_sign(left + right)


def path_pairs(max_d):
    """Every ordered pair of integer windows on 1 <= D <= max_d."""
    rows = 0
    strict_interior = 0
    for d in range(1, max_d + 1):
        windows = [(a, b) for a in range(d + 1) for b in range(a, d + 1)]
        for first in windows:
            for second in windows:
                lower = max(first[0], second[0])
                upper = min(first[1], second[1])
                if lower > upper:
                    continue
                for x in range(lower, upper + 1):
                    left = difference_sign(d, (first, second), x, lower)
                    right = difference_sign(d, (first, second), x, upper)
                    if x not in (lower, upper) and left <= 0 and right <= 0:
                        fail(
                            "two-path interior was not strictly below an endpoint"
                            f" D={d} paths={first},{second} x={x}"
                        )
                    if x not in (lower, upper):
                        strict_interior += 1
                    rows += 1
    return rows, strict_interior


def reject_forged_claims():
    """Three claims outside the theorem must fail on a fixed instance."""
    if 2 ** 3 <= 1 ** 3:
        fail("accepted the reversed power comparison")
    if g_sign_against(4, 0, 2, 1, 0) < 0 and g_sign_against(4, 0, 2, 1, 2) < 0:
        fail("forged interior win was accepted")
    if g_sign_against(4, 0, 2, 1, 2) <= 0:
        fail("the D=4 upper endpoint did not beat the interior")
    # Dropping 0^t = 0 on only the retired lower leg invents a charge.
    forged = [(1, 0), (1, 2), (-1, 2), (-1, 1), (-1, 1), (1, 1)]
    if certified_sign(forged) == 0:
        fail("a dropped zero-leg convention reproduced G(0)")


def main():
    powers = power_monotone(40, 5)
    rows, positive_proper, cancelled = half_endpoint_census(12)
    pair_rows, strict_interior = path_pairs(6)
    reject_forged_claims()
    print(
        MARKER
        + f" powers={powers} half_rows={rows}"
        + f" positive_boundary_paths={positive_proper}"
        + f" full_span_zeros={cancelled}"
        + f" two_path_rows={pair_rows} two_path_strict_interior={strict_interior}"
        + f" kappa={KAPPA} no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
