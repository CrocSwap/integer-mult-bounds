#!/usr/bin/env python3
"""PR #4535 at outer slack d = 10^-12: same kappa, all outer predicates replayed, and a smaller certified finite rank.

#4535 (head a6d7237f; RESULT.json vendored, sha256-pinned) uses kappa = 0.003020165 with outer parameters
b = kappa+5d, a = kappa+4d, q = kappa+3d, epsilon = 1-d, beta = 1-3d, r0 = d/10, stop = layout = d, tested saving
kappa+7d and complex uniform saving s_C = kappa+6d at d = 10^-10. Its absorption gap is z - theta_hi with
z = 1 - s_C, i.e. (1 - theta_hi) - kappa - 6d.

This verifier executes the outer ledger source that #4535 itself pins (research/pr4359-p7-padding/dependencies/
compiler-refill/endpoint.py, sha256-checked) with the ordinary BIT admission from research/compact-joint-compiler/
arithmetic/RESULT.json (sha256-checked), exactly as #4535's verify.py does:
  * at d = 10^-10 it reproduces #4535's 54 strict checks, 4 functional guards, nine margins and its recorded minimum
    margin 29969798347/10^20 above kappa (control);
  * at d = 10^-12 every strict check, functional guard and margin still passes, with minimum margin above kappa
    reported exactly;
  * with own certified logarithms it finds the least K with A N^theta (133 + ln N)^(2/5) < N^z at N = 2^K for the new
    gap, using the same A, p, c, n0 and root bracket, its minimality up to 1000 and monotonicity beyond.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Fr
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEDGER = ROOT / "research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py"
LEDGER_SHA256 = "d097e55f06c3f244f2074ffd7c1a0a5f3c4b4b6a6accf9619d1dde5c0ae85e15"
COMPILER = ROOT / "research/compact-joint-compiler/arithmetic/RESULT.json"
COMPILER_SHA256 = "a6caaa2a6d6460a8c1ef7e48c4853bb27976be33a52b96a4216dfa90d96c9091"
RESULT = HERE / "PR4535-RESULT.json"  # #4535 head a6d7237f, research/critical-root-multiplication/RESULT.json, blob 1c7af6e3
RESULT_SHA256 = "e830f4cab30e70ab02d2ecca283969bd97f3a6925948b61d0eb15df3be831b14"
TERMS = 60


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def atanh_bounds(x):
    s, p = Fr(0), x
    for j in range(TERMS):
        s += p / (2 * j + 1)
        p *= x * x
    return s, s + p / ((2 * TERMS + 1) * (1 - x * x))


LN2 = tuple(2 * v for v in atanh_bounds(Fr(1, 3)))


def ln_bounds(y):
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
    return Fr(-((-v.numerator * den) // v.denominator), den)


def load_ledger():
    raw = LEDGER.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == LEDGER_SHA256, "pinned outer ledger source")
    ns = {"__file__": str(LEDGER), "__name__": "outer_exact"}
    exec(compile(raw, str(LEDGER), "exec"), ns)
    comp_raw = COMPILER.read_bytes()
    need(hashlib.sha256(comp_raw).hexdigest() == COMPILER_SHA256, "pinned compiler result")
    return ns, json.loads(comp_raw)


def outer(O, comp, k, d):
    a = {"kappa": k, "tested_saving": k + 7 * d, "complex_uniform_saving": k + 6 * d, "b": k + 5 * d, "a": k + 4 * d,
         "q": k + 3 * d, "bit_saving": Fr(comp["ordinary_BIT"]["admitted"]), "epsilon": 1 - d, "beta": 1 - 3 * d,
         "r0": d / 10, "stop": d, "layout": d, "d": d}
    res = O["ledger"](a)
    res["functional_checks"]["actual_new_BIT_stock_sublinear"] = a["beta"] * (1 - Fr(comp["ordinary_BIT"]["atom"]))
    need(len(res["strict_checks"]) == 54, "54 strict checks")
    need(all(v > 0 for v in res["strict_checks"].values()), "strict checks")
    need(len(res["functional_checks"]) == 4 and all(v > 0 for v in res["functional_checks"].values()), "functional guards")
    need(len(res["margins"]) == 9 and all(v > k for v in res["margins"].values()), "nine margins above kappa")
    return min(res["margins"].values()) - k, a


def least_rank(gap, theta_lo):
    p, c = Fr(2, 5), 133
    ln_n0 = ln_bounds(145 * 1024 ** 650)
    lnA = coarse((1 - theta_lo) * ln_n0[1] - p * ln_bounds(c + ln_n0[0])[0])

    def margin(K):
        return gap * K * LN2[0] - lnA - p * ln_bounds(c + coarse(K * LN2[1]))[1]

    lo, hi = 1, 10 ** 12
    need(margin(hi) > 0, "certifies at 10^12")
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if margin(mid) > 0 else (mid, hi)
    need(margin(hi) > 0 and margin(hi - 1) <= 0, "least certified K")
    need(gap - p / (c + hi * LN2[0]) > 0, "monotone beyond K")
    return hi, lnA


def main():
    raw = RESULT.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == RESULT_SHA256, "vendored #4535 RESULT.json")
    res = json.loads(raw)
    k = Fr(res["kappa"])
    theta_lo, theta_hi = (Fr(v) for v in res["critical_root"]["critical_root_interval"])
    O, comp = load_ledger()
    m10, a10 = outer(O, comp, k, Fr(1, 10 ** 10))
    need(m10 == Fr(res["minimum_outer_margin_above_kappa"]), "control: #4535's recorded minimum outer margin")
    need(O["encode"](a10) == res["outer_parameters"], "control: #4535's outer parameters")
    d = Fr(1, 10 ** 12)
    m12, a12 = outer(O, comp, k, d)
    gap10 = (1 - theta_hi) - (k + 6 * Fr(1, 10 ** 10))
    gap12 = (1 - theta_hi) - (k + 6 * d)
    need(gap10 == Fr(377, 10 ** 12) and gap12 > gap10, "gaps")
    K10, _ = least_rank(gap10, theta_lo)
    K12, lnA = least_rank(gap12, theta_lo)
    need(K10 == 77014944503, "reproduces #4563's least rank at d = 10^-10")
    report = {"status": "PASS_PR4535_OUTER_SLACK_RANK", "kappa": str(k) + " (unchanged)",
              "d_1e-10": {"min_outer_margin_above_kappa": str(m10), "gap": str(gap10), "least_K": K10},
              "d_1e-12": {"min_outer_margin_above_kappa": str(m12), "gap": str(gap12), "least_K": K12,
                          "outer_parameters": O["encode"](a12)},
              "rank_exponent_ratio_vs_10^12": round(10 ** 12 / K12, 3),
              "log2_class_envelope_at_K": 17 * 2 * ((K12 - 8) // 10 + 1) + 31,
              "lnA_upper": float(lnA), "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
