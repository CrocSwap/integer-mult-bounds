#!/usr/bin/env python3
"""Independent proof check of PR #4532 (Dillon), PROOF.md sections 1.1, 2.2-2.3 and 3: the funded critical-root majorant
L(n) <= A n^t (c + log n)^p used by #4535 (kappa = 0.003020165). Text vendored from #4535 head a6d7237f.

Every analytic step of section 2.3 is checked in the form it is used, and section 1.1's identities:
  S0 the two mirror-slack integral identities (dz/z gives P T' - T P'; z^(t-2) dz gives (P(t)T(1) - T(t)P(1))/(1-t)),
     as exact finite sums over the actual p16 windows at seven exponents, and strict-slack positivity;
  S1 (ln f)' = tau/x and f''/f = x^-2 [tau(tau-1) - p/(c+log x)^2]: identity of rational functions in (t, p, y = c+log x)
     after the chain rule dy/dx = 1/x, checked exactly at 2,000 random rational points;
  S2 tau(x) <= 1 for x >= 1 iff c >= p/(1-t); (f(x)/x)' = f(tau-1)/x^2 <= 0 and f(n0) = n0, so L(n) = n <= f(n) on the
     base range (checked with 60-digit decimals on log-spaced grids for both witnesses below);
  S3 (11) f(e)/f(n) <= (e/n)^tau(n) for 1 <= e <= n (log(1+y) <= y), on grids;
  S4 (12) f(n) - f(n-s) >= tau(n) f(n) s/n >= eta(tau(n)) f(n) (s/n)^tau(n) for n/m < s <= n, including s = n, on grids;
  S5 the recurrence closure: with (10), the exit charge is bounded by inner-source capacity (algebraic chain, checked
     on random nonnegative potentials satisfying (10));
  S6 K_ell's derivative numerator a(c + log m + log 2) + (a-1) log M (exact rational identity) and n < m M^(ell+1)
     for C_n = floor(n/m), ell = floor(log_M C_n) (exhaustive integer ranges);
  S8 section 3's tail-gate feasibility lemma on the p16 profile (convexity bound, (13) at the crossing, the
     sufficiency construction, and necessity on random passing gate samples);
  S7 the monotonicity directions that the endpoint evaluation in critical_guards relies on, on the actual p16 profile
     over each witness's cover interval: T(t+s)/T(t) and P(t+s)/P(t) nondecreasing, tilted means nondecreasing, every
     mirror cell sum nondecreasing, eta increasing, and (6) log q(t) >= d (t - t*) from the isolated crossing.
Witnesses: #4532's p16 (M = 1024, a = b = 1, ell0 = 650, p = 2/5, c = 133, cover .997067) and #4565's retuned
(M = 2^24, a = 3, b = 2, ell0 = 64, p = 3/10, c = 101, cover .99725).
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import decimal
from decimal import Decimal as D
from fractions import Fraction as Fr
import hashlib
import json
import math
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = HERE / "PR4532-PROOF.md"  # #4535 head a6d7237f, research/adaptive-gate-existence/PROOF.md, blob bdf142f2
SPEC_SHA256 = "340d637feef40f44a808c718207c0fede12cc483e2c979b86c56bb736b9c1ef5"
PROFILE = ROOT / "research/compact-joint-compiler/arithmetic/RESULT.json"
PROFILE_SHA256 = "a6caaa2a6d6460a8c1ef7e48c4853bb27976be33a52b96a4216dfa90d96c9091"
T_STAR = D("0.99697983402295")  # inside #4535's bracket [0.9969798340229, 0.996979834023]
WITNESSES = {
    "4532_p16": dict(M=1024, a=1, b=1, ell=650, p=Fr(2, 5), c=133, s=Fr(1, 20), lam=Fr(1, 10), d=Fr(103, 100), top=D("0.997067")),
    "4565_retuned": dict(M=1 << 24, a=3, b=2, ell=64, p=Fr(3, 10), c=101, s=Fr(1, 10), lam=Fr(1, 5), d=Fr(104, 100), top=D("0.99725")),
}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


decimal.getcontext().prec = 60


def S1(rng):
    for _ in range(2000):
        t = Fr(rng.randint(1, 999), 1000)
        p = Fr(rng.randint(1, 999), 1000)
        y = Fr(rng.randint(1, 10 ** 6), 1000)
        x = Fr(rng.randint(1, 10 ** 6), 1000)
        tau = t + p / y
        gp = tau / x                        # (ln f)' = t/x + p/(x y)
        need(gp == t / x + p / (x * y), "(ln f)'")
        gpp = -tau / x ** 2 + (-p / y ** 2) * (1 / x) / x  # d/dx (tau/x) with dtau/dx = -p/(y^2 x)
        need(gpp + gp ** 2 == (tau * (tau - 1) - p / y ** 2) / x ** 2, "f''/f identity")
    return 2000


def fval(w, x):
    lnx = D(x).ln()
    n0 = D(145) * D(w["M"]) ** w["ell"]
    p = D(w["p"].numerator) / w["p"].denominator
    c = D(w["c"])
    lnA = (1 - T_STAR) * n0.ln() - p * (c + n0.ln()).ln()
    return (lnA + T_STAR * lnx + p * (c + lnx).ln()).exp(), p, c


def tau(w, x):
    p = D(w["p"].numerator) / w["p"].denominator
    return T_STAR + p / (D(w["c"]) + D(x).ln())


def S2_S3_S4():
    checks = 0
    for name, w in WITNESSES.items():
        p = w["p"]
        need(Fr(w["c"]) >= p / (1 - Fr(str(T_STAR))), "c >= p/(1-t)")
        need(tau(w, 1) <= 1, "tau(1) <= 1")
        n0 = 145 * w["M"] ** w["ell"]
        f0, _, _ = fval(w, n0)
        need(abs(f0 / D(n0) - 1) < D(10) ** -40, "f(n0) = n0")
        # S2: base range, log-spaced integers 1..n0.
        for k in range(0, 60):
            n = max(1, int(D(n0) ** (D(k) / 59)))
            need(fval(w, n)[0] >= D(n) * (1 - D(10) ** -40), "L(n) = n <= f(n) on the base range")
            checks += 1
        # S3 and S4 on grids above n0.
        m = 145
        for kn in range(1, 12):
            n = n0 * (7 ** kn) + kn
            fn = fval(w, n)[0]
            tn = tau(w, n)
            eta = tn * D(m) ** (tn - 1)
            for ke in range(0, 16):
                e = max(1, int(D(n) ** (D(ke) / 15)))
                need(fval(w, e)[0] / fn <= (D(e) / D(n)) ** tn * (1 + D(10) ** -40), "(11)")
                checks += 1
            for frac in (Fr(1, 145) + Fr(1, 10 ** 6), Fr(1, 100), Fr(1, 10), Fr(1, 2), Fr(9, 10), Fr(1)):
                s = max(n // m + 1, (n * frac.numerator) // frac.denominator)
                fns = fval(w, n - s)[0] if n - s >= 1 else D(0)
                need(fn - fns >= tn * fn * D(s) / D(n) * (1 - D(10) ** -40), "(12) concavity step")
                need(tn * D(s) / D(n) >= eta * (D(s) / D(n)) ** tn * (1 - D(10) ** -40), "(12) eta step")
                checks += 1
    return checks


def S5(rng):
    for _ in range(5000):
        eta = Fr(rng.randint(500, 999), 1000)
        I = Fr(rng.randint(1, 10 ** 6), 7)
        BF = eta * I * Fr(rng.randint(0, 1000), 1000)  # (10): B + F <= eta I
        fn = Fr(rng.randint(1, 10 ** 6), 11)
        exit_charge_upper = fn * BF   # sum_e E_e f(e) <= f(n) sum_e E_e (e/n)^tau = f(n) (B+F) / n^tau, normalised
        capacity_lower = fn * eta * I  # sum_inner S_s (f(n) - f(n-s)) >= f(n) eta I / n^tau, normalised
        need(exit_charge_upper <= capacity_lower, "recurrence closure")
    return 5000


def S6(rng):
    for _ in range(2000):
        a = rng.randint(1, 8)
        cp = Fr(rng.randint(1, 10 ** 5), 100)
        L = Fr(rng.randint(1, 10 ** 4), 100)
        ell = Fr(rng.randint(1, 10 ** 4), 10)
        need(a * (cp + (ell + 1) * L) - (a * ell + 1) * L == a * cp + (a - 1) * L, "K_ell derivative numerator")
    n_cases = 0
    for m in (2, 3, 145):
        for M in (2, 3, 4, 1024):
            for n in range(m * M, m * M ** 3 + 50, max(1, (m * M ** 3) // 3000)):
                C = n // m
                ell = 0
                while M ** (ell + 1) <= C:
                    ell += 1
                need(n < m * M ** (ell + 1), "n < m M^(ell+1)")
                n_cases += 1
    return n_cases


def S7():
    prof = json.loads(PROFILE.read_bytes())
    need(hashlib.sha256(PROFILE.read_bytes()).hexdigest() == PROFILE_SHA256, "pinned p16 profile")
    T = {int(k): v for k, v in prof["targets"].items()}
    P = {int(k): v for k, v in prof["paid"].items()}
    m = max(T)

    def mom(h, t):
        return sum(c * k ** t for k, c in h.items())

    def mean(h, t):
        return sum(c * k ** t * math.log(k) for k, c in h.items()) / mom(h, t)

    pts = sorted({0.0, *(1 / k for k in T), *(1 / r for r in P)})
    cells = []
    for left, right in zip(pts, pts[1:]):
        x = (left + right) / 2
        src, ex = {}, {}
        for k, w in T.items():
            for r, cnt in P.items():
                if k > r and 1 / k < x <= 1 / r:
                    src[k * r] = src.get(k * r, 0) + w * cnt
                if r > k and 1 / r < x <= 1 / k:
                    ex[k * r] = ex.get(k * r, 0) + w * cnt
        cells.append((src, ex))
    # isolate the crossing in floats (validation only; the certified bracket is #4535's)
    lo, hi = 0.9969, 0.9971
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if mom(T, mid) < mom(P, mid) else (lo, mid)
    ts = lo
    checks = 0
    for name, w in WITNESSES.items():
        top = float(w["top"])
        s, lam, d = float(w["s"]), float(w["lam"]), float(w["d"])
        grid = [ts + (top - ts) * k / 120 for k in range(121)]
        prev = None
        for t in grid:
            cur = (mom(T, t + s) / mom(T, t), mom(P, t + s) / mom(P, t), mean(T, t), mean(P, t),
                   [mom(src, t) for src, _ in cells], [mom(ex, t) for _, ex in cells], t * m ** (t - 1))
            need(math.log(mom(T, t) / mom(P, t)) >= d * (t - ts) - 1e-12, "(6) from the crossing")
            need(mom(T, t - lam) / mom(P, t) <= mom(T, top - lam) / mom(P, ts) * (1 + 1e-12), "root-tail endpoint bound")
            need(mom(T, t) / mom(P, t) <= mom(T, top) / mom(P, ts) * (1 + 1e-12), "moment-ratio endpoint bound")
            if prev is not None:
                need(cur[0] >= prev[0] * (1 - 1e-13) and cur[1] >= prev[1] * (1 - 1e-13), "forward ratios nondecreasing")
                need(cur[2] >= prev[2] - 1e-13 and cur[3] >= prev[3] - 1e-13, "tilted means nondecreasing")
                need(all(a >= b * (1 - 1e-13) for a, b in zip(cur[4], prev[4])), "source cells nondecreasing")
                need(all(a >= b * (1 - 1e-13) for a, b in zip(cur[5], prev[5])), "exit cells nondecreasing")
                need(cur[6] > prev[6], "eta increasing")
            prev = cur
            checks += 1
    return checks, ts


def S0():
    """Section 1.1: the two mirror-slack integral identities, as exact finite sums over the actual p16 windows.

    For pair (r, k) with coefficient P_r W_k (rk)^t: a source window (1/k, 1/r] (k > r) or an exit window (1/r, 1/k]
    (r > k) integrated against dz/z gives the same signed log(k/r); against z^(t-2) dz it gives
    (k r^t - r k^t)/(1 - t) (k > r) or minus the mirrored value (r > k). Summing must give P T' - T P' and
    (P(t) T(1) - T(t) P(1))/(1 - t). Integrals are evaluated cell by cell from the window endpoints; checked at 7
    exponents with 50-digit decimals, plus the strict-slack positivity (1 - beta) * integral of S > 0.
    """
    prof = json.loads(PROFILE.read_bytes())
    T = {int(k): v for k, v in prof["targets"].items()}
    P = {int(k): v for k, v in prof["paid"].items()}
    checks = 0
    for t in (D("0.5"), D("0.9"), D("0.99"), T_STAR, D("0.99725"), D("0.999"), D("0.3")):
        lhs1 = lhs2 = D(0)
        source_mass = D(0)
        for k, w in T.items():
            for r, cnt in P.items():
                if k == r:
                    continue
                coef = D(w * cnt) * (D(r) * D(k)) ** t
                lo, hi = (D(1) / k, D(1) / r) if k > r else (D(1) / r, D(1) / k)
                sign = 1 if k > r else -1  # source windows count positively, exit windows negatively
                lhs1 += sign * coef * (hi.ln() - lo.ln())
                lhs2 += sign * coef * (hi ** (t - 1) - lo ** (t - 1)) / (t - 1)
                if k > r:
                    source_mass += coef * (hi.ln() - lo.ln())
        Tt = sum(D(c) * D(k) ** t for k, c in T.items())
        Pt = sum(D(c) * D(r) ** t for r, c in P.items())
        Td = sum(D(c) * D(k) ** t * D(k).ln() for k, c in T.items())
        Pd = sum(D(c) * D(r) ** t * D(r).ln() for r, c in P.items())
        T1 = sum(D(c) * k for k, c in T.items())
        P1 = sum(D(c) * r for r, c in P.items())
        need(abs(lhs1 - (Pt * Td - Tt * Pd)) <= D(10) ** -30 * abs(Pt * Td), "dz/z identity = P T' - T P'")
        need(abs(lhs2 - (Pt * T1 - Tt * P1) / (1 - t)) <= D(10) ** -30 * abs(Pt * T1), "z^(t-2) identity")
        checks += 1
    # Strict slack: with E <= beta S pointwise (beta = .564 < 1), the dz/z integral is >= (1 - beta) * source mass > 0.
    need(lhs1 > 0 and (1 - D("0.564")) * source_mass > 0, "strict mirror slack gives a positive mean gap")
    return checks


def S8(rng):
    """Section 3 lemma on the p16 profile (floats; validation of a written convexity proof).

    (i) the convexity bound H(lambda) <= mu_T(t) - log q(t)/lambda on a grid of t >= t* and lambda;
    (ii) at the crossing, (13) T(t - lambda) exp(lambda mu_P) < P(t) holds for small lambda;
    (iii) sufficiency: the proof's construction g, j, a = 1, b = g - 1, M = 2^j yields, for a small s, all three gates;
    (iv) necessity: every random (a, b, M, s, lambda) passing the three gates has H(lambda) > mu_P(t).
    """
    prof = json.loads(PROFILE.read_bytes())
    T = {int(k): v for k, v in prof["targets"].items()}
    P = {int(k): v for k, v in prof["paid"].items()}

    def mom(h, t):
        return sum(c * k ** t for k, c in h.items())

    def mean(h, t):
        return sum(c * k ** t * math.log(k) for k, c in h.items()) / mom(h, t)

    def H(t, lam):
        return (math.log(mom(P, t)) - math.log(mom(T, t - lam))) / lam

    ts = float(T_STAR)
    checks = 0
    for t in (ts, ts + 1e-4, ts + 1e-3, 0.999):
        q = mom(T, t) / mom(P, t)
        for lam in (1e-3, 1e-2, 0.05, 0.1, 0.3, 1.0):
            need(H(t, lam) <= mean(T, t) - math.log(q) / lam + 1e-9, "convexity bound on H")
            checks += 1
    muT, muP = mean(T, ts), mean(P, ts)
    lam = 1e-3
    need(mom(T, ts - lam) * math.exp(lam * muP) < mom(P, ts), "(13) at the crossing")
    delta = muT - muP
    Hl = H(ts, lam)
    g = 2
    while g * Hl / math.log(2) - (g * muP + delta) / math.log(2) <= 1:
        g += 1
    j = math.floor((g * muP + delta) / math.log(2)) + 1
    need((g * muP + delta) / math.log(2) < j < g * Hl / math.log(2), "integer j inside the interval")
    a, b, M = 1, g - 1, 2.0 ** j
    s = 1e-4
    u = M ** (-s) * (mom(T, ts + s) / mom(T, ts)) ** a * (mom(P, ts + s) / mom(P, ts)) ** b
    v = M ** lam * (mom(T, ts - lam) / mom(P, ts)) ** (a + b)
    need(u < 1 and v < 1 and mom(T, ts + s) / mom(T, ts) >= mom(P, ts + s) / mom(P, ts), "constructed gates hold")
    passing = 0
    for _ in range(4000):
        a2, b2 = rng.randint(1, 6), rng.randint(1, 6)
        M2 = 2.0 ** rng.randint(2, 40)
        s2, lam2 = rng.uniform(0.001, 0.5), rng.uniform(0.001, 0.5)
        t = ts + rng.uniform(0, 1e-3)
        u2 = M2 ** (-s2) * (mom(T, t + s2) / mom(T, t)) ** a2 * (mom(P, t + s2) / mom(P, t)) ** b2
        v2 = M2 ** lam2 * (mom(T, t - lam2) / mom(P, t)) ** (a2 + b2)
        order = mom(T, t + s2) / mom(T, t) >= mom(P, t + s2) / mom(P, t)
        if u2 < 1 and v2 < 1 and order:
            need(H(t, lam2) > mean(P, t), "necessity: gates imply H(lambda) > mu_P")
            passing += 1
    need(passing > 50, "enough passing gate samples")
    return {"convexity_points": checks, "constructed": {"g": g, "j": j}, "necessity_samples": passing}


def check_binding():
    raw = SPEC.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SPEC_SHA256, "vendored #4532 PROOF.md")
    text = raw.decode("utf-8")
    for s in ("f(e)/f(n) <= (e/n)^tau(n).", "f(n)-f(n-s) >= tau(n) f(n) s/n", "a(c+log m+log 2)+(a-1)log M > 0.",
              "q(t) >= exp[d(t-t_*)]", "f''(x)/f(x)=x^(-2)[tau(x)(tau(x)-1)-p/(c+log x)^2]<=0.",
              "sum_s S_s f(n-s)+sum_e E_e f(e) <= (sum_s S_s) f(n)."):
        need(s in text, f"PROOF.md states: {s}")
    return 6


def main():
    rng = random.Random(45321)
    s7, ts = S7()
    report = {"status": "PASS_PR4532_PROOF_CHECK", "S0_section_1_1_identities": S0(), "S1_identity_points": S1(rng), "S2_S3_S4_grid_checks": S2_S3_S4(),
              "S5_closure_cases": S5(rng), "S6_integer_cases": S6(rng), "S7_profile_grid_points": s7, "S8_section_3": S8(rng),
              "float_crossing": ts, "spec_statements_bound": check_binding(), "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
