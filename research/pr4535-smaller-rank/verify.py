#!/usr/bin/env python3
"""A smaller certified finite rank for PR #4535's critical-root compiler, at the same kappa and parameters.

#4535 (head a6d7237f, vendored RESULT.json, sha256-pinned) freezes its finite compiler word at N = 2^(10^12) and
certifies L(N) < N^z from the funded majorant L(n) <= A n^theta (c + ln n)^p, with p = 2/5, c = 133,
n0 = 145*1024^650, A <= n0^(1-theta_lo), the critical-root bracket [theta_lo, theta_hi] and z = 1 - s_C,
z - theta_hi = 377/10^12. Absorption needs only

    ln A + p ln(c + ln N) < (z - theta_hi) ln N,

whose left side grows like ln ln N. #4535 bounds ln A by (1 - theta_lo) ln n0; its own definition
A = n0^(1-theta)/(c + ln n0)^p gives a sharper certified bound, and both are used. This verifier, with its own certified logarithms (atanh series with explicit
remainders, exact rationals), finds the least integer K with the inequality certified at N = 2^K, certifies that it
holds at every larger N (the derivative condition z - theta_hi > p/(c + ln N)), and that it fails at K - 1000 even
with the most favourable bounds (so K is minimal for these parameters, up to 1000), recomputes #4535's margin at K = 10^12, and
recomputes the frozen word's height and class-count envelopes at both ranks with #4535's own formulas
(G_depth <= 2 floor(log_1024 floor(N/145)), C_N < 2^(17 G_depth + 31)). Nothing about kappa, the mirror, the root
bracket or the outer ledger changes.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Fr
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
RESULT = HERE / "PR4535-RESULT.json"  # #4535 head a6d7237f, research/critical-root-multiplication/RESULT.json, blob 1c7af6e3
RESULT_SHA256 = "e830f4cab30e70ab02d2ecca283969bd97f3a6925948b61d0eb15df3be831b14"
TERMS = 60


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def atanh_bounds(x):
    """Bounds on atanh(x) for rational 0 <= x < 1: partial sum and remainder <= x^(2J+1)/((2J+1)(1-x^2))."""
    s, p = Fr(0), x
    for j in range(TERMS):
        s += p / (2 * j + 1)
        p *= x * x
    return s, s + p / ((2 * TERMS + 1) * (1 - x * x))


LN2 = tuple(2 * v for v in atanh_bounds(Fr(1, 3)))  # ln 2 = 2 atanh(1/3)


def ln_bounds(y):
    """Certified [lo, hi] for ln y, rational y > 0: y = 2^k m with m in [1, 2), ln m = 2 atanh((m-1)/(m+1))."""
    y = Fr(y)
    k = y.numerator.bit_length() - y.denominator.bit_length()
    m = y / Fr(2) ** k
    while m >= 2:
        m /= 2
        k += 1
    while m < 1:
        m *= 2
        k -= 1
    lo, hi = atanh_bounds((m - 1) / (m + 1))
    lo, hi = 2 * lo, 2 * hi
    return (k * LN2[0] + lo, k * LN2[1] + hi) if k >= 0 else (k * LN2[1] + lo, k * LN2[0] + hi)


def coarse(v, den=10 ** 30):
    """Round a rational up to a multiple of 1/den (keeps fractions small)."""
    return Fr(-((-v.numerator * den) // v.denominator), den)


def main():
    raw = RESULT.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == RESULT_SHA256, "vendored #4535 RESULT.json")
    res = json.loads(raw)
    theta_lo, theta_hi = (Fr(v) for v in res["critical_root"]["critical_root_interval"])
    s_C = Fr(res["uniform_saving"])
    z = 1 - s_C
    gap = z - theta_hi
    need(gap == Fr(res["absorption"]["positive_gap"]) == Fr(377, 10 ** 12), "z - theta_hi = 377/10^12")
    need(Fr(res["kappa"]) == Fr(604033, 200000000), "kappa unchanged")
    p, c = Fr(2, 5), 133
    n0 = 145 * 1024 ** 650
    ln_n0 = ln_bounds(n0)
    # #4535 bounds ln A by (1 - theta_lo) ln n0, dropping the factor (c + ln n0)^(-p) <= 1. Its own definition
    # A = n0^(1-theta)/(c + ln n0)^p gives the sharper certified bound used here; both are reported.
    lnA_coarse = coarse((1 - theta_lo) * ln_n0[1])
    need(lnA_coarse <= coarse(Fr(res["absorption"]["logA_upper"])) + Fr(1, 10 ** 20), "coarse ln A agrees with #4535")
    lnA_hi = coarse((1 - theta_lo) * ln_n0[1] - p * ln_bounds(c + ln_n0[0])[0])
    need(LN2[1] - LN2[0] < Fr(1, 10 ** 50), "ln 2 enclosure")

    def margin_lo(K, lnA=None):
        lnN_lo, lnN_hi = K * LN2[0], K * LN2[1]
        return gap * lnN_lo - (lnA_hi if lnA is None else lnA) - p * ln_bounds(c + coarse(lnN_hi))[1]

    def margin_hi(K):  # most favourable: smallest A term (A >= n0^(1-theta_hi)/(c + ln n0)^p), lower log bounds
        lnN_lo, lnN_hi = K * LN2[0], K * LN2[1]
        lnA_lo = (1 - theta_hi) * ln_n0[0] - p * ln_bounds(c + ln_n0[1])[1]
        return gap * lnN_hi - lnA_lo - p * ln_bounds(c + K * LN2[0])[0]

    def least(lnA=None):
        lo, hi = 1, 10 ** 12
        need(margin_lo(hi, lnA) > 0, "#4535's rank certifies")
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if margin_lo(mid, lnA) > 0:
                hi = mid
            else:
                lo = mid
        need(margin_lo(hi, lnA) > 0 and margin_lo(hi - 1, lnA) <= 0, "least certified K")
        return hi

    K_coarse = least(lnA_coarse)
    K = least()
    # For this certificate (same A, p, c, theta bracket and gap) no materially smaller K can work: below the
    # most favourable crossing the inequality fails outright.
    K_fail = K - 1000
    need(margin_hi(K_fail) < 0, "the inequality genuinely fails well below K")
    # Monotone beyond K: d/dlnN [gap lnN - p ln(c + lnN)] = gap - p/(c + lnN) > 0.
    need(gap - p / (c + K * LN2[0]) > 0, "absorption holds at every larger N")
    need(K > n0.bit_length() and K_coarse > K, "N above the base cutoff n0")

    def envelopes(K):
        # floor(N/145) for N = 2^K has bit length K - 7; log_1024 floor(N/145) < (K - 7)/10 + 1.
        G = 2 * ((K - 8) // 10 + 1)
        return G, 17 * G + 31

    G_old, logC_old = envelopes(10 ** 12)
    G_new, logC_new = envelopes(K)
    need(G_old <= 200000000000 and logC_old <= 3400000000031, "#4535's envelopes reproduced")
    report = {"status": "PASS_PR4535_SMALLER_RANK", "kappa": "604033/200000000 (unchanged)",
              "least_certified_K_with_4535_coarse_lnA": K_coarse,
              "least_certified_K": K, "ratio_10^12_over_K": round(10 ** 12 / K, 3),
              "lnA_upper": {"coarse_as_4535": float(lnA_coarse), "exact_formula": float(lnA_hi)},
              "margin_at_K_nats": float(margin_lo(K)), "margin_at_10^12_nats": float(margin_lo(10 ** 12)),
              "fails_at_K_minus_1000_even_favourably": True,
              "G_depth_bound": {"N=2^10^12": G_old, "N=2^K": G_new},
              "log2_class_envelope": {"N=2^10^12": logC_old, "N=2^K": logC_new},
              "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
