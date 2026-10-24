#!/usr/bin/env python3
"""Independent check of PR #4521 (Dillon): #4436's fully expanded rank-mass identity, with separately written code.

Using my own #4436 default-height flow (flow4436.py, written for my #4456 checks; nothing imported from #4521 or
#4436), this recomputes the expanded counts with #4436's nested widths a_n = B_(n-1), B_n = a_n S_n:
B_n (width), P_n (rank-one leaves), U_n (raw invocations) and Q_n (their column multiplicities), with base values
B = 1, P = n, U = Q = 0 below m, and child batches C = a_n S_s / B_(n-s) (source complements) and a_n E_e / B_e
(exits), required to be integers. At every rank it checks B_n n - P_n = Delta Q_n and U_n <= Q_n <= B_n n / Delta,
and at the checkpoints it compares the exact big integers B, P, Q, U with #4521's published SHA256 hashes and bit
lengths (vendored RESULT.json, blob 85ee0166): two toy rules at rank 100 and raw p7 (bound to main) at rank 1000.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULT = HERE / "PR4521-RESULT.json"
RESULT_SHA256 = "d7c90173a64629da0746015d2f03083204e4a0fdd0d43956341fea0a422062e3"
P7 = ROOT / "research/higher-moment-strictification/RESULT.json"
P7_SHA256 = "ad79e3c0459e7b495a0ca34010553b12147779a007389e1695cc1336f123c156"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def expanded(flow, W, P, N):
    m = max(W)
    delta = sum(k * x for k, x in W.items()) - sum(r * x for r, x in P.items())
    need(delta > 0, "positive surplus")
    B, Pn, U, Q = [1] * m, list(range(m)), [0] * m, [0] * m
    for n in range(m, N + 1):
        R = flow(n, W, P)
        a = B[n - 1]
        Bn = a * sum(R["S"].values())
        p = u = q = 0
        children = [(n - s, cnt) for s, cnt in R["S"].items()] + [(e, cnt) for e, cnt in R["X"].items() if cnt]
        for r, cnt in children:
            need(0 <= r < n and (a * cnt) % B[r] == 0, "integral child batch, strict descent")
            c = a * cnt // B[r]
            p, u, q = p + c * Pn[r], u + c * U[r], q + c * Q[r]
        u += a * R["units"]
        q += a * R["col"]
        need(Bn * n - p == delta * q, f"identity at n = {n}")
        need(u <= q and delta * q <= Bn * n, f"bounds at n = {n}")
        B.append(Bn), Pn.append(p), U.append(u), Q.append(q)
    return {"B": B[N], "P": Pn[N], "Q": Q[N], "U": U[N]}


def digest(x):
    return hashlib.sha256(x.to_bytes((x.bit_length() + 7) // 8, "big")).hexdigest()


def main():
    ns = {"__name__": "flow4436"}
    exec(compile((HERE / "flow4436.py").read_bytes(), str(HERE / "flow4436.py"), "exec"), ns)
    raw = RESULT.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == RESULT_SHA256, "vendored #4521 RESULT.json")
    res = json.loads(raw)
    need(hashlib.sha256(P7.read_bytes()).hexdigest() == P7_SHA256, "pinned p7 source")
    o = json.loads(P7.read_bytes())["invoice_oracle"]
    p7 = ({int(k): v for k, v in o["targets"].items()}, {int(k): v for k, v in o["paid"].items()})
    cases = []
    for entry in res["toy_counted_expansions"]:
        W = {int(k): v for k, v in entry["targets"].items()}
        P = {int(k): v for k, v in entry["paid"].items()}
        cases.append((W, P, entry["n"], entry["expanded_counts"]))
    pe = res["p7_counted_expansion"]
    cases.append((p7[0], p7[1], pe["n"], pe["expanded_counts"]))
    matched = 0
    for W, P, N, published in cases:
        got = expanded(ns["flow"], W, P, N)
        for key in ("B", "P", "Q", "U"):
            need(got[key].bit_length() == published[key]["bits"], f"{key} bit length at N = {N}")
            need(digest(got[key]) == published[key]["unsigned_big_endian_sha256"], f"{key} hash at N = {N}")
            matched += 1
    print(json.dumps({"status": "PASS_PR4521_EXPANDED_COUNT_CHECK", "rules": len(cases), "exact_totals_matched": matched,
                      "p7_rank": pe["n"], "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
