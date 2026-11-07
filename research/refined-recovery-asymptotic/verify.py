"""Exact checks for the asymptotically exact refined-recovery optimum (stdlib only).

Prints PASS_REFINED_RECOVERY_ASYMPTOTIC on success.
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
EXACT_LIMIT = 1500


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


CYCLE = 26          # #6660 direct-sum frames
DIGITS = 700        # working precision for the continued fraction of 8 log2 13
Q_EXP = 200         # claim: exact tag bits for every 27 <= t < 10^Q_EXP


def eps_terms(H, r, stages):
    """eps0 * 13^(8t) / 2^(r - rank)-normalized: sum over chi outside span^perp of 13^(-wt)."""
    out = Fraction(0)
    for chi in range(1, 2 ** r):
        hs = []
        for j in stages:
            h = 0
            for i in range(r):
                if chi >> i & 1:
                    h ^= H[j][i]
            hs.append(h)
        if any(hs):
            out += Fraction(1, 13 ** sum(wt(h) for h in hs))
    return out


def toy_cycle(code, reps):
    """Appending a direct-sum cycle spanning V multiplies eps0 by at most 13^-4."""
    rng = random.Random(26)
    r = 8
    for trial in range(8):
        while True:  # two stages whose images form a direct sum = V
            cyc = [[rng.choice(code) for _ in range(r)] for _ in range(2)]
            phi = lambda Hj, u: sum((wt(Hj[i] & u) & 1) << i for i in range(r))
            if rank2([phi(Hj, a) for Hj in cyc for a in reps]) == r:
                break
        pre = [[rng.choice(code) for _ in range(r)] for _ in range(rng.randint(1, 3))]
        if rank2([phi(Hj, a) for Hj in pre for a in reps]) == 0:
            continue
        H = pre + cyc + cyc
        e0 = eps_terms(H, r, range(len(pre)))
        e1 = eps_terms(H, r, range(len(pre) + 2))
        e2 = eps_terms(H, r, range(len(pre) + 4))
        # restricted to the full span V (rank r), eps0 counts every chi != 0
        full0 = sum(Fraction(1, 13 ** sum(wt(sum_h(H, j, chi, r)) for j in range(len(pre))))
                    for chi in range(1, 2 ** r))
        check(e1 <= full0 / 13 ** 4 and e2 <= full0 / 13 ** 8, "one cycle gains a factor 13^-4")
        check(e2 <= e1 <= full0, "monotone")


def sum_h(H, j, chi, r):
    h = 0
    for i in range(r):
        if chi >> i & 1:
            h ^= H[j][i]
    return h


def bits(x):
    """ceil(log2 x) for a positive Fraction."""
    k = x.numerator.bit_length() - x.denominator.bit_length() + 1
    while Fraction(2) ** k < x:
        k += 1
    while Fraction(2) ** (k - 1) >= x:
        k -= 1
    return k


def window(theta, t):
    """Upper bound on eps0(t) for FRAMES27 followed by #6660 cycles."""
    return theta / Fraction(13) ** (4 * ((t - 27) // CYCLE))


def main():
    rows = load_rows()
    code = code_from_rows(rows)
    reps, S = coset_data(code)
    toy_cycle(code, reps)
    rho2 = Fraction(50979600, F)
    V27 = (1 + 12 * rho2 ** 25 + 3 * rho2 ** 26) * F ** 27
    theta = V27 * 2 ** CAP / 13 ** 216 - 1
    check(0 < theta < EPS_STAR / 75, "theta below the #6848 threshold")

    # Part 1: exact big-integer determination of the tag for 27 <= t <= EXACT_LIMIT
    table = []
    for t in range(27, EXACT_LIMIT + 1):
        lo = Fraction(13 ** (8 * t), 2 ** CAP)
        b = bits(lo)
        check(bits(lo * (1 + window(theta, t))) == b, "tag determined at t=%d" % t)
        if t <= 30 or t in (40, 53, 79, 100, 584977) or t % 500 == 0:
            table.append({"t": t, "opt_bits": b,
                          "eps0_bound_log10": round(math.log10(window(theta, t)), 2)})

    # Part 2: continued fraction of alpha = 8 log2 13, best-approximation bound
    getcontext().prec = DIGITS
    alpha = 8 * (Decimal(13).ln() / Decimal(2).ln())
    x, cf = alpha, []
    p0, q0, p1, q1 = 0, 1, 1, 0
    qs = []
    while q1 <= 10 ** (Q_EXP + 5):
        a = int(x)
        cf.append(a)
        p0, q0, p1, q1 = p1, q1, a * p1 + p0, a * q1 + q0
        qs.append(q1)
        x = 1 / (x - a)
    check(cf[:6] == [29, 1, 1, 1, 1, 10], "continued fraction start")
    n = next(i for i in range(len(qs) - 1) if qs[i + 1] >= 10 ** Q_EXP)
    qn, qn1 = qs[n], qs[n + 1]
    dist = abs(qn * alpha - (qn * alpha).to_integral_value())
    check(Decimal(qn1) * Decimal(10) ** (6 - DIGITS) * 10 ** 6 < dist, "precision margin")
    # for 0 < t < q_(n+1): ||t alpha|| >= ||q_n alpha|| = dist (best approximation)
    # for t > EXACT_LIMIT: window <= log2(1 + w) <= 2 w <= 2 theta 13^(-4 m) < dist
    w = window(theta, EXACT_LIMIT + 1)
    check(Decimal(2 * w.numerator) / Decimal(w.denominator) < dist, "window below ||q_n alpha||")
    check(qn1 >= 10 ** Q_EXP, "covers every t < 10^200")

    # Part 3: t >= 10^200 by Laurent-Mignotte-Nesterenko (1995), Corollary 2:
    # log|b2 log 13 - b1 log 2| >= -24.34 (max(log b' + 0.14, 21, 1/2))^2 log A1 log A2,
    # D = 1, log A1 = 1, log A2 = log 13, b' = b1/log A2 + b2/log A1 <= 20 t here.
    # Both sides are monotone in t, so it suffices to compare at t0 = 10^200, in natural logs:
    # log window <= log(2 theta) - 4 log(13) ((t-27)//26), linear in t;
    # log ||t alpha|| >= LMN bound - log log 2, polylogarithmic in t.
    t0 = 10 ** Q_EXP
    log_window = math.log(2 * float(theta)) - 4 * math.log(13) * ((t0 - 27) // CYCLE)
    logb = math.log(20) + Q_EXP * math.log(10)
    lmn = -24.34 * max(logb + 0.14, 21.0, 0.5) ** 2 * 1.0 * math.log(13) - math.log(math.log(2))
    check(log_window < -1e199 and lmn > -2e7, "LMN margin at 10^200")
    check(log_window < 10 ** 6 * lmn, "window far below the LMN bound (factor 10^6 in the exponent)")

    result = {
        "theta_t27_float": float(theta),
        "cycle_length": CYCLE,
        "exact_limit": EXACT_LIMIT,
        "best_approx_index": n,
        "q_n_digits": len(str(qn)),
        "q_n_plus_1_digits": len(str(qn1)),
        "norm_q_n_alpha_log10": int(dist.adjusted()),
        "window_after_exact_limit_log10": round(math.log10(w), 1),
        "lmn_log_lower_bound_at_1e200": round(lmn, 1),
        "continued_fraction_first_30": cf[:30],
        "table": table,
    }
    text = json.dumps(result, indent=1) + "\n"
    if __debug__ and not RESULT.exists():
        RESULT.write_text(text)
    check(RESULT.read_text() == text, "RESULT.json matches recomputation")
    print("exact tags for all t >= 27 (cf < 10^%d, LMN above); ||q_n alpha|| ~ 1e%d; window after t=%d ~ 1e%.0f"
          % (Q_EXP, dist.adjusted(), EXACT_LIMIT, math.log10(w)))
    print("PASS_REFINED_RECOVERY_ASYMPTOTIC")


if __name__ == "__main__":
    main()
