#!/usr/bin/env python3
"""Independent check of PR #4599 (petalas): four binary full-guard events lie below the product of their marginals.

Setting (#4599): U_1..U_4 pairwise orthogonal rank-one idempotents on F_2^m (normalized U_t = e_t e_t^T), P_t = I - U_t,
G uniform on GL_m(F_2); E_t: every leading principal minor of G P_t G^-1 of orders 1..m-1 is nonzero. #4599 claims
Pr(E_1..E_4) < s_m^4 with s_m = 3^n/((2^m - 1) 2^n), n = m - 1, for all m >= 4, via a spectral bound for m >= 85
and exact comparisons for 4 <= m <= 84.

Independent route (no #4275 character law, no #4227 marginal formula, nothing imported from #4599):
  * the order-j minor of G P_t G^-1 = I - g_t h_t^T is 1 - sum_{i<=j} h_t[i] g_t[i] (g_t column t of G, h_t row t
    of G^-1);
  * for k requests, passing headers are counted through the first k columns X and first k rows Y of G^-1: pairs with
    Y X = sum_i y_i x_i^T = I_k whose first m-1 prefix sums have zero diagonal; each such pair extends to exactly
    |GL_{m-k}| headers (the remaining columns are an ordered basis of ker Y);
  * the ordered sequences are counted exactly by a dynamic programme over zero-diagonal k x k matrices, each step
    weighted by the number of factor pairs (y, x) with disjoint supports.
This gives Pr(E_1) and Pr(E_1..E_4) for every 4 <= m <= 85 as exact fractions. The verifier then
  * checks Pr(E_1) = s_m (independently confirming the marginal law) and Pr(E_1..E_4) < Pr(E_1)^4 for every m;
  * compares the direct joint count with the signed spectrum printed in #4599 PROOF.md (transcribed) at every m;
  * re-checks the integer constants of section 3 of #4599 (m >= 85) from that table;
  * anchors the reformulation by brute force from the leading-minor definition over GL_3 and GL_4.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
from itertools import product
import json
import sys

M_MAX = 85
# #4599 PROOF.md section 2: z -> signed multiplicity b_z of N_n = sum_z b_z z^n (transcribed, cited).
SPECTRUM = {81: 1, 63: -12, 57: 24, 55: -8, 51: -24, 49: 18, 47: -48, 45: 118, 43: -68, 41: 85, 39: -180,
            37: 228, 35: -336, 33: 399, 31: -444, 29: 502, 27: -548, 25: 523, 23: -332, 21: 144, 19: -48, 17: 6}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def gl_order(n):
    out = 1
    for i in range(n):
        out *= 2 ** n - 2 ** i
    return out


def outer(y, x, k):
    return sum(1 << (k * a + b) for a in range(k) if y >> a & 1 for b in range(k) if x >> b & 1)


def pass_probabilities(k, m_max):
    """{m: Pr(all k events)} for k <= m <= m_max, by the zero-diagonal prefix DP."""
    zero_diag, anything = Counter(), Counter()
    for y, x in product(range(1 << k), repeat=2):
        r = outer(y, x, k)
        anything[r] += 1
        if y & x == 0:
            zero_diag[r] += 1
    ident = sum(1 << (k * a + a) for a in range(k))
    state, out = Counter({0: 1}), {}
    for m in range(1, m_max + 1):
        if m >= k:
            pairs = sum(w * anything.get(s ^ ident, 0) for s, w in state.items())
            out[m] = Fraction(pairs * gl_order(m - k), gl_order(m))
        nxt = Counter()
        for s, ws in state.items():
            for r, wr in zero_diag.items():
                nxt[s ^ r] += ws * wr
        state = nxt
    return out


def mat_mul(a, b, n):
    return [[sum(a[i][l] & b[l][j] for l in range(n)) & 1 for j in range(n)] for i in range(n)]


def inverse(a, n):
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


def guards_pass(a, n):
    """Leading principal minors of orders 1..n-1 nonzero, by elimination without pivoting."""
    m = [row[:] for row in a]
    for c in range(n - 1):
        if not m[c][c]:
            return False
        for r in range(c + 1, n):
            if m[r][c]:
                m[r] = [u ^ v for u, v in zip(m[r], m[c])]
    return True


def brute_force(n, k):
    """Exact (Pr(E_1), Pr(E_1..E_k)) over GL_n from the leading-minor definition."""
    reqs = [[[int(i == j) ^ (i == t and j == t) for j in range(n)] for i in range(n)] for t in range(k)]
    one = joint = total = 0
    for bits in range(1 << (n * n)):
        g = [[bits >> (n * i + j) & 1 for j in range(n)] for i in range(n)]
        gi = inverse(g, n)
        if gi is None:
            continue
        total += 1
        ok = [guards_pass(mat_mul(mat_mul(g, p, n), gi, n), n) for p in reqs]
        one += ok[0]
        joint += all(ok)
    return Fraction(one, total), Fraction(joint, total)


def spectral_joint(m, spectrum):
    n, x = m - 1, 2 ** m
    s = Fraction(3 ** n, (x - 1) * 2 ** n)
    big_n = sum(b * z ** n for z, b in spectrum.items())
    h = Fraction((x - 1) ** 3, (x - 2) * (x - 4) * (x - 8))
    return Fraction(big_n, 81 ** n) * h * s ** 4


def main():
    marg, joint = pass_probabilities(1, M_MAX), pass_probabilities(4, M_MAX)
    rows = []
    for m in range(4, M_MAX + 1):
        n = m - 1
        need(marg[m] == Fraction(3 ** n, (2 ** m - 1) * 2 ** n), "marginal law s_m at m=%d" % m)
        need(joint[m] < marg[m] ** 4, "product inequality at m=%d" % m)
        need(joint[m] == spectral_joint(m, SPECTRUM), "#4599 spectrum table vs direct count at m=%d" % m)
        rows.append((m, joint[m] / marg[m] ** 4))
    need(joint[4] == 0 and joint[5] == Fraction(1, 208320) and marg[5] == Fraction(81, 496), "m = 4, 5 values")
    deficit = {m: (1 - rho) / Fraction(7, 9) ** (m - 1) for m, rho in rows}
    # 12 - deficit is dominated by the next base: |12 - d_m| <= 4083 (57/63)^n + O(2^-n) correction
    need(all(abs(deficit[m] - 12) < 4100 * Fraction(57, 63) ** (m - 1) + 20 * Fraction(9, 14) ** (m - 1)
             for m in range(40, M_MAX + 1)), "(1 - rho_m)/(7/9)^n approaches 12")
    tail = sum(abs(b) for z, b in SPECTRUM.items() if z < 63)
    need(tail == 4083 and max(z for z in SPECTRUM if z < 63) == 57, "|R_n| <= 4083 * 57^n")
    need(4083 * 57 ** 84 < 63 ** 84 and 9 * 9 ** 84 < 14 ** 84 and 11 * 7 ** 84 < 9 ** 84 and 11 * 512 < 18 * 315,
         "section 3 integer inequalities")
    need(all((x - 1) ** 3 - (x - 2) * (x - 4) * (x - 8) == 11 * x * x - 53 * x + 63 for x in range(1, 200)),
         "H numerator minus denominator")
    for n_, k_ in ((3, 1), (3, 3), (4, 1), (4, 4)):
        p1, pk = brute_force(n_, k_)
        need(p1 == pass_probabilities(1, n_)[n_] and pk == pass_probabilities(k_, n_)[n_],
             "brute force GL_%d, k=%d" % (n_, k_))
    mutated = dict(SPECTRUM)
    mutated[17] += 1
    need(any(joint[m] != spectral_joint(m, mutated) for m in range(4, M_MAX + 1)),
         "failure control: a one-unit table change is detected")
    print(json.dumps({"status": "PASS_PR4599_INDEPENDENT_CHECK",
                      "dimensions_checked": [4, M_MAX], "marginal_equals_s_m": True,
                      "joint_below_product_all_m": True, "spectrum_table_matches_direct_count_all_m": True,
                      "m5": {"joint": str(joint[5]), "marginal": str(marg[5])},
                      "rho": {str(m): "%.12f" % float(r) for m, r in rows if m in (5, 6, 8, 12, 20, 40, 85)},
                      "deficit_ratio": {str(m): "%.6f" % float(deficit[m]) for m in (20, 40, 85)},
                      "section3_constants": True, "brute_force_GL3_GL4": True, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
