#!/usr/bin/env python3
"""A retuned critical-root majorant for the p16 (#4470) profile and a smaller certified finite rank for #4535.

Same kappa = 0.003020165, same native profile, same isolated critical root. Only the compiler geometry and the
logarithmic majorant parameters of #4532's critical-root theorem change.

Gates. #4532's own exact checker `critical_guards` (root_application.py, vendored from #4535 head a6d7237f and
sha256-pinned) is run on the p16 profile from research/compact-joint-compiler/arithmetic/RESULT.json (sha256-pinned)
for two witnesses over the same root bracket [0.996979, 0.996980] that #4532 uses:
  * control: #4532's p16 witness (M = 1024, a = b = 1, ell0 = 650, p = 2/5, c = 133), as retained in
    research/rank-convergence/BENCHMARKS.json (sha256-pinned), cover exponent .997067;
  * retuned: M = 2^24, a = 3, b = 2, s = 1/10, lambda = 1/5, ell0 = 64, p = 3/10, c = 101, guards U = .9494,
    V = .8776, Q = 1.0015, d = 1.04, beta = .564, cover exponent .99725.
Both pass every guard (tails, forward ordering, moment ratio, mean gap, concavity, mirror at the cover exponent,
tangent cover, recurrence funding); three mutations of the retuned witness are rejected.

Rank. With own certified logarithms (exact rationals) and the normalisation A = n0^(1-theta)/(c + ln n0)^p,
n0 = 145 M^ell0, the least K with ln A + p ln(c + ln N) < (z - theta_hi) ln N at N = 2^K is found for both witnesses
at #4535's gap 377/10^12 (d = 10^-10) and at #4564's gap 971/10^12 (d = 10^-12), with monotonicity beyond K.
The control reproduces #4563 and #4564. The height and class-count envelopes are recomputed with the new geometry,
G_depth <= g floor(log_M floor(N/145)) with g = a + b.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Fr
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE = HERE / "PR4532-root_application.py"  # #4535 head a6d7237f, research/adaptive-gate-existence/root_application.py, blob 89d6139b
ENGINE_SHA256 = "e656ef12f73a8dd3bdb256eca95a712de1269facb18a652fc4068ba718619b4d"
PROFILE = ROOT / "research/compact-joint-compiler/arithmetic/RESULT.json"
PROFILE_SHA256 = "a6caaa2a6d6460a8c1ef7e48c4853bb27976be33a52b96a4216dfa90d96c9091"
BENCH = ROOT / "research/rank-convergence/BENCHMARKS.json"
BENCH_SHA256 = "513efe2fe74af82891c1918e462ba8338b1bbd06403cbfcec284bcf3b4f8f850"
THETA = (Fr(9969798340229, 10 ** 13), Fr(996979834023, 10 ** 12))  # #4535's isolated root bracket
KAPPA = Fr(604033, 200000000)
TERMS = 60


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def pinned(path, digest):
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == digest, f"pinned bytes: {path.name}")
    return raw


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


def least_rank(M, ell, p, c, gap):
    ln_n0 = ln_bounds(145 * M ** ell)
    lnA = coarse((1 - THETA[0]) * ln_n0[1] - p * ln_bounds(c + ln_n0[0])[0])

    def margin(K):
        return gap * K * LN2[0] - lnA - p * ln_bounds(c + coarse(K * LN2[1]))[1]

    lo, hi = 1, 10 ** 12
    need(margin(hi) > 0, "certifies at 10^12")
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if margin(mid) > 0 else (mid, hi)
    need(margin(hi) > 0 and margin(hi - 1) <= 0, "least certified K")
    need(gap - p / (c + hi * LN2[0]) > 0, "monotone beyond K")
    need(hi > (145 * M ** ell).bit_length(), "N above n0")
    return hi, lnA


def envelope(K, M, g):
    logM = M.bit_length() - 1
    G = g * ((K - 8) // logM + 1)  # floor(N/145) < 2^(K-7)
    return G, 17 * G + 31


def main():
    ns = {"__file__": str(ENGINE), "__name__": "root_exact"}
    exec(compile(pinned(ENGINE, ENGINE_SHA256), str(ENGINE), "exec"), ns)
    profile = json.loads(pinned(PROFILE, PROFILE_SHA256))
    bench = {row["name"]: row["witness"] for row in json.loads(pinned(BENCH, BENCH_SHA256))["cases"]}
    lo, hi = Fr("0.996979"), Fr("0.996980")
    old = bench["p16"]
    control = {key: old[key] for key in ("a", "b", "height_base", "ell0", "s", "lambda", "p", "c")}
    control["guards"] = {key: old["guards"][key] for key in ("U", "V", "Q", "d", "beta")}
    control["upper_exponent"] = ".997067"
    retuned = {"a": 3, "b": 2, "height_base": 1 << 24, "ell0": 64, "s": "1/10", "lambda": "1/5", "p": "3/10", "c": "101",
               "guards": {"U": ".9494", "V": ".8776", "Q": "1.0015", "d": "1.04", "beta": ".564"},
               "upper_exponent": ".99725"}
    results = {}
    for name, w in (("control_4532_p16", control), ("retuned", retuned)):
        r = ns["critical_guards"](profile, lo, hi, w)
        results[name] = {k: r[k] for k in ("mixed_tail_upper", "root_tail_upper", "moment_ratio_upper", "mirror_upper",
                                            "tangent_exponent_upper", "funding_lower", "required_funding_upper")}
    rejected = {}
    for label, change, expected in (("ell0 too small", {"ell0": 40}, "critical tangent cover"),
                                    ("p underfunded", {"p": "1/5", "c": "101"}, "critical recurrence funding"),
                                    ("beta below the mirror", {"guards": dict(retuned["guards"], beta=".55")},
                                     "critical mirror window")):
        bad = dict(retuned, **change)
        try:
            ns["critical_guards"](profile, lo, hi, bad)
        except ValueError as error:
            need(str(error) == expected, f"unexpected rejection for {label}: {error}")
            rejected[label] = str(error)
        else:
            raise AssertionError(f"mutation accepted: {label}")
    gaps = {"d=1e-10": (1 - THETA[1]) - (KAPPA + 6 * Fr(1, 10 ** 10)),
            "d=1e-12": (1 - THETA[1]) - (KAPPA + 6 * Fr(1, 10 ** 12))}
    need(gaps["d=1e-10"] == Fr(377, 10 ** 12) and gaps["d=1e-12"] == Fr(971, 10 ** 12), "gaps")
    ranks = {}
    for name, (M, ell, p, c, g) in {"control_4532_p16": (1024, 650, Fr(2, 5), 133, 2),
                                    "retuned": (1 << 24, 64, Fr(3, 10), 101, 5)}.items():
        ranks[name] = {}
        for gname, gap in gaps.items():
            K, lnA = least_rank(M, ell, p, c, gap)
            G, logC = envelope(K, M, g)
            ranks[name][gname] = {"least_K": K, "lnA_upper": float(lnA), "G_depth": G, "log2_class_envelope": logC}
    need(ranks["control_4532_p16"]["d=1e-10"]["least_K"] == 77014944503, "control reproduces #4563")
    need(ranks["control_4532_p16"]["d=1e-12"]["least_K"] == 29328002299, "control reproduces #4564")
    report = {"status": "PASS_PR4532_RETUNED_MAJORANT", "kappa": str(KAPPA) + " (unchanged)", "gates": results,
              "rejected_mutations": rejected, "ranks": ranks,
              "exponent_ratio_vs_4535": round(10 ** 12 / ranks["retuned"]["d=1e-12"]["least_K"], 2),
              "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
