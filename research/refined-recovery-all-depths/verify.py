"""Exact checks for the optimal refined-recovery fiber at every depth t >= 27 (stdlib only).

Prints PASS_REFINED_RECOVERY_ALL_DEPTHS on success.
"""
import hashlib
import itertools
import json
import math
import pathlib
import random
from decimal import Decimal, getcontext
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
FIXTURE = HERE.parent / "precision-state-frontier" / "FIXTURE.json"
FIXTURE_SHA = "2ca4d7550fcae5b757ec500f87aee1d2ef9f64b59e4abe2bda93319521304af8"
RESULT = HERE / "RESULT.json"
N, MODES = 112, 8
F = (13**8 + 14 * 13**4 + 1) // 16
CAP = 104                                        # #6660 Theorem (c)
EPS_STAR = Fraction(1, 13) / (Fraction(23, 12) ** 8 - 1)  # #6848 threshold
EXACT_TABLE = range(27, 401)
SCAN_LIMIT = 600000


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


def toy_checks(code, reps, S):
    """Section 1 on random small instances: coset form = character form, the main-term
    lower bound, and monotonicity of eps0 under appending a stage inside the span."""
    rng = random.Random(27)
    for trial in range(12):
        t = rng.choice((2, 3))
        r = rng.randint(3, 9)
        # phi_j(u)_i = h_{j,i} . u with h_{j,i} in C = C^perp (so phi_j kills C)
        H = [[rng.choice(code) for _ in range(r)] for _ in range(t)]
        phi = lambda j, u: sum((wt(H[j][i] & u) & 1) << i for i in range(r))
        lhs = 0
        for a in itertools.product(reps, repeat=t):
            acc = 0
            for j in range(t):
                acc ^= phi(j, a[j])
            if acc == 0:
                p = 1
                for j in range(t):
                    p *= S[a[j]]
                lhs += p
        def hj(j, chi):
            h = 0
            for i in range(r):
                if chi >> i & 1:
                    h ^= H[j][i]
            return h
        def terms(tt):
            return [math.prod(13 ** (8 - wt(hj(j, chi))) for j in range(tt)) for chi in range(2 ** r)]
        rhs = Fraction(sum(terms(t)), 2 ** r)
        check(lhs == rhs, "zero fiber = 2^-r sum_chi prod_j 13^(8-wt h_j)")
        images = [phi(j, a) for j in range(t) for a in reps]
        rk = rank2(images)
        main = Fraction(13 ** (8 * t), 2 ** rk)
        check(lhs >= main, "zero fiber >= 13^(8t) / 2^rank")
        # appending a stage that repeats stage 0 keeps the rank and the main term
        H.append(list(H[0]))
        lhs2 = Fraction(sum(terms(t + 1)), 2 ** r)
        eps = lhs / main - 1
        eps2 = lhs2 / Fraction(13 ** (8 * (t + 1)), 2 ** rk) - 1
        check(0 <= eps2 <= eps, "eps0 is non-increasing when a stage is appended")
        H.pop()


def bits(x):
    """ceil(log2 x) for a positive Fraction."""
    k = x.numerator.bit_length() - x.denominator.bit_length() + 1
    while Fraction(2) ** k < x:
        k += 1
    while Fraction(2) ** (k - 1) >= x:
        k -= 1
    return k


def main():
    rows = load_rows()
    code = code_from_rows(rows)
    reps, S = coset_data(code)
    toy_checks(code, reps, S)
    rho2 = Fraction(50979600, F)

    # depth 27: #6828 exact minimum, FRAMES27 has dim D = 4 (rank 104)
    V27 = (1 + 12 * rho2 ** 25 + 3 * rho2 ** 26) * F ** 27
    theta = V27 * 2 ** CAP / 13 ** 216 - 1
    check(0 < theta < EPS_STAR, "FRAMES27 eps0 below the #6848 threshold")
    check(theta < Fraction(546, 10 ** 8), "theta < 5.46e-6")

    # exact table: lower main term and upper main term * (1 + theta)
    table = []
    for t in EXACT_TABLE:
        lo = Fraction(13 ** (8 * t), 2 ** CAP)
        hi = lo * (1 + theta)
        b = bits(lo)
        check(bits(hi) == b, "tag bits determined at t=%d" % t)
        check(b == math.ceil(8 * t * math.log2(13) - CAP - 1e-9), "closed form")
        A = Fraction(13 ** (8 * t) + 14 * 13 ** (4 * t) + 1, 16)
        ident = bits(A)
        table.append({"t": t, "opt_bits": b, "identity_bits": ident, "saving": ident - b})
    check(table[0]["opt_bits"] == 696 and table[1]["opt_bits"] == 725, "t=27,28 bits")
    check({row["saving"] for row in table} == {100}, "exactly 100 bits saved vs identity frames")
    # main term beats the #6828 AM-GM floor from t = 28 on (that floor at t = 28 is < 252.51123)
    check(Fraction(13 ** 224, 2 ** CAP) / F ** 28 > Fraction(25251123, 10 ** 5), "beats d=8 floor at t=28")
    # at t = 27 the exact value is above the main term by theta
    check(V27 > Fraction(13 ** 216, 2 ** CAP), "t=27 exact value above main term")

    # scan for depths where the window (1+theta) could straddle a power of two
    getcontext().prec = 60
    alpha = 8 * (Decimal(13).ln() / Decimal(2).ln())
    width = Decimal(math.log2(1 + float(theta))) * Decimal("1.000001")
    first = None
    for t in range(27, SCAN_LIMIT):
        f = (alpha * t) % 1
        if f > 1 - width:
            first = t
            break
    check(first == 584977, "first ambiguous depth")
    for t in (584977,):  # confirm with exact-enough decimal margin
        f = (alpha * t) % 1
        check(Decimal("7.8e-6") < 1 - f < Decimal("7.9e-6"), "ambiguous depth margin")

    result = {
        "theta_t27_float": float(theta),
        "eps_star_float": float(EPS_STAR),
        "first_possibly_ambiguous_depth": first,
        "table": [row for row in table if row["t"] <= 40 or row["t"] % 50 == 0],
    }
    text = json.dumps(result, indent=1) + "\n"
    if __debug__ and not RESULT.exists():
        RESULT.write_text(text)
    check(RESULT.read_text() == text, "RESULT.json matches recomputation")
    print("theta = %.6e; bits t=27..30: %s; first ambiguous depth %d"
          % (theta, [r["opt_bits"] for r in table[:4]], first))
    print("PASS_REFINED_RECOVERY_ALL_DEPTHS")


if __name__ == "__main__":
    main()
