"""Exact checks for the maximum fiber of refined recovery chains (stdlib only).

Prints PASS_REFINED_RECOVERY_MAX_FIBER on success.
"""
import hashlib
import itertools
import json
import math
import pathlib
import random
from fractions import Fraction
from functools import lru_cache

HERE = pathlib.Path(__file__).resolve().parent
FIXTURE = HERE.parent / "precision-state-frontier" / "FIXTURE.json"
FIXTURE_SHA = "2ca4d7550fcae5b757ec500f87aee1d2ef9f64b59e4abe2bda93319521304af8"
RESULT = HERE / "RESULT.json"
N, MODES = 112, 8
F = (13**8 + 14 * 13**4 + 1) // 16
SMALL = range(-8, 8)  # tie states that can still meet a 12-element box
C_MAX = Fraction(23, 12)


def fail(msg):
    raise SystemExit("FAIL: " + msg)


def check(cond, msg):
    if not cond:
        fail(msg)


def wt(u):
    return bin(u).count("1")


# ---------------------------------------------------------------- source code C

def load_rows():
    raw = FIXTURE.read_bytes()
    check(hashlib.sha256(raw).hexdigest() == FIXTURE_SHA, "fixture hash")
    cols = json.loads(raw)["mode_columns"]
    check(len(cols) == MODES and all(len(c) == N for c in cols), "fixture shape")
    return [tuple(cols[j][i] for j in range(MODES)) for i in range(N)]


def code_from_rows(rows):
    """C = {q in F2^8 : M q = 0 mod 2}, as 8-bit masks."""
    code = [q for q in range(256)
            if all(sum(r[k] for k in range(MODES) if q >> k & 1) % 2 == 0 for r in rows)]
    check(len(code) == 16, "|C| = 16")
    check(all(wt(a & b) % 2 == 0 for a in code for b in code), "C self-orthogonal (so self-dual)")
    check(sorted(wt(c) for c in code) == [0] + [4] * 14 + [8], "C is the [8,4,4] code")
    return code


def coset_sums(code):
    w = lambda u: 7 ** (8 - wt(u)) * 6 ** wt(u)
    S = {u: sum(w(u ^ c) for c in code) for u in range(256)}
    check(S[0] == F, "S(C) = F")
    check({S[u] for u in range(256) if wt(u) % 2} == {50983170}, "odd coset sum")
    check({S[u] for u in range(256) if wt(u) % 2 == 0 and u not in code} == {50979600},
          "even coset sum")
    return Fraction(50979600, F)


# ---------------------------------------------------------------- rounding boxes

def rnd(x):
    """Nearest integer, half ties away from zero."""
    f = math.floor(x)
    d = x - f
    if d != Fraction(1, 2):
        return f + (d > Fraction(1, 2))
    return f + 1 if x > 0 else f


@lru_cache(maxsize=None)
def box(s):
    """Q(s) = {q : R((s + 56 q)/52) = q}, as a sorted tuple."""
    c = -s // 4
    return tuple(q for q in range(c - 10, c + 11) if rnd(Fraction(s + 56 * q, 52)) == q)


def tie_range(x):
    """Box Q(4x+2) shifted by x (so r = q + x), by the class of x."""
    if -7 <= x <= 6:
        return range(-6, 6)
    return range(-6, 7) if x >= 7 else range(-7, 6)


