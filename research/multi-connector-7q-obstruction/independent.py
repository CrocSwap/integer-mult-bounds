#!/usr/bin/env python3
"""Independent multi-connector / shadow census at Q=7.

Does not import model.py or verify.py. Prepared by Wentao Li with substantial
AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"
CHAMPION = (0, 1, 2, 6, 12, 24, 16)
BASIS = (1, 2, 4, 8, 16)


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def dual_and_triangle(even):
    """One pass: (Σ_m min_a (e[a]+e[a⊕m]), triangle_holds). Not a Σ e copy."""
    total = 0
    triangle = True
    for m in range(1, 32):
        best = 99
        em = even[m]
        for a in range(32):
            c0 = even[a]
            c1 = even[a ^ m]
            if c0 < 99 and c1 < 99:
                cost = c0 + c1
                if cost < best:
                    best = cost
                if em > cost:
                    triangle = False
        if best >= 99:
            return None, False
        total += best
    return total, triangle


def bundle(slots):
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
    dual, tri = dual_and_triangle(even)
    if dual is None:
        return None
    return even_r, dirty_rs, clean_rs, dual, tri


def tariff(q, r, x):
    return (28 * q + r) + (9 * q) + x + (q + r + x)


def distinct6():
    he, hd, hdu, hc = Counter(), Counter(), Counter(), Counter()
    covering = 0
    dirty_eq = 0
    dual_eq = 0
    triangle_ok = 0
    for nonzero in combinations(range(1, 32), 6):
        got = bundle((0,) + nonzero)
        if got is None:
            continue
        e, ds, cs, du, tri = got
        covering += 1
        he[e] += 1
        dmin = min(ds)
        cmin = min(cs)
        hd[dmin] += 1
        hc[cmin] += 1
        hdu[du] += 1
        if dmin == e and all(v == e for v in ds):
            dirty_eq += 1
        if du == e:
            dual_eq += 1
        if tri:
            triangle_ok += 1
    if covering != 583296:
        fail(f"covering {covering}")
    if dict(he) != {82: 97216, 88: 486080}:
        fail(f"even hist {dict(he)}")
    if dict(hd) != {82: 97216, 88: 486080}:
        fail(f"dirty hist {dict(hd)}")
    if dict(hdu) != {82: 97216, 88: 486080}:
        fail(f"dual hist {dict(hdu)}")
    if dict(hc) != {71: 97216, 80: 486080}:
        fail(f"clean hist {dict(hc)}")
    if dirty_eq != covering:
        fail(f"match dirty={dirty_eq}")
    if dual_eq != covering:
        fail(f"match dual={dual_eq}")
    if triangle_ok != covering:
        fail(f"triangle={triangle_ok}")
    return covering


def one_repeat(kind):
    hist = Counter()
    covering = 0

    def take(slots):
        nonlocal covering
        if slots[-1] == 0 or any(slots[i] == slots[i + 1] for i in range(6)):
            return
        got = bundle(tuple(slots))
        if got is None:
            return
        e, ds, cs, du, _tri = got
        if kind == "even":
            total = e
        elif kind == "dirty":
            total = min(ds)
        elif kind == "clean":
            total = min(cs)
        else:
            fail("kind")
        covering += 1
        hist[total] += 1

    for j in range(1, 6):
        rest = [i for i in range(1, 7) if i != j]
        for perm in permutations(BASIS):
            slots = [0] * 7
            slots[j] = 0
            for pos, val in zip(rest, perm):
                slots[pos] = val
            take(slots)
    for dbl in range(5):
        others = [BASIS[i] for i in range(5) if i != dbl]
        for p1, p2 in combinations(range(1, 7), 2):
            rest = [i for i in range(1, 7) if i not in (p1, p2)]
            for perm in permutations(others):
                slots = [0] * 7
                slots[p1] = slots[p2] = BASIS[dbl]
                for pos, val in zip(rest, perm):
                    slots[pos] = val
                take(slots)
    return covering, dict(hist)


def main():
    cert = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    covering = distinct6()
    for kind, expect in (("even", {96: 1680}), ("dirty", {96: 1680}), ("clean", {88: 1680})):
        cov, hist = one_repeat(kind)
        if cov != 1680 or hist != expect:
            fail(f"repeat {kind} {cov} {hist}")

    got = bundle(CHAMPION)
    if got is None:
        fail("champion uncovered")
    e, ds, cs, du, tri = got
    if e != 82 or min(ds) != 82 or du != 82 or min(cs) != 71 or not tri:
        fail(f"champion scores {got}")
    if tariff(7, 82, 6) != 442 or tariff(7, 71, 6) != 420:
        fail("tariff")
    if not (
        cert["claim"]["legal_multi_connector_min_R"] == 82
        and cert["claim"]["clean_shadow_counterfactual_min_R"] == 71
        and cert["claim"]["undercuts_436_after_complete_dirty_bill"] is False
    ):
        fail("certificate claim drift")

    print(
        "PASS_INDEPENDENT_MULTI_CONNECTOR_7Q",
        f"covering={covering}",
        "legal_min=82",
        "clean_counterfactual_min=71",
        "tariff_legal=442",
        "tariff_clean=420",
        "answers_cr7q_oq1",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
