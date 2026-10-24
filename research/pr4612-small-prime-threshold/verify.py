#!/usr/bin/env python3
"""Small-prime check of PR #4612's outer-reserve threshold (Matarener, head 7e362114).

#4612 states (README, "Threshold"; verify.py outer_reserve) that for q0(h,p) <= C(log2 h + h^d L^3 + 1), L = log2 p,
d in {0.003, 0.004}, the displayed threshold H(p) = [1024 C L^3]^(1/(1-d)) "already suffices" for every C >= 1:
"C(log2 h + 2) <= h/1024 there as well", hence q0 + O(1) <= h/64 and R(h) <= 3h/128 + q0 <= h/16. Its grid uses
L in {8, 64, 1024, 2^20, 2^40} only (p >= 256).

Findings (log-domain float arithmetic with explicit margins >= 1e-3 in log2 units; scoped, no kappa change):
  * at p = 2 (L = 1) the intermediate claim C(log2 h + 2) <= h/1024 fails at h = H for every tested C (1 .. 2^1000);
  * with #4612's own width constant C = 232960, q0's bound exceeds h/64 at h = H(2) (q0/h ~ 0.0276 > 0.0156);
  * for C = 2^40, 2^100 and 2^1000 the conclusion R(h) <= h/16 itself fails at h = H(2) for both atoms
    (it is rescued only when log2 C is so large that the factor (1024 C)^(d/(1-d)) dominates, e.g. 2^10000);
  * correction: H'(p) = max(H(p), 4096 C log2(4096 C)). With a = 1024 C >= 1024 and h >= 4a log2(4a):
    a(log2 h + 2) <= h at h = 4a log2(4a) because log2 log2(4a) + 2 <= 3 log2(4a), and h - a log2 h increases for
    h > a/ln 2. Above H also C h^d L^3 <= h/1024. Hence q0 <= h/512 <= h/64 and R <= h/16; the threshold stays
    polylogarithmic in p (the new term does not depend on p). Checked on a grid that includes L = 1 and small primes.
The constant C itself remains unbound (#4612's open question 1); the conclusion R <= h/16 survives with H'.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import json
import math
import sys

DELTAS = (0.003, 0.004)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def log2_threshold(log_c, l, d):
    return (10 + log_c + 3 * math.log2(l)) / (1 - d)


def ratios(log_c, l, d, lh):
    """(log2 of C(log2 h + 2) / h, q0_bound / h) at log2 h = lh."""
    inter = log_c + math.log2(lh + 2) - lh
    q0 = 2 ** (log_c - lh) * (lh + 1) + 2 ** (log_c + d * lh + 3 * math.log2(l) - lh)
    return inter, q0


def main():
    out = {"intermediate_fails_at_p2": [], "h64_fails": [], "R_fails": []}
    for d in DELTAS:
        for log_c in (0, math.log2(232960), 40, 100, 1000):
            inter, q0 = ratios(log_c, 1, d, log2_threshold(log_c, 1, d))
            need(inter > -10 + 1e-3, "C(log2 h + 2) > h/1024 at h = H(2)")
            out["intermediate_fails_at_p2"].append([d, round(log_c, 3)])
            if q0 > 1 / 64:
                out["h64_fails"].append([d, round(log_c, 3), round(q0, 5)])
            if q0 > 5 / 128:
                out["R_fails"].append([d, round(log_c, 3), round(q0, 5)])
        _, q_big = ratios(10000, 1, d, log2_threshold(10000, 1, d))
        need(q_big <= 5 / 128, "very large C is rescued by the (1024 C)^(d/(1-d)) factor")
    need(any(abs(c - math.log2(232960)) < 1e-2 for _, c, _ in out["h64_fails"]), "C = 232960: q0 > h/64 at H(2)")
    need({c for _, c, _ in out["R_fails"]} == {40, 100, 1000}, "R <= h/16 fails at H(2) for C = 2^40, 2^100, 2^1000")
    # #4612's own grid (L >= 8) does pass, which is why it did not see the failure
    for d in DELTAS:
        for log_c in (0, 20, 1000):
            for l in (8, 64, 1024):
                lh = log2_threshold(log_c, l, d)
                need(ratios(log_c, l, d, lh)[1] <= 1 / 64, "#4612 grid passes")
    # corrected threshold H' = max(H, 4096 C log2(4096 C)): q0 <= h/512 on a grid including small primes
    for d in DELTAS:
        for log_c in (0, 5, math.log2(232960), 40, 100, 1000, 10000):
            for l in (1, math.log2(3), math.log2(5), math.log2(7), 8, 64, 1024, 2 ** 20):
                lh0 = max(log2_threshold(log_c, l, d), 12 + log_c + math.log2(12 + log_c))
                for s in (0, 0.5, 1, 10, 100, 1e4):
                    inter, q0 = ratios(log_c, l, d, lh0 + s)
                    need(inter <= -10 + 1e-9 and q0 <= 1 / 512 + 1e-12, "corrected threshold suffices")
    need(all(math.log2(math.log2(4 * a)) + 2 <= 3 * math.log2(4 * a) for a in (1024, 2 ** 20, 2 ** 100)),
         "lemma: log2 log2(4a) + 2 <= 3 log2(4a) for a >= 1024")
    print(json.dumps({"status": "PASS_PR4612_SMALL_PRIME_THRESHOLD_CHECK", **out,
                      "corrected_threshold": "H'(p) = max([1024 C L^3]^(1/(1-d)), 4096 C log2(4096 C))",
                      "conclusion_R_le_h_over_16_with_corrected_threshold": True, "new_kappa_claimed": False},
                     indent=1))


if __name__ == "__main__":
    sys.exit(main())
