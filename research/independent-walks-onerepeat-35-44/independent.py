#!/usr/bin/env python3
"""Independent one-repeat (3,5)/(4,4) dual census at Q=8.

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
INF = 99


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def even_table(slots):
    n = len(slots)
    even = [INF] * 32
    even[0] = 0
    for bits in range(1, 1 << n):
        size = bits.bit_count()
        if size % 2:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        if size < even[value]:
            even[value] = size
    return even


def dual_R(e0, e1):
    reach0 = [(a, e0[a]) for a in range(32) if e0[a] < INF]
    total = 0
    for m in range(1, 32):
        best = INF
        for a, c0 in reach0:
            c1 = e1[a ^ m]
            if c1 < INF:
                best = min(best, c0 + c1)
        if best >= INF:
            return None
        total += best
    return total


def path_X(slots):
    closed = slots + (0,)
    total = 0
    for a, b in zip(closed, closed[1:]):
        delta = a ^ b
        if delta == 0:
            return None
        total += 2 * (delta.bit_count() - 1)
    return total


def tariff(q, r, x):
    return 38 * q + 2 * r + 2 * x


_TABLES = None


def _init(tables):
    global _TABLES
    _TABLES = tables


def _work(i):
    e0 = _TABLES[0][i]
    hist = Counter()
    covering = 0
    for e1 in _TABLES[1]:
        r = dual_R(e0, e1)
        if r is None:
            continue
        covering += 1
        hist[r] += 1
    return covering, hist


def pair_census(tables_a, tables_b):
    n = max(1, os.cpu_count() or 2)
    with Pool(n, initializer=_init, initargs=((tables_a, tables_b),)) as pool:
        parts = pool.map(_work, range(len(tables_a)))
    covering = 0
    hist = Counter()
    for c, h in parts:
        covering += c
        hist.update(h)
    return covering, hist


def main():
    cert = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    claim = cert["claim"]

    if path_X((0, 1, 1)) is not None:
        fail("length-3 one-repeat should be invalid")

    tables3 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 2)]
    tables5 = []
    for d in range(1, 32):
        for o1, o2 in combinations([x for x in range(1, 32) if x != d], 2):
            tables5.append(even_table((0, d, d, o1, o2)))
    c35, h35 = pair_census(tables3, tables5)
    if c35 != claim["one_repeat_35_covering"]:
        fail(f"35 covering {c35}")
    if min(h35) != 112 or set(h35) != {112} or h35[112] != c35:
        fail(f"35 hist {dict(h35)}")

    tables_or = []
    for d in range(1, 32):
        for o in range(1, 32):
            if o == d:
                continue
            if path_X((0, d, o, d)) is None:
                fail("expected L4 one-repeat form")
            tables_or.append(even_table((0, d, d, o)))
    tables4 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 3)]
    c44, h44 = pair_census(tables_or, tables4)
    if c44 != claim["one_repeat_44_covering"]:
        fail(f"44 covering {c44}")
    if min(h44) != 112 or set(h44) != {112} or h44[112] != c44:
        fail(f"44 hist {dict(h44)}")

    both, both_h = pair_census(tables_or, tables_or)
    if both != 0 or both_h:
        fail(f"both-or covering {both}")

    r35 = dual_R(even_table((0, 1, 2)), even_table((0, 8, 4, 16, 4)))
    r44 = dual_R(even_table((0, 1, 2, 1)), even_table((0, 4, 8, 16)))
    if r35 != 112 or r44 != 112:
        fail(f"champ R {r35} {r44}")
    x35 = path_X((0, 1, 2)) + path_X((0, 8, 4, 16, 4))
    x44 = path_X((0, 1, 2, 1)) + path_X((0, 4, 8, 16))
    if x35 != 8 or x44 != 8:
        fail(f"champ X {x35} {x44}")

    floor = tariff(8, 112, 0)
    if floor != 528 or floor <= 436:
        fail(f"tariff floor {floor}")
    if claim["one_repeat_35_min_R"] <= claim["distinct_35_min_R"]:
        fail("should not beat distinct 98")
    if claim["one_repeat_44_min_R"] <= claim["distinct_44_min_R"]:
        fail("should not beat distinct 100")

    print(
        "PASS_INDEPENDENT_WALKS_ONEREPEAT_35_44",
        f"covering_35={c35}",
        f"covering_44={c44}",
        "one_repeat_35_min_R=112",
        "one_repeat_44_min_R=112",
        f"tariff_floor={floor}",
        "distinct_35_min_R=98",
        "distinct_44_min_R=100",
        "answers_independent_walks_onerepeat_8q_oq1",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
