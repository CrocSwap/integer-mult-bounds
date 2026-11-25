#!/usr/bin/env python3
"""Independent transfer-coupled (5,1,1) census at Q=7.

Does not import model.py or verify.py. Prepared by Wentao Li with substantial
AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
from collections import Counter
from itertools import combinations, permutations
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"
INF = 99

EXPECTED_COVERING = 8749440
EXPECTED_HIST = {84: 1458240, 88: 2083200, 90: 5208000}
EXPECTED_MIN_X = 9
EXPECTED_TARIFF = 452


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def even_table(nz5):
    slots = (0,) + tuple(nz5)
    even = [INF] * 32
    even[0] = 0
    for bits in range(1, 64):
        size = bits.bit_count()
        if size % 2:
            continue
        value = 0
        for i in range(6):
            if bits >> i & 1:
                value ^= slots[i]
        if size < even[value]:
            even[value] = size
    return even


def edge(a, b):
    d = a ^ b
    if d == 0:
        return None
    return 2 * (d.bit_count() - 1)


def dual(e0, e1):
    reach = [(i, e0[i]) for i in range(32) if e0[i] < INF]
    total = 0
    for m in range(1, 32):
        best = INF
        for i, c0 in reach:
            c1 = e1[i ^ m]
            if c1 < INF and c0 + c1 < best:
                best = c0 + c1
        if best >= INF:
            return None
        total += best
    return total


def path_ends(P):
    best = {p: INF for p in P}
    for pref in permutations(P):
        cost = 0
        prev = 0
        ok = True
        for v in pref:
            c = edge(prev, v)
            if c is None:
                ok = False
                break
            cost += c
            prev = v
        if ok and cost < best[pref[-1]]:
            best[pref[-1]] = cost
    return best


def min_fair_x(P, a, b):
    best = INF
    best_prefix = None
    for pref in permutations(P):
        x = 0
        prev = 0
        ok = True
        for v in pref:
            c = edge(prev, v)
            if c is None:
                ok = False
                break
            x += c
            prev = v
        if not ok:
            continue
        x += 1  # transfer C
        pend = pref[-1]
        for tip in (a, b):
            c = edge(pend, tip)
            if c is None:
                ok = False
                break
            x += c
            c = edge(tip, 0)
            if c is None:
                ok = False
                break
            x += c
        if not ok:
            continue
        if x < best:
            best = x
            best_prefix = (0,) + pref
    return None if best >= INF else (best, best_prefix)


def worker(P):
    P = tuple(P)
    rem = [x for x in range(1, 32) if x not in P]
    tables = {t: even_table(P + (t,)) for t in rem}
    ends = path_ends(P)
    hist = Counter()
    covering = 0
    min_x = INF
    witness = None
    for i, a in enumerate(rem):
        ea = tables[a]
        for b in rem[i + 1 :]:
            r = dual(ea, tables[b])
            if r is None:
                continue
            covering += 1
            hist[r] += 1
            if r != 84:
                continue
            close = 2 * (a.bit_count() - 1) + 2 * (b.bit_count() - 1)
            lb = INF
            for pend in P:
                ca = edge(pend, a)
                cb = edge(pend, b)
                if ca is None or cb is None or ends[pend] >= INF:
                    continue
                lb = min(lb, ends[pend] + 1 + ca + cb + close)
            if lb <= 9:
                got = min_fair_x(P, a, b)
                if got and got[0] < min_x:
                    min_x = got[0]
                    witness = (got[1], a, b, got[0])
    return covering, dict(hist), min_x, witness


def tariff(q, r, x):
    return 38 * q + 2 * r + 2 * x


def main():
    with Pool() as pool:
        results = pool.map(worker, list(combinations(range(1, 32), 4)), chunksize=32)

    covering = 0
    hist = Counter()
    min_x = INF
    witness = None
    for c, h, mx, w in results:
        covering += c
        hist.update(h)
        if mx < min_x:
            min_x = mx
            witness = w

    if covering != EXPECTED_COVERING:
        fail(f"covering {covering} != {EXPECTED_COVERING}")
    if dict(hist) != EXPECTED_HIST:
        fail(f"histogram {dict(hist)}")
    if min(hist) != 84:
        fail(f"min R {min(hist)}")
    if min_x != EXPECTED_MIN_X:
        fail(f"min X {min_x}")
    if witness is None:
        fail("missing witness")

    prefix, a, b, x = witness
    r = dual(even_table(prefix[1:] + (a,)), even_table(prefix[1:] + (b,)))
    if r != 84 or x != 9:
        fail(f"witness recompute R={r} X={x}")
    t = tariff(7, r, x)
    if t != EXPECTED_TARIFF:
        fail(f"tariff {t}")
    if t <= 436:
        fail("undercuts endpoint")

    # Cross-check pinned certificate without importing model.
    cert = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    claim = cert["claim"]
    if claim["covering_pairs"] != covering:
        fail("cert covering")
    if claim["min_R"] != 84 or claim["min_fair_X_at_R84"] != 9:
        fail("cert floors")
    if claim["tariff_floor"] != t:
        fail("cert tariff")
    if claim.get("undercuts_436_after_complete_bill") is not False:
        fail("cert undercut flag")

    print(
        "PASS_INDEPENDENT_TRANSFER_COUPLED_7Q "
        f"covering={covering} min_R=84 min_fair_X={min_x} tariff_floor={t} "
        f"champion_prefix={list(prefix)} tips=[{a}, {b}] "
        "answers_transfer_coupled_511 no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
