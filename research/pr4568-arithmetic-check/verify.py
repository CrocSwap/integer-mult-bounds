#!/usr/bin/env python3
"""Independent arithmetic check of PR #4568 (hexapode): conditional kappa = 0.00302016597 (+9.7e-10 over #4535).

#4568 (head b269a729; RESULT.json vendored, sha256-pinned) keeps #4535's native profile, critical-root bracket and
#4532 majorant, and moves the outer point to d = 10^-12 with z = .996979834024, kappa = .00302016597, q, a, b =
kappa + 3d, 4d, 5d, tested saving kappa + 7d and complex uniform saving s_C = 1 - z = kappa + 6d. This verifier:
  * replays the outer ledger source that #4535/#4568 pin (research/pr4359-p7-padding/dependencies/compiler-refill/
    endpoint.py, sha256-checked) with the ordinary BIT admission (research/compact-joint-compiler/arithmetic/RESULT.json)
    at #4568's exact parameters: 54 strict predicates, 4 functional guards, 9 margins above kappa, the recorded minimum
    margin and the full outer_parameters encoding;
  * checks the saving order kappa < s_C < tested saving < 1 - theta (theta in #4535's bracket, open at theta_hi) and
    the absorption gap z - theta_hi = 10^-12 exactly;
  * with own certified logarithms, checks absorption at #4568's N = 2^(10^14) and finds the least certified rank K for
    (i) #4532's p16 witness with #4568's coarse ln A, (ii) the same witness with A's own definition, and (iii) my #4565
    retuned witness (M = 2^24, ell0 = 64, p = 3/10, c = 101), monotone beyond K.
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
RESULT = HERE / "PR4568-RESULT.json"  # #4568 head b269a729, research/critical-slack-multiplication/RESULT.json, blob 540ffb95
RESULT_SHA256 = "b55c34dd733ed09472c487ea21df1f7c102c3427bcb05222e60b218242715abb"
THETA = (Fr(9969798340229, 10 ** 13), Fr(996979834023, 10 ** 12))  # #4535's isolated root bracket
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



def least_rank(lnA, p, c, gap, K_max=10 ** 15):
    def margin(K):
        return gap * K * LN2[0] - lnA - p * ln_bounds(c + coarse(K * LN2[1]))[1]

    lo, hi = 1, K_max
    need(margin(hi) > 0, "certifies at K_max")
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if margin(mid) > 0 else (mid, hi)
    need(margin(hi) > 0 and margin(hi - 1) <= 0, "least certified K")
    need(gap - p / (c + hi * LN2[0]) > 0, "monotone beyond K")
    return hi, margin


def main():
    raw = RESULT.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == RESULT_SHA256, "vendored #4568 RESULT.json")
    res = json.loads(raw)
    ledger_raw = LEDGER.read_bytes()
    need(hashlib.sha256(ledger_raw).hexdigest() == LEDGER_SHA256, "pinned outer ledger")
    ns = {"__file__": str(LEDGER), "__name__": "outer_exact"}
    exec(compile(ledger_raw, str(LEDGER), "exec"), ns)
    comp_raw = COMPILER.read_bytes()
    need(hashlib.sha256(comp_raw).hexdigest() == COMPILER_SHA256, "pinned compiler result")
    comp = json.loads(comp_raw)
    k = Fr(res["kappa"])
    d = Fr(1, 10 ** 12)
    need(k == Fr("0.00302016597"), "kappa")
    a = {"kappa": k, "tested_saving": k + 7 * d, "complex_uniform_saving": k + 6 * d, "b": k + 5 * d, "a": k + 4 * d,
         "q": k + 3 * d, "bit_saving": Fr(comp["ordinary_BIT"]["admitted"]), "epsilon": 1 - d, "beta": 1 - 3 * d,
         "r0": d / 10, "stop": d, "layout": d, "d": d}
    need(ns["encode"](a) == res["outer_parameters"], "outer parameters are kappa + jd at d = 1e-12")
    out = ns["ledger"](a)
    out["functional_checks"]["actual_new_BIT_stock_sublinear"] = a["beta"] * (1 - Fr(comp["ordinary_BIT"]["atom"]))
    need(len(out["strict_checks"]) == 54 and all(v > 0 for v in out["strict_checks"].values()), "54 strict predicates")
    need(len(out["functional_checks"]) == 4 and all(v > 0 for v in out["functional_checks"].values()), "4 guards")
    need(len(out["margins"]) == 9 and all(v > k for v in out["margins"].values()), "9 margins above kappa")
    min_margin = min(out["margins"].values()) - k
    need(min_margin == Fr(res["minimum_outer_margin_above_kappa"]), "recorded minimum outer margin")
    s_C, tested = a["complex_uniform_saving"], a["tested_saving"]
    need(s_C == Fr(res["uniform_saving"]), "uniform saving")
    need(k < s_C < tested == 1 - THETA[1] < 1 - THETA[0], "saving order (the root theta < theta_hi strictly)")
    z = 1 - s_C
    gap = z - THETA[1]
    need(gap == Fr(1, 10 ** 12), "absorption gap 1e-12")
    ln_n0 = ln_bounds(145 * 1024 ** 650)
    lnA_coarse = coarse((1 - THETA[0]) * ln_n0[1])
    need(lnA_coarse <= coarse(Fr(res["absorption"]["logA_upper"])) + Fr(1, 10 ** 20), "coarse ln A as #4568")
    lnA_exact = coarse((1 - THETA[0]) * ln_n0[1] - Fr(2, 5) * ln_bounds(133 + ln_n0[0])[0])
    ln_n0r = ln_bounds(145 * (1 << 24) ** 64)
    lnA_retuned = coarse((1 - THETA[0]) * ln_n0r[1] - Fr(3, 10) * ln_bounds(101 + ln_n0r[0])[0])
    K1, margin1 = least_rank(lnA_coarse, Fr(2, 5), 133, gap)
    K2, _ = least_rank(lnA_exact, Fr(2, 5), 133, gap)
    K3, _ = least_rank(lnA_retuned, Fr(3, 10), 101, gap)
    m_at = margin1(10 ** 14)
    need(m_at > Fr(418, 15), "absorption margin at N = 2^(10^14) exceeds #4568's certified 418/15")
    report = {"status": "PASS_PR4568_ARITHMETIC_CHECK", "kappa": str(k),
              "outer": {"strict": 54, "guards": 4, "margins": 9, "min_margin_above_kappa": str(min_margin)},
              "absorption_gap": str(gap), "margin_at_N=2^10^14_nats": float(m_at),
              "least_K": {"4532_witness_coarse_lnA": K1, "4532_witness_exact_A": K2, "4565_retuned": K3},
              "rank_exponent_ratio_10^14_over_retuned": round(10 ** 14 / K3, 2), "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
