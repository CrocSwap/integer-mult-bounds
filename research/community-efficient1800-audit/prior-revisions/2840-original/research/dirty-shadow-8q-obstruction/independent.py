#!/usr/bin/env python3
"""Independent dirty-shadow / clean-shadow census at Q=8.

Does not import model.py or verify.py. Prepared by Wentao Li with substantial
AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
import os
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"
CHAMPION = (0, 1, 2, 3, 4, 8, 16, 29)
INF = 99


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def gf2_rank(vals):
    basis = []
    for v in vals:
        x = v
        for b in basis:
            x = min(x, x ^ b)
        if x:
            basis.append(x)
            basis.sort(reverse=True)
    return len(basis)


def bit_bundle(slots):
    """Bit-enumeration even / dirty-by-k / clean-by-k totals."""
    n = len(slots)
    even = [99] * 32
    even[0] = 0
    dirty = [[99] * 32 for _ in range(n)]
    clean = [[99] * 32 for _ in range(n)]
    for bits in range(1 << n):
        size = bits.bit_count()
        if size == 0:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        if size % 2 == 0:
            if size < even[value]:
                even[value] = size
            for k in range(n):
                if size < dirty[k][value]:
                    dirty[k][value] = size
                if size < clean[k][value]:
                    clean[k][value] = size
                cost = size + 1
                v = value ^ slots[k]
                if cost < clean[k][v]:
                    clean[k][v] = cost
        else:
            for k in range(n):
                cost = size + 1
                v = value ^ slots[k]
                if cost < dirty[k][v]:
                    dirty[k][v] = cost
    for k in range(n):
        sigma = slots[k]
        if sigma != 0 and 1 < clean[k][sigma]:
            clean[k][sigma] = 1
    if any(even[m] >= 99 for m in range(1, 32)):
        return None
    even_r = sum(even[1:])
    dirty_rs = [sum(dirty[k][1:]) for k in range(n)]
    clean_rs = [sum(clean[k][1:]) for k in range(n)]
    return even_r, dirty_rs, clean_rs


def dp_bundle(slots):
    """Separate even/odd DP; dirty equals even under collapse; clean min-over-k."""
    be = [INF] * 32
    bo = [INF] * 32
    be[0] = 0
    for v in slots:
        ne = be[:]
        no = bo[:]
        for m in range(32):
            e = be[m]
            if e < INF:
                nm = m ^ v
                c = e + 1
                if c < no[nm]:
                    no[nm] = c
            o = bo[m]
            if o < INF:
                nm = m ^ v
                c = o + 1
                if c < ne[nm]:
                    ne[nm] = c
        be, bo = ne, no
    if any(be[m] >= INF for m in range(1, 32)):
        return None
    even_r = sum(be[1:])
    dirty_rs = []
    clean_rs = []
    for sigma in slots:
        dirty_ok = True
        cr = 0
        for m in range(1, 32):
            e = be[m]
            alt = bo[m ^ sigma]
            if alt < INF and alt + 1 < e:
                dirty_ok = False
            c = e
            e2 = be[m ^ sigma]
            if e2 < INF and e2 + 1 < c:
                c = e2 + 1
            if sigma == m and c > 1:
                c = 1
            cr += c
        dirty_rs.append(even_r if dirty_ok else -1)
        clean_rs.append(cr)
    if any(v < 0 for v in dirty_rs):
        # Collapse failed: fall back to explicit dirty totals.
        dirty_rs = []
        for sigma in slots:
            dr = 0
            for m in range(1, 32):
                d = be[m]
                if bo[m ^ sigma] < INF:
                    d = min(d, bo[m ^ sigma] + 1)
                dr += d
            dirty_rs.append(dr)
    return even_r, dirty_rs, clean_rs


def tariff(q, r, x):
    return (28 * q + r) + (9 * q) + x + (q + r + x)


def _d7_worker(combos):
    he, hd, hc = Counter(), Counter(), Counter()
    covering = 0
    dirty_eq = 0
    for combo in combos:
        if gf2_rank(combo) < 5:
            continue
        got = dp_bundle((0,) + combo)
        if got is None:
            continue
        e, ds, cs = got
        covering += 1
        dmin = min(ds)
        cmin = min(cs)
        he[e] += 1
        hd[dmin] += 1
        hc[cmin] += 1
        if dmin == e and all(v == e for v in ds):
            dirty_eq += 1
    return covering, dirty_eq, he, hd, hc


def distinct7():
    combos = list(combinations(range(1, 32), 7))
    n = os.cpu_count() or 4
    chunk = (len(combos) + n - 1) // n
    chunks = [combos[i * chunk : (i + 1) * chunk] for i in range(n)]
    with Pool(n) as pool:
        parts = pool.map(_d7_worker, chunks)
    covering = dirty_eq = 0
    he, hd, hc = Counter(), Counter(), Counter()
    for c, de, a, d, cl in parts:
        covering += c
        dirty_eq += de
        he.update(a)
        hd.update(d)
        hc.update(cl)
    if covering != 2430400:
        fail(f"covering {covering}")
    if dict(he) != {74: 416640, 80: 1180480, 84: 833280}:
        fail(f"even hist {dict(he)}")
    if dict(hd) != {74: 416640, 80: 1180480, 84: 833280}:
        fail(f"dirty hist {dict(hd)}")
    if dict(hc) != {67: 416640, 70: 1180480, 76: 833280}:
        fail(f"clean hist {dict(hc)}")
    if dirty_eq != covering:
        fail(f"match dirty={dirty_eq}")
    return covering


def _dup_worker(items):
    he, hd, hc = Counter(), Counter(), Counter()
    covering = 0
    dirty_eq = 0
    for six, dup in items:
        if gf2_rank(six) < 5:
            continue
        labels = (0,) + six
        slots = tuple(sorted(labels + (dup,)))
        got = dp_bundle(slots)
        if got is None:
            continue
        e, ds, cs = got
        covering += 1
        dmin = min(ds)
        cmin = min(cs)
        he[e] += 1
        hd[dmin] += 1
        hc[cmin] += 1
        if dmin == e and all(v == e for v in ds):
            dirty_eq += 1
    return covering, dirty_eq, he, hd, hc


def one_dup():
    items = []
    for six in combinations(range(1, 32), 6):
        labels = (0,) + six
        for dup in labels:
            items.append((six, dup))
    n = os.cpu_count() or 4
    chunk = (len(items) + n - 1) // n
    chunks = [items[i * chunk : (i + 1) * chunk] for i in range(n)]
    with Pool(n) as pool:
        parts = pool.map(_dup_worker, chunks)
    covering = dirty_eq = 0
    he, hd, hc = Counter(), Counter(), Counter()
    for c, de, a, d, cl in parts:
        covering += c
        dirty_eq += de
        he.update(a)
        hd.update(d)
        hc.update(cl)
    if covering != 4083072:
        fail(f"one-dup covering {covering}")
    if dict(he) != {82: 680512, 88: 3402560}:
        fail(f"one-dup even {dict(he)}")
    if dict(hd) != {82: 680512, 88: 3402560}:
        fail(f"one-dup dirty {dict(hd)}")
    if dict(hc) != {71: 680512, 80: 3402560}:
        fail(f"one-dup clean {dict(hc)}")
    if dirty_eq != covering:
        fail(f"one-dup match {dirty_eq}")
    return covering


def main():
    cert = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    covering = distinct7()
    one_dup_covering = one_dup()

    bit = bit_bundle(CHAMPION)
    dp = dp_bundle(CHAMPION)
    if bit is None or dp is None or bit != dp:
        fail(f"champion bit/dp {bit} {dp}")
    e, ds, cs = bit
    if e != 74 or min(ds) != 74 or min(cs) != 67 or any(v != 74 for v in ds):
        fail(f"champion scores {bit}")
    if tariff(8, 74, 0) != 452 or tariff(8, 67, 0) != 438:
        fail("tariff")
    if not (
        cert["claim"]["dirty_shadow_min_R"] == 74
        and cert["claim"]["clean_shadow_counterfactual_min_R"] == 67
        and cert["claim"]["undercuts_436_after_complete_dirty_bill"] is False
        and cert["claim"]["undercuts_436_if_clean_shadow_free"] is False
        and cert["claim"]["answers_mc7q_oq2"] is True
    ):
        fail("certificate claim drift")

    print(
        "PASS_INDEPENDENT_DIRTY_SHADOW_8Q",
        f"covering={covering}",
        f"one_dup={one_dup_covering}",
        "dirty_min=74",
        "clean_counterfactual_min=67",
        "tariff_legal=452",
        "tariff_clean=438",
        "answers_mc7q_oq2",
        "matches_2677_even_floor",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