def check_boxes():
    """Lemma 1 on a window; PROOF.md section 2 proves it for every s."""
    for s in range(-3000, 3001):
        q = box(s)
        if s % 4 != 2:
            check(q == tuple(v for v in range(-s // 4 - 10, -s // 4 + 11) if abs(s + 4 * v) < 26),
                  "non-tie box is {q : |s+4q| < 26}")
            check(len(q) == 13, "non-tie box has 13 elements")
            for w in (-3, -1, 1, 2, 5):
                check(box(s + 56 * w) == tuple(v - 14 * w for v in q), "non-tie box shifts by 14w")
        else:
            x = (s - 2) // 4
            check(tuple(v + x for v in q) == tuple(tie_range(x)), "tie box by class of x")


# ---------------------------------------------------------------- per-coordinate chains

@lru_cache(maxsize=None)
def chains_direct(s, bits):
    """Z_s(b) = sum over one coordinate's chains of prod_j (-1)^(b_j q_j), b_1 = stage t."""
    if not bits:
        return 1
    b = bits[0]
    return sum((-1 if b and q % 2 else 1) * chains_direct(s + 56 * q, bits[1:]) for q in box(s))


def transfer(par):
    """Transfer matrices on {x in SMALL of parity par} + {U, L}; signs (-1)^(b r)."""
    states = [x for x in SMALL if x % 2 == par] + ["U", "L"]
    idx = {s: i for i, s in enumerate(states)}
    rep = {"U": 100 + par, "L": -100 + par}  # any |x| >= 8 outside SMALL behaves alike
    cls = lambda y: y if y in SMALL else ("U" if y > 0 else "L")
    n = len(states)
    T = {b: [[0] * n for _ in range(n)] for b in (0, 1)}
    for s in states:
        x = rep.get(s, s)
        for r in tie_range(x):
            y = -13 * x + 14 * r
            if s in ("U", "L"):
                check(abs(y) >= 20 and (y > 0) == (s == "L"), "big states alternate U <-> L")
            for b in (0, 1):
                T[b][idx[s]][idx[cls(y)]] += -1 if b and r % 2 else 1
    for x in range(-60, 61):  # closure: outside SMALL never re-enters SMALL
        if x not in SMALL:
            check(all(-13 * x + 14 * r not in SMALL for r in tie_range(x)), "SMALL is the reach set")
    return states, idx, T


def apply(T, b, v):
    nm = 13 if b == 0 else 1
    return [Fraction(sum(a * x for a, x in zip(row, v)), nm) for row in T[b]]


def predicted(s, bits, cache):
    """Z_s(b) from the transfer matrices (tie s) or the product formula (others)."""
    zeros = bits.count(0)
    if s % 4 != 2:
        sign = 1
        for j, b in enumerate(bits):  # majority parity of every 13-box is that of Q(s)'s lowest point
            if b and box(s)[0] % 2:
                sign = -sign
        return sign * 13 ** zeros
    x = (s - 2) // 4
    par = x % 2
    states, idx, T = cache[par]
    v = [Fraction(1)] * len(states)
    for b in reversed(bits):
        v = apply(T, b, v)
    key = x if x in SMALL else ("U" if x > 0 else "L")
    return (-1) ** (x * sum(bits) % 2) * v[idx[key]] * 13 ** zeros


def check_transfer(cache):
    for L in range(1, 5):
        for s in range(-150, 151):
            for bits in itertools.product((0, 1), repeat=L):
                check(chains_direct(s, bits) == predicted(s, bits, cache), "transfer = direct chains")


def interval_step(D, T, n):
    nS = n - 2
    out = {}
    for (u, l), iv in D.items():
        for b in (0, 1):
            nm = 13 if b == 0 else 1
            key = (Fraction(T[b][n - 2][n - 2] * u + T[b][n - 2][n - 1] * l, nm),
                   Fraction(T[b][n - 1][n - 2] * u + T[b][n - 1][n - 1] * l, nm))
            check(abs(key[0]) == 1 and abs(key[1]) == 1, "big states keep |value| = 1")
            new = []
            for i in range(nS):
                check(sum(1 for j in range(nS) if T[b][i][j]) <= 1, "one small successor")
                lo = hi = Fraction(T[b][i][n - 2] * u + T[b][i][n - 1] * l)
                for j in range(nS):
                    a = T[b][i][j]
                    lo, hi = (lo + a * iv[j][0], hi + a * iv[j][1]) if a > 0 else \
                             (lo + a * iv[j][1], hi + a * iv[j][0]) if a < 0 else (lo, hi)
                new.append((lo / nm, hi / nm))
            out[key] = [(min(p[0], q[0]), max(p[1], q[1])) for p, q in zip(out[key], new)] \
                if key in out else new
    return out


def ratio_bounds(cache):
    """Lemma 2: an exactly closed interval family on the 1/12 grid."""
    caps = {}
    for par in (0, 1):
        states, idx, T = cache[par]
        n = len(states)
        start = {(Fraction(1), Fraction(1)): [(Fraction(1), Fraction(1))] * (n - 2)}
        D = start
        for _ in range(40):
            D = interval_step(D, T, n)
        grid = {k: [(Fraction(math.floor(lo * 12), 12), Fraction(math.ceil(hi * 12), 12))
                    for lo, hi in iv] for k, iv in D.items()}
        for k, iv in start.items():
            check(all(g[0] <= a[0] and a[1] <= g[1] for g, a in zip(grid[k], iv)), "start inside")
        img = interval_step(grid, T, n)
        check(set(img) <= set(grid), "keys closed")
        check(all(grid[k][i][0] <= img[k][i][0] and img[k][i][1] <= grid[k][i][1]
                  for k in img for i in range(n - 2)), "interval family closed under T_0/13, T_1")
        for i, s in enumerate(states[:-2]):
            caps[s] = max(max(abs(a), abs(b)) for iv in grid.values() for a, b in [iv[i]])
    check(max(caps.values()) == C_MAX, "sup ratio bound 23/12")
    one = [x for x, c in caps.items() if c <= 1]
    check(sorted(one) == [-8, -7, 6, 7], "ratio <= 1 exactly at the boundary states")
    check(all(-7 <= x <= 6 for x, c in caps.items() if c > 1), "ratio > 1 only in the 12-box class")
    # tightness: depth 27 already exceeds 1.9166
    par, x = 0, -6
    states, idx, T = cache[par]
    D = {(Fraction(1), Fraction(1)): [(Fraction(1), Fraction(1))] * (len(states) - 2)}
    for _ in range(27):
        D = interval_step(D, T, len(states))
    sup27 = max(max(abs(a), abs(b)) for iv in D.values() for a, b in [iv[idx[x]]])
    check(Fraction(19166, 10000) < sup27 <= C_MAX, "bound is essentially attained at depth 27")
    return caps, sup27


def check_counts(cache):
    """Lemma 3: row sums of T_0 are <= 13, and = 12 on the 12-box class."""
    for par in (0, 1):
        states, idx, T = cache[par]
        for i, s in enumerate(states):
            tot = sum(T[0][i])
            x = s if s in SMALL else None
            check(tot == (12 if x is not None and -7 <= x <= 6 else 13), "box sizes")


# ---------------------------------------------------------------- Poisson identity on a toy

def toy_poisson(code):
    """t = 2: sum over a coset of H of prod_k c_k equals the character formula."""
    rng = random.Random(6660)
    rep = lambda u: min(u ^ c for c in code)
    reps = sorted({rep(u) for u in range(256)})
    for trial in range(6):
        t = 2
        ss = [rng.choice([0, -22, -18, 30, 7, 13, 2, -26]) for _ in range(MODES)]
        # per-coordinate parity-string counts
        cnt = []
        for s in ss:
            c = [0] * 4
            for q2 in box(s):
                for q1 in box(s + 56 * q2):
                    c[(q2 & 1) | (q1 & 1) << 1] += 1
            cnt.append(c)
        gens = [tuple(rng.choice(reps) for _ in range(t)) for _ in range(rng.randint(1, 3))]
        Dset = {tuple([0] * t)}
        for g in gens:
            Dset |= {tuple(rep(a ^ b) for a, b in zip(d, g)) for d in Dset}
        vstar = tuple(rng.randrange(256) for _ in range(t))
        lhs = 0
        for v in itertools.product(range(256), repeat=t):
            if tuple(rep(a ^ b) for a, b in zip(v, vstar)) in Dset:
                p = 1
                for k in range(MODES):
                    p *= cnt[k][(v[0] >> k & 1) | (v[1] >> k & 1) << 1]
                lhs += p
        Hperp = [h for h in itertools.product(code, repeat=t)
                 if all(sum(wt(hj & dj) for hj, dj in zip(h, d)) % 2 == 0 for d in Dset)]
        rhs = Fraction(0)
        for h in Hperp:
            term = (-1) ** (sum(wt(hj & vj) for hj, vj in zip(h, vstar)) % 2)
            for k in range(MODES):
                bits = tuple(h[j] >> k & 1 for j in range(t))  # bits[0] = stage t = v[0]
                term *= sum(cnt[k][a] * (-1) ** sum(bits[j] * (a >> j & 1) for j in range(t))
                            for a in range(4))
            rhs += term
        dimD = len(Dset).bit_length() - 1
        rhs *= Fraction(2 ** dimD, 2 ** (4 * t))
        check(lhs == rhs, "Poisson form of the fiber")
        check(len(Hperp) == 2 ** (4 * t - dimD), "|H^perp| = 2^(4t - dim D)")


# ---------------------------------------------------------------- main

def main():
    rows = load_rows()
    code = code_from_rows(rows)
    rho2 = coset_sums(code)
    check_boxes()
    cache = {par: transfer(par) for par in (0, 1)}
    check_transfer(cache)
    check_counts(cache)
    caps, sup27 = ratio_bounds(cache)
    toy_poisson(code)

    # control: the naive per-coordinate Fourier majorant fails at a tie
    z = chains_direct(-22, (1, 0, 1))
    check(abs(z) == 24 and 24 > 13, "control: |Z| exceeds 13^zeros at s = -22")

    # Theorem threshold
    eps_star = Fraction(1, 13) / (C_MAX ** 8 - 1)
    # Depth-27 corollary
    t, dimD = 27, 4
    V = (1 + 12 * rho2 ** 25 + 3 * rho2 ** 26) * F ** t
    eps0 = V * 2 ** (4 * t - dimD) / 13 ** (8 * t) - 1
    check(0 < eps0 < eps_star, "FRAMES27 zero fiber is within the threshold")
    check(eps0 * 75 < eps_star, "with a factor 75 to spare")
    bits = math.ceil(math.log2(V))
    check(2 ** (bits - 1) < V <= 2 ** bits and bits == 696, "696 tag bits")
    # control: a t = 26 direct sum is not covered (PR6660 handles it separately)
    eps26 = Fraction(F ** 26 * 2 ** (4 * 26), 13 ** (8 * 26)) - 1
    check(eps26 > eps_star, "control: direct sums at t=26 lie outside the threshold")

    result = {
        "per_coordinate_ratio_bound": str(C_MAX),
        "ratio_caps_by_tie_state": {str(k): str(v) for k, v in sorted(caps.items())},
        "sup_ratio_depth27_state_minus6": float(sup27),
        "threshold_eps_star": str(eps_star),
        "threshold_eps_star_float": float(eps_star),
        "t27_value_over_F27": float(V / F ** t),
        "t27_eps0_float": float(eps0),
        "t27_exact_optimum_tag_bits": bits,
        "t26_direct_sum_eps0_float": float(eps26),
    }
    text = json.dumps(result, indent=1) + "\n"
    if __debug__ and not RESULT.exists():
        RESULT.write_text(text)
    check(RESULT.read_text() == text, "RESULT.json matches recomputation")
    print("eps* = %.6e, eps0(t=27) = %.6e, sup ratio = 23/12, bits = %d" % (eps_star, eps0, bits))
    print("PASS_REFINED_RECOVERY_MAX_FIBER")


if __name__ == "__main__":
    main()
