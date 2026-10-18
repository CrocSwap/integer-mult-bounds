#!/usr/bin/env python3
"""Independent audit verifier for PR2298 PROOF.md sections 6, 4, 3a/3b and the
section 5 chirp/twist identity.

Written from PROOF.md (PR #2298 head 8507498d, sha256 4afeb170...f513); it does
not import or read PR2298's packing.py/checks.py.  Python stdlib only, exact
integers/Fractions.  Prints one line per item and the final token
PASS_PR2298_FORMAT_RECOVERY_AUDIT when every positive check holds and every
mutation control is detected.

Scope: exact finite checks plus explicit cutoffs for written implications.  It
is NOT a formal proof of the PR2298 transfer theorem.  Section 2 conclusions are
imported as hypotheses H2; inherited published/callee error units are named and
not re-derived.

Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic,
Claude Opus 5.5).  Apache-2.0.
"""
from fractions import Fraction as Fr
import hashlib
import itertools
import math
import random
import sys

FAILURES = []
S6_CONTROLS = {}
S6_SENSITIVITY = {}
# Least value of each S6 row predicate (asserted, so a changed row derivation
# cannot silently move the published cutoff).
# Order: 6.1, 6.2a, 6.2b, 6.4, 6.5, 6.6a, 6.6b, 6.7, 6.8, 6.9, 6.11, 6.14, 6.15.
S6_EXPECTED_LEAST = [2, 2, 2, 3, 2, 3, 1, 3, 25, 4, 3, 2, 19]
S6_EXPECTED_CUTOFF = 25

PROOF_SHA256 = "4afeb1708cf9568a9cd25afc72b159d5b06d151a6a6aba567a50970b38a1f513"


def check(cond, label):
    if not cond:
        FAILURES.append(label)
    return cond


# ---------------------------------------------------------------------------
# P1. Section 6: disk-margin / error step table with explicit least-b cutoffs.
# H2 (section 2 conclusions plus the section 6 restatement, not re-audited):
#   p = 6b, h = 2^-p, T = 2^L, b/2 <= L, T < 2^b (so L < b; restated in
#   section 6, section 2 itself says log2 T <= b), S < T,
#   gamma <= b/4, d <= b^(1/12), d >= 2 (p >= 2^40), r = 2^ell >= 2.
# Inherited units (named, not re-derived): one component truncation toward
# zero has error < sqrt2*h; a computed unit-phase product has error < 4h and
# does not increase norm; each tensor Gaussian map (A, B0) has error < d p^2 h
# and is a contraction; normalized DFTs and length-normalized convolutions are
# sup-norm contractions (bilinear norm <= 1).
# ---------------------------------------------------------------------------
INV_LN2_UPPER = Fr(14427, 10000)  # 1/ln 2 = 1.442695... < 1.4427


def exp_condition(C, k, c):
    """Predicate for C * b^k < 2^(c b), exact after raising to the power m that
    clears the denominators of k and c.  g(b) = c b ln2 - k ln b - ln C is
    increasing for b > k/(c ln 2) <= k*1.4427/c, so the predicate stays true
    beyond that point once true there."""
    C, k, c = Fr(C), Fr(k), Fr(c)
    m = math.lcm(k.denominator, c.denominator)
    km, cm = int(k * m), int(c * m)
    Cn, Cd = C.numerator ** m, C.denominator ** m

    def pred(b):
        return Cn * b ** km < Cd << (cm * b)

    return pred, max(1, math.ceil(k * INV_LN2_UPPER / c))


def least_b(pred, mono, scan=2048):
    top = max(scan, mono + 1)
    ok = [pred(b) for b in range(1, top + 1)]
    check(ok[-1], "least_b: predicate false at scan top")
    b0 = top
    while b0 > 1 and ok[b0 - 2]:
        b0 -= 1
    return b0


def least_L(pred, scan=5000):
    ok = [pred(L) for L in range(1, scan + 1)]
    check(ok[-1], "least_L: predicate false at scan top")
    L0 = scan
    while L0 > 1 and ok[L0 - 2]:
        L0 -= 1
    return L0


