#!/usr/bin/env python3
"""Exact checks for the proper-terminal contact-free rank bill. No new kappa.

The written proof is PROOF.md.  This script replays the exact finite
certificate, the stated finite censuses and the control rejections.  Every
sign comparison is decided with integer square-root arithmetic; no floating
point decides an assertion.
"""

import math
from fractions import Fraction

MARKER = "PASS_PROPER_TERMINAL_HELPER_RANK_BILL"
KAPPA = "363005817/100000000000"


def fail(message):
    raise SystemExit("FAIL: " + message)


def sign_sqrt_sum(terms, bits=64):
    """Sign of sum coef*sqrt(radicand) for nonnegative rational radicands.

    Each term is bounded by an integer truncation with error strictly below one
    unit in the scaled representation, so a positive accumulator beyond the
    accumulated error is a certified sign.
    """
    cleaned = {}
    for c, r in terms:
        if c == 0 or r == 0:
            continue
        if r < 0:
            fail("negative radicand " + repr(r))
        cleaned[r] = cleaned.get(r, 0) + c
    cleaned = [(c, r) for r, c in cleaned.items() if c != 0]
    if not cleaned:
        return 0
    # Clear denominators: sqrt(n/d) = sqrt(n*d)/d.
    scale_den = 1
    for _c, r in cleaned:
        d = r.denominator
        scale_den = scale_den * d // math.gcd(scale_den, d)
    ints = []
    for c, r in cleaned:
        n = r.numerator * (scale_den * scale_den) // r.denominator
        ints.append((c, n))
    shift = 1 << bits
    acc = 0
    err = 0
    for c, n in ints:
        acc += c * math.isqrt(n * shift * shift)
        err += abs(c)
    if acc > err:
        return 1
    if -acc > err:
        return -1
    if err == 0:
        return 0
    if bits > 1 << 16:
        fail("sign unresolved: " + repr(terms))
    return sign_sqrt_sum(terms, bits * 4)


def power_monotone(max_base, max_q):
    """Lemma 1 integer form: 1 <= u <= v implies u^s <= v^s, s = q - p."""
    checked = 0
    for q in range(2, max_q + 1):
        for p in range(1, q):
            s = q - p
            for u in range(1, max_base + 1):
                previous = u ** s
                for v in range(u, max_base + 1):
                    if previous > v ** s:
                        fail("power increase failed at u={} v={} s={}".format(u, v, s))
                    previous = v ** s
                    checked += 1
            if not (2 ** s > 1):
                fail("strict unit power failed at q={} p={}".format(q, p))
    return checked


def g_terms(T, paths, x):
    """Terms of G(x) at t = 1/2; x is a Fraction."""
    terms = [
        (1, Fraction(x)),
        (1, Fraction(T - x)),
        (-1, Fraction(T)),
    ]
    for a, b in paths:
        terms.append((-1, Fraction(x - a)))
        terms.append((-1, Fraction(b - x)))
        terms.append((1, Fraction(b - a)))
    return terms


def g_sign(T, paths, x):
    return sign_sqrt_sum(g_terms(T, paths, x))


def g_diff_sign(T, paths, x, y):
    """Sign of G(x) - G(y)."""
    return sign_sqrt_sum(g_terms(T, paths, x) +
                         [(-c, r) for c, r in g_terms(T, paths, y)])


def grid(A, B, steps):
    """Exact rational grid including both endpoints."""
    return [Fraction(A) + Fraction(B - A) * k / steps for k in range(steps + 1)]


def check_structure(D, T, paths):
    if not (0 < T < D):
        fail("proper terminal violated D={} T={}".format(D, T))
    for a, b in paths:
        if not (0 <= a <= b <= D):
            fail("path outside ambient space {} {} D={}".format(a, b, D))


def one_path_census_clean(max_d=10, steps=8):
    rows = 0
    for D in range(2, max_d + 1):
        for T in range(1, D):
            for a in range(0, T + 1):
                for b in range(T + 1, D + 1):
                    paths = [(a, b)]
                    check_structure(D, T, paths)
                    if a >= T:
                        continue
                    xs = grid(a, T, steps)
                    for x, y in zip(xs, xs[1:]):
                        if g_diff_sign(T, paths, y, x) >= 0:
                            fail("one-path decrease failed D={} T={} a={} b={}"
                                 .format(D, T, a, b))
                        rows += 1
                    if a == 0 and g_sign(T, paths, 0) != 0:
                        fail("G(0) was not zero")
    return rows


