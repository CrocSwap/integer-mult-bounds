"""Exact checks for the rate of the second-order term of the refined-recovery optimum.

Prints PASS_REFINED_RECOVERY_EPS_RATE on success (stdlib only).
"""
import hashlib
import itertools
import json
import math
import pathlib
import random
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
FIXTURE = HERE.parent / "precision-state-frontier" / "FIXTURE.json"
FIXTURE_SHA = "2ca4d7550fcae5b757ec500f87aee1d2ef9f64b59e4abe2bda93319521304af8"
RESULT = HERE / "RESULT.json"
N, MODES = 112, 8
F = (13**8 + 14 * 13**4 + 1) // 16
CAP = 104                                        # #6660 Theorem (c)
EPS_STAR = Fraction(1, 13) / (Fraction(23, 12) ** 8 - 1)  # #6848 threshold


def fail(msg):
    raise SystemExit("FAIL: " + msg)


def check(cond, msg):
    if not cond:
        fail(msg)


def wt(u):
    return bin(u).count("1")


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


def weight(u):
    return 7 ** (8 - wt(u)) * 6 ** wt(u)


def coset_data(code):
    rep = lambda u: min(u ^ c for c in code)
    reps = sorted({rep(u) for u in range(256)})
    S = {a: sum(weight(a ^ c) for c in code) for a in reps}
    check(S[0] == F, "S(C) = F")
    check({S[a] for a in reps if wt(a) % 2} == {50983170}, "odd coset sum")
    check({S[a] for a in reps if a and wt(a) % 2 == 0} == {50979600}, "even coset sum")
    for h in code:  # Fourier transform of the [-6,6] box weight
        check(sum(weight(u) * (-1) ** wt(h & u) for u in range(256)) == 13 ** (8 - wt(h)),
              "hat w(h) = 13^(8 - wt h)")
    return reps, S


def rank2(vecs):
    basis = []
    for v in vecs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


EIDX = (0, 1, 2, 4)  # rows of E, as in PR6327 / PR6660
RPRIME_DIM = 100