def cdiv(a, b):
    return -(-a // b)


def p1_section6():
    rows = []
    # 6.1 synthetic error sqrt2*ell*h < L h, ell = ceil(L/d), worst d = 2:
    #     2*ceil(L/2)^2 < L^2.  (Larger d only lowers ell.)  Written tail: for
    #     L >= 3, ceil(L/2) <= (L+1)/2 and (L+1)^2 < 2 L^2.
    rows.append(("6.1 sqrt2*ell < L  (synthetic err < Lh)", "L",
                 least_L(lambda L: 2 * cdiv(L, 2) ** 2 < L * L)))
    # 6.2 section 4 gives sqrt2*M*(3ell+1)h; need sqrt2(3ell+1) <= 3L+2 ...
    rows.append(("6.2 sqrt2(3ell+1) <= 3L+2", "L",
                 least_L(lambda L: 2 * (3 * cdiv(L, 2) + 1) ** 2 <= (3 * L + 2) ** 2)))
    # ... and E_ring = M(3L+2) < 5TL with M = T/r <= T (written: 3L+2 < 5L).
    rows.append(("6.2 M(3L+2) < 5TL  (M <= T)", "L", least_L(lambda L: 3 * L + 2 < 5 * L)))
    # 6.4 .7 + E_ring h < .701  <=  5TL 2^-p < 1/1000  <=  5000 b < 2^(5b)
    rows.append(("6.4 .7 + E_ring h < .701", "b", least_b(*exp_condition(5000, 1, 5))))
    # 6.5 scalar conv: E_ring + 4 + 4 (input twists through a bilinear map of
    #     norm <= 1) + 4 (untwist) < 6TL; with M <= T: T(3L+2)+12 < 6TL, T=2^L
    rows.append(("6.5 E_ring + 12 < 6TL", "L",
                 least_L(lambda L: (1 << L) * (3 * L + 2) + 12 < 6 * (1 << L) * L, 300)))
    # 6.6 chirp: 4 (pre-multiplication by conj(a), which is also the error of
    #     the conj(a)x operand) + 4 (chirp operand a) + 6TL (scalar conv)
    #     + 4 (post) = 6TL + 12 < 8TL; the row keeps 16 as a generous budget
    #     (one spare phase unit), which needs TL > 8
    rows.append(("6.6 6TL + 16 < 8TL  (chirp err < 8TLh)", "L",
                 least_L(lambda L: 6 * (1 << L) * L + 16 < 8 * (1 << L) * L, 300)))
    # 6.6 output norm .6 + 8TL h < 1  <=  20 b < 2^(5b)
    rows.append(("6.6 .6 + 8TLh < 1  (legal disk output)", "b", least_b(*exp_condition(20, 1, 5))))
    # 6.7 expansion .5 + d p^2 h < .51  <=  100*36 b^(25/12) < 2^(6b)
    rows.append(("6.7 .5 + d p^2 h < .51", "b", least_b(*exp_condition(3600, Fr(25, 12), 6))))
    # 6.8 2^g(2dp^2 + 8TL) < 9*2^g*TL <=> 2dp^2 < TL; 2dp^2 <= 72 b^(25/12),
    #     TL >= 2^(b/2) b/2  =>  144 b^(13/12) < 2^(b/2)
    rows.append(("6.8 2dp^2 < TL  (E_s = 9*2^g*T*L)", "b", least_b(*exp_condition(144, Fr(13, 12), Fr(1, 2)))))
    # 6.9 .5 + E_s h < .501  <=  9000 b 2^(b/4) 2^b < 2^(6b)  <=  9000 b < 2^(19b/4)
    rows.append(("6.9 .5 + E_s h < .501", "b", least_b(*exp_condition(9000, 1, Fr(19, 4)))))
    # 6.11 1/4 + E_s h < .26  <=  900 b < 2^(19b/4)
    rows.append(("6.11 1/4 + E_s h < .26", "b", least_b(*exp_condition(900, 1, Fr(19, 4)))))
    # 6.12 .26^2 < .5 exactly; 6.13 .51 E_s + sqrt2 <= 2E_s + 2 for all E_s >= 0
    check(Fr(26, 100) ** 2 < Fr(1, 2), "6.12 .26^2 < .5")
    check(Fr(14143, 10000) ** 2 > 2 and Fr(14143, 10000) <= 2, "6.13 sqrt2 < 2")
    # 6.14 S(3E_s+2) < 28*2^g*T^2*L  <=  (S < T)  2 <= 2^g*T*L  (T >= 2, L >= 1);
    #      norm of (u*v)/S: 1/16 + 28*2^g*T^2*L*h < 1  <=  (448/15) b < 2^(15b/4)
    rows.append(("6.14 1/16 + 28 2^g T^2 L h < 1", "b", least_b(*exp_condition(Fr(448, 15), 1, Fr(15, 4)))))
    # 6.15 896 b < 2^(3b/4)  (448 b 2^(-3b/4) < 1/2)
    rows.append(("6.15 448 b 2^(-3b/4) < 1/2", "b", least_b(*exp_condition(896, 1, Fr(3, 4)))))
    # 6.15 exact algebra 2^(2b+4) S * 28*2^g*T^2*L*2^(-6b) < 448 b 2^(g-b)
    rng = random.Random(2298)
    for _ in range(300):
        b = rng.randrange(8, 300)
        L = rng.randrange(cdiv(b, 2), b)
        T = 1 << L
        S = rng.randrange(T // 2 + 1, T)
        g = rng.randrange(0, b // 4 + 1)
        lhs = Fr(28 * S * T * T * L << (2 * b + 4 + g), 1 << (6 * b))
        check(lhs < Fr(448 * b << g, 1 << b), "6.15 exact algebra")
    # Negative controls for the precision/scale budget: the final error bound
    # is 448 b 2^(g + 5b - p).  It must fail for every b when p is lowered to
    # 5b + floor(b/4) (with g = floor(b/4)) or when g is raised to b (p = 6b).
    def final_ok(b, p, g):
        return 448 * b * 2 < 1 << max(0, p - 5 * b - g) if p - 5 * b - g > 0 else False
    check(all(final_ok(b, 6 * b, b // 4) for b in range(19, 2048)), "6.15 positive")
    S6_SENSITIVITY["S6 p lowered to 5b+floor(b/4)"] = not any(final_ok(b, 5 * b + b // 4, b // 4) for b in range(1, 2048))
    # 6.1 needs d >= 2: with d = 1 (ell = L) sqrt2*ell < L never holds.
    S6_SENSITIVITY["S6 d=1 in row 6.1"] = not any(2 * L * L < L * L for L in range(1, 5000))
    S6_SENSITIVITY["S6 gamma raised to b"] = not any(final_ok(b, 6 * b, b) for b in range(1, 2048))
    S6_SENSITIVITY["S6 drop the factor S<2^b (S<2^(2b))"] = not all(
        Fr(28 * (1 << (2 * b - 1)) * (1 << (2 * (b - 1))) * (b - 1) << (2 * b + 4 + b // 4), 1 << (6 * b))
        < Fr(1, 2) for b in range(19, 64))
    need = []
    for name, var, val in rows:
        bb = val if var == "b" else 2 * val      # L >= b/2, so b >= 2 L0 gives L >= L0
        need.append(bb)
        print(f"  S6 {name:44s} least {var} = {val:3d}  -> b >= {bb}")
    b_s6 = max(need)
    check([val for _, _, val in rows] == S6_EXPECTED_LEAST, "S6 per-row least values")
    check(b_s6 == S6_EXPECTED_CUTOFF, "S6 cutoff == 25")
    # Implementation controls that run the least_L / least_b machinery itself.
    # (a) A non-eventual row (6.6 with no slack: 8TL + 16 < 8TL) must be
    #     rejected by least_L's scan-top check.
    n0 = len(FAILURES)
    least_L(lambda L: 8 * (1 << L) * L + 16 < 8 * (1 << L) * L, 300)
    S6_CONTROLS["S6 machinery: non-eventual row 6.6"] = len(FAILURES) > n0
    del FAILURES[n0:]
    # (b) A changed row 6.8 derivation (exponent 13/12 -> 3/2) is still a true
    #     eventual inequality but moves the least b, which the asserted
    #     per-row table must reject.
    S6_CONTROLS["S6 machinery: row 6.8 exponent 3/2"] = (
        least_b(*exp_condition(144, Fr(3, 2), Fr(1, 2))) != S6_EXPECTED_LEAST[8])
    p_d2 = 1 << 40
    b_d2 = cdiv(p_d2, 6)
    check(b_s6 < (1 << 24) < b_d2, "S6 cutoffs below the regime")
    # Remark (H2 consistency only, section 2 not audited): 32 b^(11/20) <= b/4
    # <=> 128^20 <= b^9; least such b.
    lo, hi = 1, 1 << 20
    while lo < hi:
        mid = (lo + hi) // 2
        if 128 ** 20 <= mid ** 9:
            hi = mid
        else:
            lo = mid + 1
    print(f"  S6 every listed step holds for all b >= {b_s6}; regime: recovery b >= 2^24,"
          f" d >= 2 needs b >= {b_d2}, package domain log2 b = 524288")
    print(f"  remark (H2 consistency, not audited): 32 b^(11/20) <= b/4 iff b >= {lo} (< 2^24)")
    return b_s6


def p1_phase_norm(p=3):
    R = 1 << p
    grid = [(x, y) for x in range(-R, R + 1) for y in range(-R, R + 1) if x * x + y * y <= R * R]
    for (ax, ay) in grid:
        for (xx, xy) in grid:
            re = ax * xx - ay * xy
            im = ax * xy + ay * xx
            tr = (abs(re) >> p) * (1 if re >= 0 else -1)
            ti = (abs(im) >> p) * (1 if im >= 0 else -1)
            if not check(tr * tr + ti * ti <= xx * xx + xy * xy, "6.3 phase norm"):
                return
    print(f"  S6 6.3 truncated phase product never increases norm: {len(grid) ** 2} disk-grid pairs (p={p})")


def carry_scan(c, Q0):
    k, digits, ks = 0, [], [0]
    for cj in c:
        digits.append((cj + k) % Q0)
        k = (cj + k) // Q0
        ks.append(k)
    return digits, ks


def p1_carry():
    count, max_gap = 0, None
    for b, q in [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (2, 4), (3, 1), (3, 2)]:
        Q0 = 1 << b
        vecs = list(itertools.product(range(Q0), repeat=q))
        for u in vecs:
            for v in vecs:
                c = [0] * (2 * q - 1)
                for i, ui in enumerate(u):
                    for j, vj in enumerate(v):
                        c[i + j] += ui * vj
                count += 1
                ok = all(0 <= cj < 1 << (3 * b) for cj in c)
                digits, ks = carry_scan(c, Q0)
                ok &= all(0 <= kj <= q * (Q0 - 1) < Q0 * Q0 for kj in ks)
                for j in range(len(c) + 1):
                    ok &= (sum(c[h] * Q0 ** h for h in range(j))
                           == sum(digits[h] * Q0 ** h for h in range(j)) + ks[j] * Q0 ** j)
                U = sum(x * Q0 ** i for i, x in enumerate(u))
                V = sum(x * Q0 ** i for i, x in enumerate(v))
                tail, k = [], ks[-1]
                while k:
                    tail.append(k % Q0)
                    k //= Q0
                ok &= sum(x * Q0 ** i for i, x in enumerate(digits + tail)) == U * V
                ok &= U * V < 1 << (2 * q * b)
                gap = max(ks) - q * (Q0 - 1)
                max_gap = gap if max_gap is None else max(max_gap, gap)
                if not check(ok, f"carry lemma b={b} q={q} u={u} v={v}"):
                    return
    for b in (4, 8, 16, 32, 64):
        Q0 = 1 << b
        for q in (1, 2, 3, 7, 16, 64):
            if q > Q0:
                continue
            c = [min(k + 1, q, 2 * q - 1 - k) * (Q0 - 1) ** 2 for k in range(2 * q - 1)]
            check(max(c) < 1 << (3 * b), "integer range extremal")
            digits, ks = carry_scan(c, Q0)
            check(all(0 <= kj <= q * (Q0 - 1) < Q0 * Q0 for kj in ks), "carry extremal")
            max_gap = max(max_gap, max(ks) - q * (Q0 - 1))
            check(max(ks) == q * (Q0 - 1) - 1 or q * (Q0 - 1) == 1, 'all-max digits reach q(Q0-1)-1')
            count += 1
    print(f"  S6 integer range c<2^(3b) + carry lemma: {count} cases (exhaustive small b,q with q<=2^b,"
          f" extremal to b=64); max over cases of max_j k_j - q(Q0-1) = {max_gap}")


# ---------------------------------------------------------------------------
# P2. Section 4: signed packing, centered extraction, wrap and Q_p(fg/r).
# ---------------------------------------------------------------------------
def pack(coeffs, p, mutate=None):
    B0 = 1 << (4 * p)
    carry, val, carries = 0, 0, [0]
    for i, a in enumerate(coeffs):
        t = a + carry
        blk = t % B0
        carry = (t - blk) // B0 if mutate != "pack_no_carry" else 0
        carries.append(carry)
        val += blk << (4 * p * i)
    return val + carry * B0 ** len(coeffs), carries


def extract(P, r, p, mutate=None):
    B0 = 1 << (4 * p)
    W = B0 ** (2 * r)
    if mutate == "ignore_sign":
        P = abs(P)
    eps = -1 if P < 0 else 0
    U = P - eps * W
    assert 0 <= U < W
    if mutate == "drop_sign_extension":
        eps = 0
    rho, hs, rhos = 0, [], [0]
    for j in range(2 * r):
        t = ((U >> (4 * p * j)) & (B0 - 1)) + rho
        h = t % B0
        if mutate != "unsigned_extraction" and h >= B0 // 2:
            h -= B0
        rho = (t - h) // B0
        hs.append(h)
        rhos.append(rho)
    return hs, rhos, eps


def ordinary(a, c):
    out = [0] * (len(a) + len(c) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(c):
                out[i + j] += x * y
    return out


def real_product(a, c, p, mutate=None):
    """Returns (recovered ordinary coefficients, section 4 lemma flags ok)."""
    r = len(a)
    B0 = 1 << (4 * p)
    A, ca = pack(a, p, mutate)
    C, cc = pack(c, p, mutate)
    ok = A == sum(x * B0 ** i for i, x in enumerate(a))
    ok &= all(k in (-1, 0) for k in ca + cc)
    hs, rhos, eps = extract(A * C, r, p, mutate)
    ok &= all(k in (0, 1) for k in rhos)
    ok &= rhos[-1] + eps == 0
    ok &= hs[-1] == 0
    return hs[:2 * r - 1], ok


def ring_qp(f, g, p, mutate=None):
    r = len(f)
    ell = r.bit_length() - 1
    a = [x for x, _ in f]; b = [y for _, y in f]
    c = [x for x, _ in g]; e = [y for _, y in g]
    ok, pr = True, {}
    for name, (u, v) in {"ac": (a, c), "be": (b, e), "ae": (a, e), "bc": (b, c)}.items():
        h, lem = real_product(u, v, p, mutate)
        ok &= lem and h == ordinary(u, v)
        ok &= max(abs(x) for x in h) <= r << (2 * p) < (1 << (4 * p)) // 2
        # the displayed chain r 2^(2p) < 2^(3p) < B0/2 needs r < 2^p and p >= 2
        # (2^(3p) = B0/2 at p = 1); extraction itself only needs r 2^(2p) < B0/2.
        ok &= p < 2 or r << (2 * p) < 1 << (3 * p) < (1 << (4 * p)) // 2
        pr[name] = h + [0]
    re = [pr["ac"][k] - pr["be"][k] for k in range(2 * r)]
    im = [pr["ae"][k] + pr["bc"][k] for k in range(2 * r)]
    if mutate == "drop_wrap":
        Nre, Nim = re[:r], im[:r]
    else:
        Nre = [re[k] - re[k + r] for k in range(r)]
        Nim = [im[k] - im[k + r] for k in range(r)]
    ok &= all(x * x + y * y <= (r << (2 * p)) ** 2 for x, y in zip(Nre, Nim))
    sh = p if mutate == "shift_p" else p + ell

    def q(N):
        if mutate == "floor_shift":
            return N >> sh
        return (abs(N) >> sh) * (1 if N >= 0 else -1)

    return [(q(x), q(y)) for x, y in zip(Nre, Nim)], ok


def ring_qp_reference(f, g, p):
    """Independent Fraction reference for Q_p(fg/r) in C[y]/(y^r+1); Q_p
    truncates each component toward zero on the 2^-p grid."""
    r = len(f)
    R = 1 << p
    F = [(Fr(x, R), Fr(y, R)) for x, y in f]
    G = [(Fr(x, R), Fr(y, R)) for x, y in g]
    out = []
    for k in range(r):
        zr = zi = Fr(0)
        for i in range(r):
            j = (k - i) % r
            sgn = 1 if i + j < r else -1
            (xr, xi), (yr, yi) = F[i], G[j]
            zr += sgn * (xr * yr - xi * yi)
            zi += sgn * (xr * yi + xi * yr)
        zr, zi = zr / r, zi / r
        tr = lambda z: math.floor(z * R) if z >= 0 else -math.floor(-z * R)
        out.append((tr(zr), tr(zi), zr, zi))
    return out


def compare(f, g, p, mutate=None):
    got, ok = ring_qp(f, g, p, mutate)
    R = 1 << p
    for (gx, gy), (rx, ry, zr, zi) in zip(got, ring_qp_reference(f, g, p)):
        ok &= (gx, gy) == (rx, ry)
        ok &= gx * gx + gy * gy <= R * R
        er, ei = zr - Fr(gx, R), zi - Fr(gy, R)
        ok &= er * er + ei * ei < Fr(2, R * R)
    return ok


def disk(p):
    R = 1 << p
    return [(x, y) for x in range(-R, R + 1) for y in range(-R, R + 1) if x * x + y * y <= R * R]


def p2_section4(mutate=None, quick=False):
    n = 0
    # (a) packing lemma: every real vector, |a_i| <= 2^p
    for r, p in [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (4, 1), (4, 2), (4, 3)]:
        if quick and r == 4 and p > 1:
            continue
        R, B0 = 1 << p, 1 << (4 * p)
        for a in itertools.product(range(-R, R + 1), repeat=r):
            val, car = pack(list(a), p, mutate)
            n += 1
            if not (val == sum(x * B0 ** i for i, x in enumerate(a)) and all(k in (-1, 0) for k in car)):
                return n, False
    # (b) extraction lemma: every real pair, H2 r < 2^p
    for r, p in [(1, 1), (1, 2), (1, 3), (2, 2), (2, 3)]:
        if quick and (r, p) == (2, 3):
            continue
        R = 1 << p
        vecs = [list(v) for v in itertools.product(range(-R, R + 1), repeat=r)]
        for a in vecs:
            for c in vecs:
                h, lem = real_product(a, c, p, mutate)
                n += 1
                if not (lem and h == ordinary(a, c)):
                    return n, False
    # (c) complex Q_p(fg/r): every disk-grid pair at r = 1
    for p in ((1, 2) if quick else (1, 2, 3)):
        pts = disk(p)
        for f in pts:
            for g in pts:
                n += 1
                if not compare([f], [g], p, mutate):
                    return n, False
    # (d) extremal and random instances, r = 2^ell < 2^p, ell <= 6
    rng = random.Random(4)
    for ell in range(0, 7):
        r = 1 << ell
        for p in sorted({ell + 1, ell + 2, 8, 16, 24}):
            if r >= 1 << p:
                continue
            R = 1 << p
            ext = [(R, 0), (-R, 0), (0, R), (0, -R)]
            pats = [[(R, 0)] * r, [(-R, 0)] * r, [(0, -R)] * r,
                    [ext[i % 4] for i in range(r)], [ext[(3 * i) % 4] for i in range(r)],
                    [((-1) ** i * R, 0) for i in range(r)], [(0, 0)] * r]
            for f in pats:
                for g in pats:
                    n += 1
                    if not compare(f, g, p, mutate):
                        return n, False
            def rnd():
                out = []
                for _ in range(r):
                    while True:
                        x, y = rng.randint(-R, R), rng.randint(-R, R)
                        if x * x + y * y <= R * R:
                            break
                    out.append(rng.choice(ext) if rng.random() < .3 else (x, y))
                return out
            for _ in range(5 if quick else 25):
                n += 1
                if not compare(rnd(), rnd(), p, mutate):
                    return n, False
    return n, True


# ---------------------------------------------------------------------------
# P3. Section 3a CRT index map / triangular shifts, 3b exchange words.
# ---------------------------------------------------------------------------
def p3_crt(order_fwd="dec", order_inv="inc"):
    ok, cases = True, 0
    for s in [(3, 5), (5, 3), (3, 5, 7), (7, 3, 5), (5, 7, 3), (3, 5, 7, 11), (11, 7, 5, 3), (3, 7, 5, 13)]:
        d = len(s)
        P = [math.prod(s[:i]) for i in range(d)]
        mu = [pow(P[i], -1, s[i]) for i in range(d)]
        S = math.prod(s)
        t = [1 << (x - 1).bit_length() for x in s]      # padded dyadic lengths, s_i < t_i
        digits = lambda k: tuple((k // P[i]) % s[i] for i in range(d))
        bmap = lambda a: tuple((a[i] + mu[i] * sum(a[j] * P[j] for j in range(i))) % s[i] for i in range(d))
        seen = set()
        for k in range(S):
            bb = bmap(digits(k))
            ok &= bb == tuple((k * mu[i]) % s[i] for i in range(d))   # x^k -> prod x_i^(k mu_i)
            seen.add(bb)
        ok &= len(seen) == S
        for k1 in range(0, S, max(1, S // 37)):
            for k2 in range(0, S, max(1, S // 29)):
                b1, b2, b3 = bmap(digits(k1)), bmap(digits(k2)), bmap(digits((k1 + k2) % S))
                ok &= all((b1[i] + b2[i]) % s[i] == b3[i] for i in range(d))
        box = {}
        for pos in itertools.product(*[range(x) for x in t]):
            valid = all(pos[i] < s[i] for i in range(d))
            box[pos] = 1 + sum(pos[i] * P[i] for i in range(d)) if valid else 0

        def apply(bx, inverse, order):
            for i in (range(d - 1, -1, -1) if order == "dec" else range(d)):
                new = {}
                for pos, val in bx.items():
                    if pos[i] < s[i] and all(pos[j] < s[j] for j in range(i)):
                        off = mu[i] * sum(pos[j] * P[j] for j in range(i))
                        ni = (pos[i] - off) % s[i] if inverse else (pos[i] + off) % s[i]
                        new[pos[:i] + (ni,) + pos[i + 1:]] = val
                    else:
                        new[pos] = val
                bx = new
                if any(val and not all(pos[j] < s[j] for j in range(d)) for pos, val in bx.items()):
                    return None
            return bx

        cases += 1
        fwd = apply(box, False, order_fwd)
        target = {pos: 0 for pos in box}
        for k in range(S):
            target[bmap(digits(k))] = k + 1
        ok &= fwd == target
        ok &= fwd is not None and apply(fwd, True, order_inv) == box
    return ok, cases


def p3_words(mutate=None):
    def interchange(w, i, j, width):
        return w[:i] + w[j:j + width] + w[i + width:j] + w[i:i + width] + w[j + width:]

    def bitmove(w, i, j):
        x, w2 = w[i], w[:i] + w[i + 1:]
        return w2[:j] + [x] + w2[j:]

    ok, n = True, 0
    for m in range(1, 7):
        for g in range(0, 7):
            e, X = ["e"], [f"x{i}" for i in range(m)]
            G, Y = [f"G{i}" for i in range(g)], [f"y{i}" for i in range(m)]
            # line 1: (e x) G y -> e y G x -> y G e x
            w = e + X + G + Y
            if mutate == "swap_words":            # apply the line-2 recipe instead
                w1 = interchange(bitmove(w, 0, len(w) - 1), 0, m + g, m)
            else:
                w1 = interchange(w, 1, 1 + m + g, m)
                if mutate != "omit_bitmove":
                    w1 = bitmove(w1, 0, m + g)
            ok &= w1 == Y + G + e + X
            # line 2: x G (e y) -> e x G y -> e y G x
            w = X + G + e + Y
            if mutate == "swap_words":            # apply the line-1 recipe instead
                w2 = bitmove(interchange(w, 0, m + g + 1, m), 0, m + g)
            else:
                w2 = w if mutate == "omit_bitmove" else bitmove(w, m + g, 0)
                w2 = interchange(w2, 1, 1 + m + g, m) if w2[0] == "e" else w2
            ok &= w2 == e + Y + G + X
            n += 2
    return ok, n


# ---------------------------------------------------------------------------
# P4. Section 5 chirp identity (exact roots of unity) and zeta twist.
# ---------------------------------------------------------------------------
def p4_chirp(sign=-1, even=True, conj_outer=True):
    """Unit-vector check of Q F_t x = conj(a) * [a conv (conj(a) x)] / T.  With
    x = e_j every entry on both sides is zeta_N^u / T, so equality is equality
    of exponents mod N.  F_t has kernel exp(sign*2*pi*i*j*m/t) (source07 fixes
    sign = -1)."""
    boxes = ([((4, 3),), ((8, 3),), ((8, 5),), ((8, 7),), ((16, 13),), ((4, 3), (8, 5)),
              ((8, 7), (4, 3)), ((16, 11), (8, 3))] if even else [((5, 3),), ((7, 3),), ((9, 5),)])
    ok, n = True, 0
    for box in boxes:
        ts, ss = [t for t, _ in box], [s for _, s in box]
        N = math.lcm(*[2 * t for t in ts])
        D = range(len(ts))
        chirp = lambda j: sum(-ss[i] * j[i] * j[i] * (N // (2 * ts[i])) for i in D)
        idx = list(itertools.product(*[range(t) for t in ts]))
        for j in idx:
            for k in idx:
                lhs = sum(sign * 2 * j[i] * ((-ss[i] * k[i]) % ts[i]) * (N // (2 * ts[i])) for i in D)
                kj = tuple((k[i] - j[i]) % ts[i] for i in D)
                rhs = (-chirp(k) if conj_outer else chirp(k)) + chirp(kj) - chirp(j)
                ok &= (lhs - rhs) % N == 0
                n += 1
    return ok, n


def zmul(x, y, r):
    """Product in Z[zeta] = Z[y]/(y^r+1), zeta = exp(pi i/r), r a power of 2."""
    out = [0] * r
    for i, a in enumerate(x):
        if a:
            for j, b in enumerate(y):
                if i + j >= r:
                    out[i + j - r] -= a * b
                else:
                    out[i + j] += a * b
    return out


def zpow(k, r):
    k %= 2 * r
    v = [0] * r
    v[k % r] = 1 if k < r else -1
    return v


def p4_twist(omit=False):
    rng = random.Random(5)
    ok, n = True, 0
    for r in (1, 2, 4, 8):
        tests = []
        if r <= 4:
            vals = list(itertools.product((-1, 0, 1), repeat=r))
            tests = [(f, g) for f in vals for g in vals]
        tests += [([rng.randint(-9, 9) for _ in range(r)], [rng.randint(-9, 9) for _ in range(r)]) for _ in range(50)]
        for f, g in tests:
            cyc = [sum(f[i] * g[(k - i) % r] for i in range(r)) for k in range(r)]
            tw = lambda i: zpow(0 if omit else i, r)
            F = [[x * c for c in tw(i)] for i, x in enumerate(f)]
            G = [[x * c for c in tw(i)] for i, x in enumerate(g)]
            for k in range(r):
                acc = [0] * r
                for i in range(r):
                    j = (k - i) % r
                    sgn = 1 if i + j < r else -1
                    acc = [u + sgn * v for u, v in zip(acc, zmul(F[i], G[j], r))]
                ok &= zmul(acc, zpow(0 if omit else -k, r), r) == [cyc[k]] + [0] * (r - 1)
            n += 1
    return ok, n


# ---------------------------------------------------------------------------
def main():
    print("PR2298 PROOF.md sections 6/4/3/5 independent audit (PROOF.md sha256 4afeb170...f513)")
    for a in sys.argv[1:]:
        if a.startswith("--proof="):
            digest = hashlib.sha256(open(a.split("=", 1)[1], "rb").read()).hexdigest()
            check(digest == PROOF_SHA256, "PROOF.md pin")
            print(f"  pin PROOF.md sha256 {digest} {'matches' if digest == PROOF_SHA256 else 'MISMATCH'}")
    b_s6 = p1_section6()
    p1_phase_norm()
    p1_carry()
    n, ok = p2_section4()
    check(ok, "S4 positive")
    print(f"  S4 signed packing / centered extraction / wrap / Q_p(fg/r): {n} instances ok={ok}")
    controls = dict(S6_CONTROLS)
    for mut in ["pack_no_carry", "unsigned_extraction", "ignore_sign", "drop_sign_extension",
                "shift_p", "drop_wrap", "floor_shift"]:
        controls["S4 " + mut] = not p2_section4(mutate=mut, quick=True)[1]
    ok3, c3 = p3_crt()
    check(ok3, "S3a positive")
    print(f"  S3a CRT map, triangular shifts in padded box, inverse: {c3} prime tuples (d<=4) ok={ok3}")
    controls["S3a forward shifts in increasing i"] = not p3_crt(order_fwd="inc")[0]
    controls["S3a inverse in decreasing i"] = not p3_crt(order_inv="dec")[0]
    okw, nw = p3_words()
    check(okw, "S3b positive")
    print(f"  S3b exchange words: {nw} labelled instances (m<=6, |G|<=6) ok={okw}")
    controls["S3b swap the two words"] = not p3_words("swap_words")[0]
    controls["S3b omit the bit move"] = not p3_words("omit_bitmove")[0]
    ok4, n4 = p4_chirp()
    check(ok4, "S5 chirp positive")
    print(f"  S5 chirp identity, kernel exp(-2 pi i jk/t): {n4} unit-vector entries ok={ok4}")
    controls["S5 opposite DFT sign"] = not p4_chirp(sign=+1)[0]
    controls["S5 odd target lengths"] = not p4_chirp(even=False)[0]
    controls["S5 unconjugated outer chirp"] = not p4_chirp(conj_outer=False)[0]
    okt, nt = p4_twist()
    check(okt, "S5 twist positive")
    print(f"  S5 zeta twist turns negacyclic into cyclic: {nt} instances ok={okt}")
    controls["S5 omit twist"] = not p4_twist(omit=True)[0]
    for name, detected in controls.items():
        print(f"  control {name:38s} {'DETECTED' if detected else 'NOT DETECTED'}")
        check(detected, f"control {name}")
    # Hypothesis-sensitivity checks: each weakened H2 premise makes the stated
    # sufficient bound fail.  They are true by construction and do not exercise
    # the cutoff machinery, so they are not counted as mutation controls.
    for name, fails in S6_SENSITIVITY.items():
        print(f"  sensitivity {name:34s} {'BOUND FAILS' if fails else 'BOUND STILL HOLDS'}")
        check(fails, f"sensitivity {name}")
    print(f"  {len(controls)} mutation controls, {len(S6_SENSITIVITY)} hypothesis-sensitivity checks")
    if FAILURES:
        print("FAIL", FAILURES[:10])
        return 1
    print(f"S6 explicit cutoff: every section 6 eventual step holds for all b >= {b_s6}")
    print("PASS_PR2298_FORMAT_RECOVERY_AUDIT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
