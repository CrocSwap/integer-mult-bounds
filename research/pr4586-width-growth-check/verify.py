#!/usr/bin/env python3
"""Independent check of PR #4586 (mihir-s-05): quasipolynomial growth of #4507's chronological batch widths.

#4586 checks its lemmas on an authenticated copy of #4507's own generator. This verifier instead uses separately
written code (flow_widths.py: my default-height flow for #4436 and my width recurrence for #4507) on the raw p7 rule
bound to main's research/higher-moment-strictification/RESULT.json (sha256-pinned), through rank N = 4000:
  * B_1000 has 2,524 bits, as #4586 and #4507 report;
  * rank descent: every recursive rank in J_n (source complements n - s and actual exits e) is <= floor((m-1)n/m);
  * B_n | L_N^D(n) for every n <= N, checked by D(n) rounds of gcd stripping (no factoring);
  * the depth bound (2) D(n) <= 1 + floor(log(n/m)/log(m/(m-1)));
  * the source-state lemma: the flow's height and complete source census at n equal those at m*t, t the largest
    Pi-smooth integer <= floor(n/m), Pi = {2,3,5,7,11,19,41} (d = 7), for every n in [m, N];
  * the counting bound (5) |H(M)| <= prod_p (1 + floor(log_p M));
  * #4586's explicit exponent D(N) K_N ceil(log2 C_N) = 303,840 at N = 1000.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import json
import math
from math import gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/higher-moment-strictification/RESULT.json"
SOURCE_SHA256 = "ad79e3c0459e7b495a0ca34010553b12147779a007389e1695cc1336f123c156"
N_MAX = 4000
PI = (2, 3, 5, 7, 11, 19, 41)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    ns = {"__name__": "flow_widths"}
    exec(compile((HERE / "flow_widths.py").read_bytes(), str(HERE / "flow_widths.py"), "exec"), ns)
    raw = SOURCE.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "pinned p7 source")
    oracle = json.loads(raw)["invoice_oracle"]
    W = {int(k): v for k, v in oracle["targets"].items()}
    P = {int(k): v for k, v in oracle["paid"].items()}
    m = max(W)
    need(m == 121 and sorted({p for r in list(W) + list(P) for p in PI if r % p == 0}) == list(PI), "raw p7 rule, d = 7")
    B, nested = ns["widths"](W, P, N_MAX)
    need(B[1000].bit_length() == 2524, "B_1000 has 2,524 bits")

    def D(n):
        d = 0
        while n >= m:
            n = n * (m - 1) // m
            d += 1
        return d

    S, constraints = {}, 0
    for n in range(m, N_MAX + 1):
        R = ns["flow"](n, W, P)
        G, cs, agg = ns["cuts"](n, W, P)
        S[n] = sum(R["S"].values())
        bound = n * (m - 1) // m
        need(all(n - s <= bound for s in R["S"]) and all(e <= bound for e, q, _ in cs), "rank descent")
        constraints += len(R["S"]) + len(cs)
    L = 1
    for n in range(m, N_MAX + 1):
        L = L // gcd(L, S[n]) * S[n]
    for n in range(N_MAX + 1):
        g = B[n]
        for _ in range(D(n)):
            g //= gcd(g, L)
        need(g == 1, f"B_n | L_N^D(n) at n = {n}")
        if n >= m:
            need(D(n) <= 1 + math.floor(math.log(n / m) / math.log(m / (m - 1))), "depth bound (2)")

    def smooth(x):
        for p in PI:
            while x % p == 0:
                x //= p
        return x == 1

    need(all(smooth(r) for r in list(W) + list(P)), "every rank is Pi-smooth")
    for n in range(m, N_MAX + 1):
        t = n // m
        while not smooth(t):
            t -= 1
        R1, R2 = ns["flow"](n, W, P), ns["flow"](m * t, W, P)
        need(R1["G"] == R2["G"] and R1["S"] == R2["S"], f"source-state lemma at n = {n}")
    M = N_MAX // m
    K = 1
    for p in PI:
        k = 0
        while p ** (k + 1) <= M:
            k += 1
        K *= 1 + k
    H_M = len([x for x in range(1, M + 1) if smooth(x)])
    need(H_M <= K, "counting bound (5)")
    # #4586's explicit exponent at N = 1000.
    N1, Wt, Pt = 1000, sum(W.values()), sum(P.values())
    h = 0
    while 5 ** (h + 1) <= N1 // m:
        h += 1
    C = Wt * (Wt + Pt + 1) ** (h + 1)
    K1 = 1
    for p in PI:
        k = 0
        while p ** (k + 1) <= N1 // m:
            k += 1
        K1 *= 1 + k
    exponent = D(N1) * K1 * (C - 1).bit_length()
    need((D(N1), K1, (C - 1).bit_length(), exponent) == (211, 32, 45, 303840), "explicit exponent 303,840")
    print(json.dumps({"status": "PASS_PR4586_WIDTH_GROWTH_CHECK", "ranks_checked": N_MAX - m + 1,
                      "batch_constraints": constraints, "B_1000_bits": 2524, "B_N_bits": B[N_MAX].bit_length(),
                      "L_N_bits": L.bit_length(), "D_N": D(N_MAX), "H_M": H_M, "K_bound": K,
                      "explicit_exponent_N1000": exponent, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