def kernel_mod2_rank(rows):
    """Integer kernel of M^T restricted to rows outside E; ranks of its mod-2 reduction
    alone and together with the columns of M mod 2."""
    free = [i for i in range(N) if i not in EIDX]
    A = [[rows[i][k] for i in free] for k in range(MODES)]
    n = len(free)
    U = [[int(i == j) for j in range(n)] for i in range(n)]

    def colop(c1, c2, f):
        for r in A:
            r[c1] -= f * r[c2]
        for r in U:
            r[c1] -= f * r[c2]

    def swap(c1, c2):
        for r in A + U:
            r[c1], r[c2] = r[c2], r[c1]

    piv = 0
    for k in range(MODES):
        while True:
            nz = [c for c in range(piv, n) if A[k][c] != 0]
            if len(nz) <= 1:
                break
            c0 = min(nz, key=lambda c: abs(A[k][c]))
            for c in nz:
                if c != c0:
                    colop(c, c0, A[k][c] // A[k][c0])
        nz = [c for c in range(piv, n) if A[k][c] != 0]
        if nz:
            swap(piv, nz[0])
            piv += 1
    check(piv == MODES, "M^T has rank 8 on the free rows")
    kern = []
    for c in range(MODES, n):
        v = [0] * N
        for i, x in zip(free, (U[r][c] for r in range(n))):
            v[i] = x
        check(all(sum(rows[i][k] * v[i] for i in range(N)) == 0 for k in range(MODES)), "M^T v = 0")
        check(all(v[i] == 0 for i in EIDX), "E v = 0")
        kern.append(sum((v[i] & 1) << i for i in range(N)))
    mcols = [sum((rows[i][k] & 1) << i for i in range(N)) for k in range(MODES)]
    return rank2(kern), rank2(kern + mcols), rank2(mcols)


def eta_rows(rows):
    """eta(u)_b = <row E_b, u> mod 2, as 8-bit masks of the E rows."""
    return [sum((rows[i][k] & 1) << k for k in range(MODES)) for i in EIDX]


def h_of(func, er):
    """The element h in C with h.u = func . eta(u) (func a 4-bit functional)."""
    h = 0
    for b in range(4):
        if func >> b & 1:
            h ^= er[b]
    return h


def toy_first_moment(code, er):
    """Exact average of S over all psi (psi_1 = 0) for small R' (dim r'), t stages."""
    for rp, t in ((1, 2), (1, 3), (2, 2), (1, 4)):
        maps = list(itertools.product(range(2 ** rp), repeat=4))  # images of eta-basis
        total, count = Fraction(0), 0
        for psis in itertools.product(maps, repeat=t - 1):
            psis = ((0, 0, 0, 0),) + psis
            S = Fraction(0)
            for chi1 in range(16):
                for chi2 in range(2 ** rp):
                    if chi1 == 0 and chi2 == 0:
                        continue
                    w = 0
                    for psi in psis:
                        f = chi1
                        for b in range(4):  # functional chi2 o psi on eta-basis
                            if wt(chi2 & psi[b]) & 1:
                                f ^= 1 << b
                        h = h_of(f, er)
                        check(h in code, "chi o phi_j is a word of C")
                        w += wt(h)
                    S += Fraction(1, 13 ** w)
            total += S
            count += 1
        avg = total / count
        q = Fraction(16 * F, 13 ** 8) / 16
        formula = (2 ** (4 + rp) - 16) * q ** t + 14 * Fraction(1, 13 ** (4 * t)) \
            + Fraction(1, 13 ** (8 * t))
        check(avg == formula, "first moment formula (r'=%d, t=%d)" % (rp, t))


def toy_jensen(code, er):
    """Sum over chi of total weight is 4 t 2^r for injective stage maps (toy r = 6)."""
    rng = random.Random(29)
    for trial in range(10):
        t, rp = rng.randint(2, 4), 2
        psis = [(0, 0, 0, 0)] + [tuple(rng.randrange(4) for _ in range(4)) for _ in range(t - 1)]
        tot, S = 0, Fraction(0)
        for chi in range(1, 2 ** (4 + rp)):
            chi1, chi2 = chi & 15, chi >> 4
            w = 0
            for psi in psis:
                f = chi1
                for b in range(4):
                    if wt(chi2 & psi[b]) & 1:
                        f ^= 1 << b
                w += wt(h_of(f, er))
            tot += w
            S += Fraction(1, 13 ** w)
        R = 2 ** (4 + rp)
        check(tot == 4 * t * R, "sum of weights = 4 t 2^r")
        check(S >= (R - 1) * 13.0 ** (-4 * t * R / (R - 1)) * (1 - 1e-12), "Jensen lower bound")


def E_t(t):
    q = Fraction(16 * F, 13 ** 8) / 16
    return (2 ** CAP - 16) * q ** t + 14 * Fraction(1, 13 ** (4 * t)) + Fraction(1, 13 ** (8 * t))


def log2_frac(x):
    return math.log2(x.numerator) - math.log2(x.denominator)


def main():
    rows = load_rows()
    code = code_from_rows(rows)
    reps, S = coset_data(code)
    r_k, r_all, r_m = kernel_mod2_rank(rows)
    check((r_k, r_all, r_m) == (RPRIME_DIM, CAP, 4), "R' has dim 100 and V = im mu + R' has dim 104")
    er = eta_rows(rows)
    check(sorted({h_of(f, er) for f in range(16)}) == sorted(code), "eta^T maps F2^4 onto C")
    toy_first_moment(code, er)
    toy_jensen(code, er)

    check(E_t(28) > EPS_STAR, "control: first moment does not reach the threshold at t = 28")
    table = []
    for t in range(29, 61):
        e = E_t(t)
        check(e < EPS_STAR, "E_t below the #6848 threshold at t=%d" % t)
        lo_log2 = math.log2(2 ** CAP - 1) - 4 * t * (2 ** CAP / (2 ** CAP - 1)) * math.log2(13)
        table.append({"t": t, "log2_upper_eps": round(log2_frac(e), 3), "log2_lower_eps": round(lo_log2, 3)})
    rate_up = 4 - math.log2(16 * F / 13 ** 8)
    rate_lo = 4 * math.log2(13)
    check(abs((table[-1]["log2_upper_eps"] - table[-2]["log2_upper_eps"]) + rate_up) < 1e-3, "upper rate")
    result = {
        "E_t_formula": "(2^104-16)((16F/13^8)/16)^t + 14*13^(-4t) + 13^(-8t)",
        "E_28_over_eps_star": float(E_t(28) / EPS_STAR),
        "E_29_float": float(E_t(29)),
        "rate_bits_per_stage_upper_bound_side": round(rate_up, 6),
        "rate_bits_per_stage_lower_bound_side": round(rate_lo, 6),
        "table": [row for row in table if row["t"] <= 32 or row["t"] % 10 == 0],
    }
    text = json.dumps(result, indent=1) + "\n"
    if __debug__ and not RESULT.exists():
        RESULT.write_text(text)
    check(RESULT.read_text() == text, "RESULT.json matches recomputation")
    print("E_29 = %.4e < eps*; decay rates %.4f (upper) and %.4f (lower) bits per stage"
          % (float(E_t(29)), rate_up, rate_lo))
    print("PASS_REFINED_RECOVERY_EPS_RATE")


if __name__ == "__main__":
    main()
