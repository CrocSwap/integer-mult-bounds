#!/usr/bin/env python3
"""Five binary full-guard events lie strictly below the product of their marginals (k = 5 of #4275 OQ2).

Setting (#4275/#4599): U_1..U_5 pairwise orthogonal rank-one idempotents on F_2^m, m >= 5 (normalized U_t = e_t e_t^T),
P_t = I - U_t, G uniform on GL_m(F_2); E_t: every leading principal minor of G P_t G^-1 of orders 1..m-1 is nonzero.
With n = m - 1, X = 2^m and s_m = 3^n/((X - 1) 2^n) the common marginal, this verifier certifies

    Pr(E_1 .. E_5) < s_m^5 for every m >= 5,   1 - rho_m = 20 (7/9)^n + O((19/21)^n (7/9)^n).

Steps (PROOF.md gives the argument):
  1. reduction: Pr(E_1..E_5) = D_n(E) |GL_{m-5}| / |GL_m|, where D_n(E) is the weighted number of ordered sequences
     of n zero-diagonal rank-<=1 increments y x^T (weighted by factor pairs (y, x) with disjoint supports) summing to
     E = J - I_5; the m-th increment is then forced to be J. Hence rho_m = (N_n / 243^n) H(X) with
     N_n = 2^20 D_n(E) and H(X) = (X - 1)^4 / ((X - 2)(X - 4)(X - 8)(X - 16));
  2. N_n = sum_c (-1)^|c| w^(c)^n over the 2^20 characters c of the zero-diagonal 5 x 5 matrices, w^ the
     Walsh-Hadamard transform of the increment weights, computed exactly here (62 signed bases);
  3. cross-checks of the spectrum against direct meet-in-the-middle counts of D_n(E) for n = 4, 5, 6 and against the
     2,880 complete headers at m = 6 (#4598, independently recounted in #4605); the marginal law from the same
     reduction at k = 1; the reduction itself against brute force over GL_3 and GL_4 (k = 1, 3, 4);
  4. uniform tail for n >= 117 from exact integer inequalities; exact rational comparisons for 5 <= m <= 118.
Successor work to petalas's #4275 (character law) and #4599 (k = 4), whose method is followed and credited.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
from itertools import product
import json
import sys

K = 5
N0 = 117                      # uniform range n >= N0, i.e. m >= 118
OFF = [(a, b) for a in range(K) for b in range(K) if a != b]
BIT = {p: i for i, p in enumerate(OFF)}
E = (1 << len(OFF)) - 1       # J - I_5 in the zero-diagonal coordinates


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def gl_order(n):
    out = 1
    for i in range(n):
        out *= 2 ** n - 2 ** i
    return out


def increment_weights():
    """Zero-diagonal rank-<=1 increments y x^T, keyed by their 20-bit off-diagonal pattern, weighted by pairs."""
    w = Counter()
    for y, x in product(range(1 << K), repeat=2):
        if y & x == 0:
            w[sum(1 << BIT[(a, b)] for a in range(K) if y >> a & 1 for b in range(K) if x >> b & 1)] += 1
    need(sum(w.values()) == 3 ** K and w[0] == 2 ** (K + 1) - 1 and len(w) == 181, "increment weights")
    return w


def signed_spectrum(w):
    """{z: b_z} with N_n = sum_z b_z z^n, by an exact Walsh-Hadamard transform over 2^20 characters."""
    size = 1 << len(OFF)
    a = [0] * size
    for r, v in w.items():
        a[r] = v
    h = 1
    while h < size:
        for i in range(0, size, 2 * h):
            for j in range(i, i + h):
                u, v = a[j], a[j + h]
                a[j], a[j + h] = u + v, u - v
        h *= 2
    spec = Counter()
    for c, z in enumerate(a):
        spec[z] += -1 if bin(c).count("1") & 1 else 1
    return {z: b for z, b in spec.items() if b}


def big_n(spec, n):
    return sum(b * z ** n for z, b in spec.items())


def direct_counts(w):
    """D_n(E) for n = 4, 5, 6 by meet-in-the-middle, without characters."""
    def conv(t, u):
        out = Counter()
        for p, wp in t.items():
            for q, wq in u.items():
                out[p ^ q] += wp * wq
        return out
    d2 = conv(w, w)
    d3 = conv(d2, w)
    return {4: sum(v * d2.get(p ^ E, 0) for p, v in d2.items()),
            5: sum(v * d3.get(p ^ E, 0) for p, v in d2.items()),
            6: sum(v * d3.get(p ^ E, 0) for p, v in d3.items())}


def h_factor(x):
    return Fraction((x - 1) ** 4, (x - 2) * (x - 4) * (x - 8) * (x - 16))


def rho(spec, m):
    n = m - 1
    return Fraction(big_n(spec, n), 243 ** n) * h_factor(2 ** m)


def joint(spec, m):
    n, x = m - 1, 2 ** m
    return Fraction(big_n(spec, n), 2 ** (5 * n) * (x - 1) * (x - 2) * (x - 4) * (x - 8) * (x - 16))


def brute_force(n, k):
    def mul(a, b):
        return [[sum(a[i][l] & b[l][j] for l in range(n)) & 1 for j in range(n)] for i in range(n)]

    def inv(a):
        m = [row[:] + [int(i == j) for j in range(n)] for i, row in enumerate(a)]
        for c in range(n):
            p = next((r for r in range(c, n) if m[r][c]), None)
            if p is None:
                return None
            m[c], m[p] = m[p], m[c]
            for r in range(n):
                if r != c and m[r][c]:
                    m[r] = [u ^ v for u, v in zip(m[r], m[c])]
        return [row[n:] for row in m]

    def passes(a):
        m = [row[:] for row in a]
        for c in range(n - 1):
            if not m[c][c]:
                return False
            for r in range(c + 1, n):
                if m[r][c]:
                    m[r] = [u ^ v for u, v in zip(m[r], m[c])]
        return True

    reqs = [[[int(i == j) ^ (i == t and j == t) for j in range(n)] for i in range(n)] for t in range(k)]
    hits = total = 0
    for bits in range(1 << (n * n)):
        g = [[bits >> (n * i + j) & 1 for j in range(n)] for i in range(n)]
        gi = inv(g)
        if gi is not None:
            total += 1
            hits += all(passes(mul(mul(g, p), gi)) for p in reqs)
    return Fraction(hits, total)


def reduction_probability(k, m):
    """Pr(E_1..E_k) on GL_m by the pair reduction, by a direct DP over all k x k matrices (small k only)."""
    zero, anything = Counter(), Counter()
    for y, x in product(range(1 << k), repeat=2):
        r = sum(1 << (k * a + b) for a in range(k) if y >> a & 1 for b in range(k) if x >> b & 1)
        anything[r] += 1
        if y & x == 0:
            zero[r] += 1
    state = Counter({0: 1})
    for _ in range(m - 1):
        nxt = Counter()
        for s, ws in state.items():
            for r, wr in zero.items():
                nxt[s ^ r] += ws * wr
        state = nxt
    ident = sum(1 << (k * a + a) for a in range(k))
    pairs = sum(v * anything.get(s ^ ident, 0) for s, v in state.items())
    return Fraction(pairs * gl_order(m - k), gl_order(m))


def main():
    w = increment_weights()
    spec = signed_spectrum(w)
    top = sorted(spec, reverse=True)
    need(len(spec) == 62 and min(spec) > 0, "62 positive signed bases")
    need([(z, spec[z]) for z in top[:3]] == [(243, 1), (189, -20), (171, 60)], "leading spectrum 243, -20*189, 60*171")
    need(big_n(spec, 0) == 0, "N_0 = 0 since E is nonzero")
    # step 3: cross-checks of the spectrum and of the reduction
    direct = direct_counts(w)
    need(all(direct[n] << 20 == big_n(spec, n) for n in (4, 5, 6)), "spectrum vs direct counts n = 4, 5, 6")
    need(direct[4] == 0 and joint(spec, 5) == 0, "m = 5: no passing header")
    need(joint(spec, 6) * gl_order(6) == 2880, "m = 6: 2,880 headers (#4598, #4605)")
    for m in range(1, 12):
        need(reduction_probability(1, m) == Fraction(3 ** (m - 1), (2 ** m - 1) * 2 ** (m - 1)), "marginal law")
    for n_, k_ in ((3, 1), (3, 3), (4, 1), (4, 3), (4, 4)):
        need(brute_force(n_, k_) == reduction_probability(k_, n_), "reduction vs brute force GL_%d k=%d" % (n_, k_))
    for m in range(4, 9):
        n_ = m - 1
        rho4 = reduction_probability(4, m) / Fraction(3 ** n_, (2 ** m - 1) * 2 ** n_) ** 4
        need(rho4 < 1, "k = 4 control (#4599) at m = %d" % m)
    # step 4a: exact finite range 5 <= m <= N0 + 1
    rows = {}
    for m in range(5, N0 + 2):
        s = Fraction(3 ** (m - 1), (2 ** m - 1) * 2 ** (m - 1))
        need(joint(spec, m) < s ** 5 and rho(spec, m) == joint(spec, m) / s ** 5, "strict inequality at m = %d" % m)
        rows[m] = rho(spec, m)
    # step 4b: uniform range n >= N0 (m >= N0 + 1), x = (7/9)^n
    a_tail = sum(abs(b) for z, b in spec.items() if z < 189)
    need(max(z for z in spec if z < 189) == 171 and a_tail == 1048555, "|R_n| <= 1048555 * 171^n")
    need(a_tail * 171 ** N0 <= 9 * 189 ** N0, "R_n/243^n <= 9 x for n >= N0 (ratio 171/189 < 1)")
    need(all((x - 1) ** 4 - (x - 2) * (x - 4) * (x - 8) * (x - 16) == 26 * x ** 3 - 274 * x ** 2 + 956 * x - 1023
             for x in range(1, 300)), "H numerator minus denominator")
    need(all(-274 * x * x + 956 * x - 1023 < 0 for x in range(4, 300)) and 26 * 1024 < 85 * 315,
         "H(X) - 1 < 85/X for X >= 32 (denominator >= (315/1024) X^4)")
    need(85 * 9 ** N0 <= 2 * 14 ** N0, "85/X = 42.5/2^n <= x for n >= N0")
    need(11 * 7 ** N0 < 9 ** N0, "1 - 11 x > 0")
    # then rho_m <= (1 - 11x)(1 + x) = 1 - 10x - 11x^2 < 1 for every n >= N0
    deficit = {m: (1 - rows[m]) / Fraction(7, 9) ** (m - 1) for m in (20, 40, 80, 118)}
    need(abs(deficit[118] - 20) < Fraction(1, 100), "leading deficit -> 20")
    mutated = dict(spec)
    mutated[189] += 1
    need(any(direct[n] << 20 != big_n(mutated, n) for n in (4, 5, 6)), "failure control: table mutation detected")
    print(json.dumps({"status": "PASS_FIVE_EVENT_PRODUCT_INEQUALITY",
                      "spectrum_bases": len(spec), "leading": [[z, spec[z]] for z in top[:4]],
                      "finite_range_m": [5, N0 + 1], "uniform_range_m": ">= %d" % (N0 + 1),
                      "m6_headers": 2880, "m7_joint": str(joint(spec, 7)),
                      "rho": {str(m): "%.12f" % float(rows[m]) for m in (6, 7, 8, 12, 20, 40, 80, 118)},
                      "deficit_ratio": {str(m): "%.6f" % float(d) for m, d in deficit.items()},
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