def zero_start_census(max_d=8, max_m=3, steps=8):
    """Lemma 4: all paths start at zero, every interior value is negative."""
    from itertools import combinations_with_replacement
    rows = 0
    for D in range(2, max_d + 1):
        for T in range(1, D):
            ends = list(range(T + 1, D + 1))
            for m in range(1, max_m + 1):
                for combo in combinations_with_replacement(ends, m):
                    paths = [(0, b) for b in combo]
                    check_structure(D, T, paths)
                    if g_sign(T, paths, 0) != 0:
                        fail("G(0) not zero for zero-start paths")
                    for x in grid(0, T, steps * T)[1:-1]:
                        if g_sign(T, paths, x) >= 0:
                            fail("zero-start interior not negative D={} T={} b={}"
                                 .format(D, T, combo))
                        rows += 1
    return rows


def terminal_census(max_d=8, max_m=2):
    """Lemma 3: G(T) <= 0 whenever T lies between the path endpoints."""
    from itertools import combinations_with_replacement
    rows = 0
    for D in range(2, max_d + 1):
        for T in range(1, D):
            types = [(a, b) for a in range(0, T + 1) for b in range(T, D + 1)]
            for m in range(1, max_m + 1):
                for combo in combinations_with_replacement(types, m):
                    paths = list(combo)
                    check_structure(D, T, paths)
                    if g_sign(T, paths, T) > 0:
                        fail("positive terminal bill D={} T={} {}".format(D, T, combo))
                    rows += 1
    return rows


def endpoint_census(m, max_d, steps=8):
    """Finite census: no interior point beats both endpoints on this grid."""
    from itertools import combinations_with_replacement
    rows = 0
    for D in range(2, max_d + 1):
        for T in range(1, D):
            types = [(a, b) for a in range(0, T + 1) for b in range(T + 1, D + 1)]
            for combo in combinations_with_replacement(types, m):
                paths = list(combo)
                check_structure(D, T, paths)
                A = max(a for a, b in paths)
                if A >= T:
                    continue
                for x in grid(A, T, steps)[1:-1]:
                    if (g_diff_sign(T, paths, x, A) > 0
                            and g_diff_sign(T, paths, x, T) > 0):
                        fail("interior beats both endpoints at m={} D={} T={} x={} paths={}"
                             .format(m, D, T, x, paths))
                    rows += 1
    return rows


def counterexample():
    """Proposition: four crossing paths beat both endpoints exactly."""
    D, T = 26, 24
    paths = [(3, 25), (17, 26), (0, 25), (6, 25)]
    x0 = Fraction(3819, 160)
    A = max(a for a, b in paths)
    check_structure(D, T, paths)
    if A != 17 or not (A < x0 < T):
        fail("counterexample interval changed")
    if not all(b > T for _a, b in paths):
        fail("counterexample path does not cross the terminal")
    if g_diff_sign(T, paths, x0, A) <= 0:
        fail("interior did not beat the left endpoint")
    if g_diff_sign(T, paths, x0, T) <= 0:
        fail("interior did not beat the terminal")
    if g_sign(T, paths, x0) >= 0:
        fail("counterexample unexpectedly has a nonnegative value")
    return D, T, x0


def controls():
    """Reject forged claims adjacent to the proved statements."""
    D, T = 26, 24
    paths = [(3, 25), (17, 26), (0, 25), (6, 25)]
    x0 = Fraction(3819, 160)
    # 1. A forged claim that the left endpoint wins at the witness.
    if g_diff_sign(T, paths, 17, x0) >= 0:
        fail("control: forged endpoint win was not rejected")
    # 2. Theorem 1 does not apply to four crossing paths: some step increases.
    xs = grid(17, T, 32)
    if not any(g_diff_sign(T, paths, y, x) > 0 for x, y in zip(xs, xs[1:])):
        fail("control: four-path witness was unexpectedly monotone")
    # 3. A forged positive terminal claim at a crossing configuration.
    if g_sign(T, paths, T) > 0:
        fail("control: positive terminal bill was not rejected")
    # 4. Lemma 2 is strict for two positive legs.
    if sign_sqrt_sum([(1, Fraction(9)), (1, Fraction(16)), (-1, Fraction(25))]) != 1:
        fail("control: strict subadditivity failed at 9 and 16")
    return 4


def main():
    checked_power = power_monotone(24, 6)
    one_path = one_path_census_clean(10, 8)
    zero_start = zero_start_census(8, 3, 4)
    terminal = terminal_census(8, 2)
    two_path = endpoint_census(2, 8, 8)
    three_path = endpoint_census(3, 7, 6)
    D, T, x0 = counterexample()
    rejected = controls()
    print(
        "{} power_pairs={} one_path={} zero_start={} terminal={} "
        "two_path={} three_path={} counterexample=D{},T{},x={} controls={} "
        "kappa={} no_new_kappa=true".format(
            MARKER, checked_power, one_path, zero_start, terminal, two_path,
            three_path, D, T, x0, rejected, KAPPA
        )
    )


if __name__ == "__main__":
    main()
